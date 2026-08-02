from __future__ import annotations

import argparse
import sys
import unittest
from collections.abc import Sequence


INCOMPLETE_VERIFICATION_EXIT_CODE = 125


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ddh-unittest-runner")
    parser.add_argument("start_directory")
    parser.add_argument("--pattern", default="test*.py")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    suite = unittest.defaultTestLoader.discover(
        arguments.start_directory,
        pattern=arguments.pattern,
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.skipped:
        return INCOMPLETE_VERIFICATION_EXIT_CODE
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
