"""Factory paths and environment (single unit — import from worker_factory/)."""
from __future__ import annotations

import os
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parent
TESTS_DIR = FACTORY_ROOT / "tests"
PLAYWRIGHT_DIR = TESTS_DIR / "playwright"


def _load_dotenv() -> None:
    env_file = FACTORY_ROOT / ".env"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


_load_dotenv()

app_domain = os.getenv("APP_DOMAIN", "http://localhost:3000").rstrip("/")
api_domain = os.getenv("API_DOMAIN", "").rstrip("/")
resolved_api_domain = (api_domain or app_domain).rstrip("/")
loki_s3_bucket = os.getenv("LOKI_S3_BUCKET", "")
aws_region = os.getenv("AWS_REGION", "us-west-1")
errors_prefix = os.getenv("FACTORY_ERRORS_PREFIX", "factory/errors").strip("/")
git_commit = os.getenv("GIT_COMMIT") or os.getenv("COMMIT_SHA", "local")
ci_run_url = os.getenv("CI_RUN_URL", "")
