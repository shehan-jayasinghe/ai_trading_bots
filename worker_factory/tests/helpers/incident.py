"""Build failure bundles and upload to LOKI_S3_BUCKET under factory/errors/<component>/."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)

COMPONENTS = frozenset({"backend", "frontend", "workers"})


def new_incident_id() -> str:
    return str(uuid4())


def build_bundle(
    *,
    incident_id: str,
    scenario_id: str,
    component: str,
    error_summary: str,
    commit_sha: str = "local",
    ci_run_url: str = "",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if component not in COMPONENTS:
        raise ValueError(f"component must be one of {COMPONENTS}")
    return {
        "incident_id": incident_id,
        "scenario_id": scenario_id,
        "component": component,
        "error_summary": error_summary,
        "commit_sha": commit_sha,
        "ci_run_url": ci_run_url,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        **(extra or {}),
    }


def s3_prefix_for(component: str, incident_id: str, errors_prefix: str) -> str:
    now = datetime.now(timezone.utc)
    return (
        f"{errors_prefix}/{component}/"
        f"{now.year:04d}/{now.month:02d}/{now.day:02d}/{incident_id}/"
    )


def save_local_incident(
    base_dir: Path,
    *,
    incident_id: str,
    files: dict[str, str | bytes | dict[str, Any]],
) -> Path:
    root = base_dir / incident_id
    root.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        path = root / name
        if isinstance(content, dict):
            path.write_text(json.dumps(content, indent=2, default=str), encoding="utf-8")
        elif isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
    return root


def upload_incident(
    *,
    bucket: str,
    region: str,
    prefix: str,
    files: dict[str, str | bytes | dict[str, Any]],
) -> str | None:
    if not bucket:
        return None
    try:
        import boto3
    except ImportError:
        logger.warning("boto3 not installed; skip S3 upload")
        return None

    client = boto3.client("s3", region_name=region)
    for name, content in files.items():
        key = f"{prefix}{name}"
        if isinstance(content, dict):
            body = json.dumps(content, default=str).encode("utf-8")
            content_type = "application/json"
        elif isinstance(content, bytes):
            body = content
            content_type = "application/octet-stream"
        else:
            body = content.encode("utf-8")
            content_type = "text/plain; charset=utf-8"
        client.put_object(Bucket=bucket, Key=key, Body=body, ContentType=content_type)
    return f"s3://{bucket}/{prefix}"


def record_failure(
    *,
    component: str,
    scenario_id: str,
    error_summary: str,
    bucket: str | None = None,
    region: str | None = None,
    errors_prefix: str | None = None,
    commit_sha: str | None = None,
    ci_run_url: str | None = None,
    api_response: dict[str, Any] | None = None,
    ui_log: str | None = None,
    local_dir: Path | None = None,
) -> str:
    from config import settings

    bucket = bucket if bucket is not None else settings.loki_s3_bucket
    region = region if region is not None else settings.aws_region
    errors_prefix = errors_prefix if errors_prefix is not None else settings.errors_prefix
    commit_sha = commit_sha if commit_sha is not None else settings.commit_sha
    ci_run_url = ci_run_url if ci_run_url is not None else settings.ci_run_url
    local_dir = local_dir or settings.LOCAL_INCIDENTS_DIR

    incident_id = new_incident_id()
    bundle = build_bundle(
        incident_id=incident_id,
        scenario_id=scenario_id,
        component=component,
        error_summary=error_summary,
        commit_sha=commit_sha,
        ci_run_url=ci_run_url,
    )
    prefix = s3_prefix_for(component, incident_id, errors_prefix)
    files: dict[str, str | bytes | dict[str, Any]] = {"bundle.json": bundle}
    if api_response is not None:
        files["api_response.json"] = api_response
    if ui_log:
        files["ui_console.log"] = ui_log

    local_path = save_local_incident(local_dir, incident_id=incident_id, files=files)
    logger.error("incident saved locally: %s", local_path)

    uri = upload_incident(bucket=bucket, region=region, prefix=prefix, files=files)
    if uri:
        logger.error("incident uploaded: %s", uri)
        return uri
    return str(local_path)
