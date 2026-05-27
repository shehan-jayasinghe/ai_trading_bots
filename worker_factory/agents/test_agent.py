"""
Phase 0 test agent — single Python unit.

Backend (4 API) then frontend (3 UI). Test implementations are TODO.
"""
from __future__ import annotations

import config


def _print_plan() -> None:
    bucket = config.loki_s3_bucket or "(not set)"
    print("=== Worker factory — test agent ===")
    print(f"APP_DOMAIN={config.app_domain}")
    print(f"API_DOMAIN={config.resolved_api_domain}")
    print(f"LOKI_S3_BUCKET={bucket}")
    print("Backend: TODO — 4 API tests (pytest)")
    print("Frontend: TODO — 3 UI tests (Playwright)")
    print()


def run_backend() -> int:
    # TODO: pytest tests/api/ (same interpreter: sys.executable -m pytest)
    print("--- Backend: skipped (TODO) ---\n")
    return 0


def run_frontend() -> int:
    # TODO: npm test in tests/playwright
    print("--- Frontend: skipped (TODO) ---\n")
    return 0


def run() -> int:
    _print_plan()
    code = run_backend()
    if code != 0:
        return code
    code = run_frontend()
    if code == 0:
        print("=== Result: PASS (stubs — add tests next) ===")
    else:
        print("=== Result: FAIL ===")
    return code
