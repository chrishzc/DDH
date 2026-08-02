from __future__ import annotations

import ctypes
import subprocess
from ctypes import wintypes
from typing import Any


class BasicLimitInformation(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),
        ("PerJobUserTimeLimit", ctypes.c_int64),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class IoCounters(ctypes.Structure):
    _fields_ = [
        (name, ctypes.c_uint64)
        for name in (
            "ReadOperationCount",
            "WriteOperationCount",
            "OtherOperationCount",
            "ReadTransferCount",
            "WriteTransferCount",
            "OtherTransferCount",
        )
    ]


class ExtendedLimitInformation(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", BasicLimitInformation),
        ("IoInfo", IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


KILL_ON_JOB_CLOSE = 0x00002000
EXTENDED_LIMIT_INFORMATION_CLASS = 9


def create_kill_job() -> int | None:
    kernel32 = _kernel32()
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        return None
    if not _configure_kill_on_close(kernel32, job):
        kernel32.CloseHandle(job)
        return None
    return int(job)


def _configure_kill_on_close(kernel32: Any, job: int) -> bool:
    information = ExtendedLimitInformation()
    information.BasicLimitInformation.LimitFlags = KILL_ON_JOB_CLOSE
    return bool(
        kernel32.SetInformationJobObject(
            job,
            EXTENDED_LIMIT_INFORMATION_CLASS,
            ctypes.byref(information),
            ctypes.sizeof(information),
        )
    )


def assign_process(job: int, process: subprocess.Popen[bytes]) -> bool:
    kernel32 = _kernel32()
    kernel32.AssignProcessToJobObject.argtypes = (
        wintypes.HANDLE,
        wintypes.HANDLE,
    )
    process_handle = wintypes.HANDLE(int(process._handle))
    return bool(kernel32.AssignProcessToJobObject(job, process_handle))


def close_handle(handle: int) -> None:
    kernel32 = _kernel32()
    kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel32.CloseHandle(wintypes.HANDLE(handle))


def _kernel32() -> Any:
    return ctypes.WinDLL("kernel32", use_last_error=True)
