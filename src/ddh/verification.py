from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from ddh.contracts import CandidateReference, ContractError
from ddh.test_auditor import VerificationAsset


@dataclass(frozen=True)
class ExecutionPlan:
    plan_id: str
    candidate: CandidateReference
    asset_digest: str
    adapter_id: str
    argv: tuple[str, ...]
    cwd: Path
    timeout_seconds: float
    expected_exit_codes: tuple[int, ...] = (0,)


@dataclass(frozen=True)
class VerificationResult:
    plan_id: str
    candidate: CandidateReference
    asset_digest: str
    terminal_state: str
    acceptance_outcome: str
    verification_completeness: str
    reason_code: str
    retryable: bool
    exit_code: int | None
    duration_milliseconds: int
    stdout: str
    stderr: str
    output_truncated: bool


class PytestAdapter:
    adapter_id = "pytest"

    def build_plan(
        self,
        asset: VerificationAsset,
        cwd: Path,
        timeout_seconds: float,
    ) -> ExecutionPlan:
        argv = (sys.executable, "-m", "pytest", *asset.command)
        return _plan(asset, self.adapter_id, argv, cwd, timeout_seconds)


class FixedCommandAdapter:
    adapter_id = "fixed_command"

    def build_plan(
        self,
        asset: VerificationAsset,
        cwd: Path,
        timeout_seconds: float,
    ) -> ExecutionPlan:
        _reject_generic_shell(asset.command)
        return _plan(asset, self.adapter_id, asset.command, cwd, timeout_seconds)


GENERIC_SHELLS = {
    "bash",
    "cmd",
    "cmd.exe",
    "powershell",
    "powershell.exe",
    "pwsh",
    "sh",
    "zsh",
}
INCOMPLETE_VERIFICATION_EXIT_CODE = 125


def _reject_generic_shell(command: tuple[str, ...]) -> None:
    if not command:
        raise ContractError("fixed_command_empty")
    executable = Path(command[0]).name.lower()
    if executable in GENERIC_SHELLS:
        raise ContractError("generic_shell_executor_prohibited")


def _plan(
    asset: VerificationAsset,
    adapter_id: str,
    argv: tuple[str, ...],
    cwd: Path,
    timeout_seconds: float,
) -> ExecutionPlan:
    identity = f"{asset.digest}:{adapter_id}"
    return ExecutionPlan(
        identity,
        asset.candidate,
        asset.digest,
        adapter_id,
        argv,
        cwd,
        timeout_seconds,
    )


def adaptive_timeout_seconds(
    declared_seconds: float | None,
    history_p95_seconds: float | None,
    reliable_estimate_seconds: float | None,
) -> float:
    basis = history_p95_seconds or declared_seconds or reliable_estimate_seconds
    return 600.0 if basis is None else max(1.0, basis * 2.0 + 30.0)


class VerificationRunner:
    def __init__(
        self,
        stdout_limit: int = 65_536,
        stderr_limit: int = 65_536,
        drain_grace_seconds: float = 30.0,
    ) -> None:
        self._stdout_limit = stdout_limit
        self._stderr_limit = stderr_limit
        self._drain_grace = drain_grace_seconds
        self._windows_jobs: dict[int, int] = {}

    def run(self, plan: ExecutionPlan) -> VerificationResult:
        started = time.monotonic()
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            try:
                process = self._start(plan, stdout, stderr)
            except OSError:
                duration = int(round((time.monotonic() - started) * 1000))
                return self._start_failure(plan, duration)
            timed_out = not self._wait(process, plan.timeout_seconds)
            if timed_out:
                self._terminate_tree(process)
                self._wait(process, self._drain_grace)
            self._close_windows_job(process.pid)
            output = self._read_outputs(stdout, stderr)
        duration = time.monotonic() - started
        return self._result(plan, process.returncode, timed_out, duration, output)

    def _start_failure(
        self,
        plan: ExecutionPlan,
        duration_milliseconds: int,
    ) -> VerificationResult:
        return VerificationResult(
            plan.plan_id,
            plan.candidate,
            plan.asset_digest,
            "failed",
            "undetermined",
            "incomplete",
            "runner_start_failed",
            True,
            None,
            duration_milliseconds,
            "",
            "",
            False,
        )

    def _start(
        self,
        plan: ExecutionPlan,
        stdout: object,
        stderr: object,
    ) -> subprocess.Popen[bytes]:
        options: dict[str, object] = {}
        if os.name == "nt":
            options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            options["start_new_session"] = True
        process = subprocess.Popen(
            plan.argv,
            cwd=plan.cwd,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            shell=False,
            **options,
        )
        self._assign_windows_kill_job(process)
        return process

    def _assign_windows_kill_job(self, process: subprocess.Popen[bytes]) -> None:
        if os.name != "nt":
            return
        job = _create_windows_kill_job()
        if job is None:
            return
        if not _assign_process_to_job(job, process):
            _close_windows_handle(job)
            return
        self._windows_jobs[process.pid] = job

    def _close_windows_job(self, process_id: int) -> None:
        job = self._windows_jobs.pop(process_id, None)
        if job is not None:
            _close_windows_handle(job)

    def _wait(self, process: subprocess.Popen[bytes], timeout: float) -> bool:
        try:
            process.wait(timeout=timeout)
            return True
        except subprocess.TimeoutExpired:
            return False

    def _terminate_tree(self, process: subprocess.Popen[bytes]) -> None:
        if process.poll() is not None:
            return
        if os.name == "nt":
            self._terminate_windows_tree(process)
            return
        os.killpg(process.pid, signal.SIGKILL)

    def _terminate_windows_tree(self, process: subprocess.Popen[bytes]) -> None:
        try:
            subprocess.run(
                ("taskkill", "/PID", str(process.pid), "/T", "/F"),
                capture_output=True,
                check=False,
                shell=False,
                timeout=self._drain_grace,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
        if process.poll() is None:
            process.kill()
        self._wait(process, self._drain_grace)

    def _read_outputs(
        self,
        stdout: object,
        stderr: object,
    ) -> tuple[str, str, bool]:
        stdout.seek(0)
        stderr.seek(0)
        stdout_bytes = stdout.read(self._stdout_limit + 1)
        stderr_bytes = stderr.read(self._stderr_limit + 1)
        truncated = (
            len(stdout_bytes) > self._stdout_limit
            or len(stderr_bytes) > self._stderr_limit
        )
        return (
            _decode_bounded(stdout_bytes, self._stdout_limit),
            _decode_bounded(stderr_bytes, self._stderr_limit),
            truncated,
        )

    def _result(
        self,
        plan: ExecutionPlan,
        exit_code: int | None,
        timed_out: bool,
        duration: float,
        output: tuple[str, str, bool],
    ) -> VerificationResult:
        if timed_out:
            outcome = ("failed", "undetermined", "incomplete", "verification_timeout", True)
        else:
            outcome = self._classify_exit(plan, exit_code)
        return VerificationResult(
            plan.plan_id,
            plan.candidate,
            plan.asset_digest,
            *outcome,
            exit_code,
            int(round(duration * 1000)),
            *output,
        )

    def _classify_exit(
        self,
        plan: ExecutionPlan,
        exit_code: int | None,
    ) -> tuple[str, str, str, str, bool]:
        if exit_code in plan.expected_exit_codes:
            return ("succeeded", "passed", "complete", "verification_passed", False)
        if exit_code == INCOMPLETE_VERIFICATION_EXIT_CODE:
            return (
                "failed",
                "undetermined",
                "incomplete",
                "required_tests_skipped",
                False,
            )
        if plan.adapter_id == "pytest":
            return _classify_pytest_exit(exit_code)
        return ("failed", "failed", "complete", "product_verification_failed", False)


def _classify_pytest_exit(
    exit_code: int | None,
) -> tuple[str, str, str, str, bool]:
    outcomes = {
        1: ("failed", "failed", "complete", "product_verification_failed", False),
        2: ("failed", "undetermined", "incomplete", "verification_interrupted", True),
        3: ("failed", "undetermined", "incomplete", "runner_internal_error", True),
        4: ("failed", "undetermined", "incomplete", "verification_plan_invalid", False),
        5: ("failed", "undetermined", "incomplete", "required_tests_not_collected", False),
    }
    return outcomes.get(
        exit_code,
        ("failed", "undetermined", "incomplete", "verification_exit_unknown", False),
    )


def _decode_bounded(data: bytes, byte_limit: int) -> str:
    return data[:byte_limit].decode("utf-8", errors="ignore")


def _create_windows_kill_job() -> int | None:
    if os.name != "nt":
        return None
    from ddh.windows_process import create_kill_job

    return create_kill_job()


def _assign_process_to_job(
    job: int,
    process: subprocess.Popen[bytes],
) -> bool:
    from ddh.windows_process import assign_process

    return assign_process(job, process)


def _close_windows_handle(handle: int) -> None:
    from ddh.windows_process import close_handle

    close_handle(handle)
