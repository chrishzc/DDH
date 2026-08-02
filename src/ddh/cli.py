from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from ddh.confirmation import (
    authority_for_document,
    create_confirmation,
    expected_confirmation_phrase,
    publish_confirmation,
)
from ddh.contracts import parse_strict_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ddh")
    commands = parser.add_subparsers(dest="command", required=True)
    digest = commands.add_parser("specification-digest")
    digest.add_argument("specification", type=Path)
    confirm = commands.add_parser("confirm")
    confirm.add_argument("specification", type=Path)
    confirm.add_argument("--record", type=Path, required=True)
    return parser


def load_document(path: Path) -> dict[str, object]:
    value = parse_strict_json(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("specification_root_must_be_object")
    return value


def run_digest(path: Path) -> int:
    authority = authority_for_document(load_document(path))
    print(json.dumps(authority.__dict__, ensure_ascii=False, indent=2))
    return 0


def run_confirm(path: Path, record: Path) -> int:
    if not sys.stdin.isatty():
        raise RuntimeError("interactive_human_terminal_required")
    document = load_document(path)
    authority = authority_for_document(document)
    expected = expected_confirmation_phrase(authority)
    print(f"Type exactly: {expected}")
    confirmation = create_confirmation(document, input("> "), "local_cli")
    publish_confirmation(record, confirmation)
    print(f"confirmed {authority.authority_id}@{authority.version}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "specification-digest":
        return run_digest(arguments.specification)
    if arguments.command == "confirm":
        return run_confirm(arguments.specification, arguments.record)
    raise AssertionError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
