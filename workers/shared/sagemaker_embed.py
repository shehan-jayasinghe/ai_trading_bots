"""SageMaker serverless embedding endpoint (Hugging Face feature-extraction)."""
from __future__ import annotations

import json
import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from shared.settings import settings

logger = logging.getLogger(__name__)


def _parse_embedding_body(body: bytes) -> list[float]:
    data = json.loads(body.decode("utf-8"))
    if isinstance(data, list):
        if data and isinstance(data[0], (int, float)):
            return [float(x) for x in data]
        if data and isinstance(data[0], list):
            inner = data[0]
            if inner and isinstance(inner[0], (int, float)):
                return [float(x) for x in inner]
            if inner and isinstance(inner[0], list):
                return [float(x) for x in inner[0]]
    if isinstance(data, dict):
        for key in ("embedding", "embeddings", "vector"):
            val = data.get(key)
            if isinstance(val, list) and val:
                if isinstance(val[0], (int, float)):
                    return [float(x) for x in val]
                if isinstance(val[0], list):
                    return [float(x) for x in val[0]]
    raise ValueError(f"Unrecognized embedding response shape: {str(data)[:200]}")


def embed_text_sync(text: str) -> list[float] | None:
    """Encode text to a vector via SageMaker InvokeEndpoint. Returns None if not configured."""
    endpoint = (settings.sagemaker_embedding_endpoint or "").strip()
    if not endpoint or not text.strip():
        return None

    region = (settings.aws_region or settings.bedrock_region or "us-west-1").strip()
    payload = json.dumps({"inputs": text.strip()})

    try:
        client = boto3.client("sagemaker-runtime", region_name=region)
        response = client.invoke_endpoint(
            EndpointName=endpoint,
            ContentType="application/json",
            Accept="application/json",
            Body=payload.encode("utf-8"),
        )
        return _parse_embedding_body(response["Body"].read())
    except (ClientError, BotoCoreError) as exc:
        logger.warning("SageMaker embed failed endpoint=%s: %s", endpoint, exc)
        return None
    except (ValueError, json.JSONDecodeError) as exc:
        logger.warning("SageMaker embed parse error: %s", exc)
        return None
    except Exception:
        logger.exception("SageMaker embed error")
        return None
