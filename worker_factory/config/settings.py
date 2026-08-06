"""Factory root paths and environment (shared by all agents)."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

FACTORY_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = FACTORY_ROOT / "tests"
TEST_VENV_PYTHON = TESTS_DIR / ".venv" / "bin" / "python"
PLAYWRIGHT_DIR = TESTS_DIR / "playwright"
TESTS_CATALOG_PATH = FACTORY_ROOT / "tests_catalog" / "scenarios.yaml"
PROMPTS_PATH = FACTORY_ROOT / "prompts.md"
LOCAL_INCIDENTS_DIR = FACTORY_ROOT / ".factory-incidents"


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
commit_sha = git_commit
ci_run_url = os.getenv("CI_RUN_URL", "")


def merge_into_environ(base: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(base or {})
    extra = os.pathsep.join([str(FACTORY_ROOT), str(TESTS_DIR)])
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [extra, env.get("PYTHONPATH", "")]))
    env.setdefault("APP_DOMAIN", app_domain)
    env.setdefault("API_DOMAIN", resolved_api_domain)
    env.setdefault("LOKI_S3_BUCKET", loki_s3_bucket)
    env.setdefault("AWS_REGION", aws_region)
    env.setdefault("FACTORY_ERRORS_PREFIX", errors_prefix)
    return env


def load_scenarios_catalog() -> dict[str, Any]:
    if not TESTS_CATALOG_PATH.is_file():
        return {"scenarios": []}
    try:
        import yaml
    except ImportError:
        return {"scenarios": []}
    with TESTS_CATALOG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def unique_test_email() -> str:
    import uuid

    return f"factory-{uuid.uuid4().hex[:12]}@example.com"
