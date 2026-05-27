"""Environment helpers for subprocesses (pytest / Playwright) when added."""
from __future__ import annotations

import os

import config


def merge_into_environ(base: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(base or {})
    extra = os.pathsep.join([str(config.FACTORY_ROOT), str(config.TESTS_DIR)])
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [extra, env.get("PYTHONPATH", "")]))
    env.setdefault("APP_DOMAIN", config.app_domain)
    env.setdefault("API_DOMAIN", config.resolved_api_domain)
    env.setdefault("LOKI_S3_BUCKET", config.loki_s3_bucket)
    env.setdefault("AWS_REGION", config.aws_region)
    env.setdefault("FACTORY_ERRORS_PREFIX", config.errors_prefix)
    return env
