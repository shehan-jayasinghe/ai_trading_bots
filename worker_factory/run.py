#!/usr/bin/env python3
"""Worker factory entrypoint — runs as a single unit from this directory."""
from __future__ import annotations

from agents.test_agent import run


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
