"""
Phase 0 test agent — single Python unit.

Backend API (signup + sign-in) then frontend UI (TODO).
"""
from __future__ import annotations

import os
import sys

import config


def _print_plan() -> None:
    bucket = config.loki_s3_bucket or "(not set)"
    print("=== Worker factory — test agent ===")
    print(f"APP_DOMAIN={config.app_domain}")
    print(f"API_DOMAIN={config.resolved_api_domain}")
    print(f"LOKI_S3_BUCKET={bucket}")
    print("Backend: signup + sign-in API tests (pytest)")
    print("Frontend: TODO — Playwright")
    print()


def run_backend() -> int:
    import pytest

    root = str(config.FACTORY_ROOT)
    tests = str(config.TESTS_DIR)
    for path in (root, tests):
        if path not in sys.path:
            sys.path.insert(0, path)
    os.chdir(tests)
    print("--- Backend (pytest): signup + sign-in API ---")
    code = pytest.main(["api/test_auth_api.py", "-v", "--tb=short"])
    if code == 0:
        print("Backend: PASS\n")
    else:
        print("Backend: FAIL (see .factory-incidents/ or S3 factory/errors/backend/)\n")
    return int(code)


def run_frontend() -> int:
    print("--- Frontend: skipped (TODO) ---\n")
    return 0


def run() -> int:
    _print_plan()
    code = run_backend()
    if code != 0:
        return code
    code = run_frontend()
    if code == 0:
        print("=== Result: PASS ===")
    else:
        print("=== Result: FAIL ===")
    return code
