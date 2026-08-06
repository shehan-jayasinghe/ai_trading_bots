"""API tests: Next.js signup + NextAuth credentials sign-in on APP_DOMAIN."""
from __future__ import annotations

import pytest

from helpers.config import unique_test_email
from helpers.incident import record_failure

SIGNUP_PATH = "/api/auth/signup"
CSRF_PATH = "/api/auth/csrf"
CALLBACK_PATH = "/api/auth/callback/credentials"
SESSION_PATH = "/api/auth/session"
TEST_PASSWORD = "TestPass123!"


def _safe_json(resp) -> dict | str:
    try:
        return resp.json()
    except Exception:
        return resp.text[:2000]


def _fail(
    factory_config,
    scenario_id: str,
    summary: str,
    *,
    status: int,
    body: dict | str,
    url: str,
    method: str = "GET",
):
    uri = record_failure(
        component="backend",
        scenario_id=scenario_id,
        error_summary=summary,
        bucket=factory_config.loki_s3_bucket,
        region=factory_config.aws_region,
        errors_prefix=factory_config.errors_prefix,
        commit_sha=factory_config.commit_sha,
        ci_run_url=factory_config.ci_run_url,
        api_response={
            "method": method,
            "url": url,
            "status": status,
            "body": body,
        },
    )
    print(f"incident: {uri}")
    pytest.fail(summary)


def _get_csrf(client, cfg) -> str:
    url = f"{cfg.app_domain}{CSRF_PATH}"
    resp = client.get(url, headers={"Accept": "application/json"})
    if resp.status_code != 200:
        _fail(
            cfg,
            "auth.login.api.csrf",
            f"GET csrf expected 200 got {resp.status_code}",
            status=resp.status_code,
            body=_safe_json(resp),
            url=url,
        )
    data = _safe_json(resp)
    token = data.get("csrfToken") if isinstance(data, dict) else None
    if not token:
        _fail(
            cfg,
            "auth.login.api.csrf-token",
            "csrfToken missing",
            status=resp.status_code,
            body=data,
            url=url,
        )
    return token


def _login_credentials(client, cfg, *, email: str, password: str, csrf_token: str, scenario: str):
    url = f"{cfg.app_domain}{CALLBACK_PATH}"
    resp = client.post(
        url,
        data={
            "csrfToken": csrf_token,
            "email": email,
            "password": password,
            "callbackUrl": f"{cfg.app_domain}/",
            "redirect": "false",
            "json": "true",
        },
        follow_redirects=False,
    )
    if resp.status_code >= 400:
        _fail(
            cfg,
            scenario,
            f"POST login callback expected <400 got {resp.status_code}",
            status=resp.status_code,
            body=_safe_json(resp),
            url=url,
            method="POST",
        )
    return resp


def _session_user(client, cfg) -> dict | None:
    url = f"{cfg.app_domain}{SESSION_PATH}"
    resp = client.get(url, headers={"Accept": "application/json"})
    if resp.status_code != 200:
        _fail(
            cfg,
            "auth.login.api.session",
            f"GET session expected 200 got {resp.status_code}",
            status=resp.status_code,
            body=_safe_json(resp),
            url=url,
        )
    data = _safe_json(resp)
    if not isinstance(data, dict):
        return None
    user = data.get("user")
    return user if isinstance(user, dict) else None


def test_signup_valid(http_client):
    client, cfg = http_client
    url = f"{cfg.app_domain}{SIGNUP_PATH}"
    email = unique_test_email()
    resp = client.post(url, json={"email": email, "password": TEST_PASSWORD})
    if resp.status_code != 201:
        _fail(
            cfg,
            "auth.signup.api.valid",
            f"POST signup expected 201 got {resp.status_code}",
            status=resp.status_code,
            body=_safe_json(resp),
            url=url,
            method="POST",
        )
    data = resp.json()
    assert data.get("ok") is True


def test_signup_validation(http_client):
    client, cfg = http_client
    url = f"{cfg.app_domain}{SIGNUP_PATH}"
    resp = client.post(url, json={"email": "not-an-email", "password": "short"})
    if resp.status_code != 400:
        _fail(
            cfg,
            "auth.signup.api.validation",
            f"POST invalid signup expected 400 got {resp.status_code}",
            status=resp.status_code,
            body=_safe_json(resp),
            url=url,
            method="POST",
        )
    data = resp.json()
    assert data.get("ok") is False
    assert data.get("fieldErrors")


def test_signup_duplicate(http_client):
    client, cfg = http_client
    url = f"{cfg.app_domain}{SIGNUP_PATH}"
    email = unique_test_email()
    payload = {"email": email, "password": TEST_PASSWORD}
    first = client.post(url, json=payload)
    if first.status_code != 201:
        _fail(
            cfg,
            "auth.signup.api.duplicate",
            f"first signup failed: {first.status_code}",
            status=first.status_code,
            body=_safe_json(first),
            url=url,
            method="POST",
        )
    second = client.post(url, json=payload)
    if second.status_code != 409:
        _fail(
            cfg,
            "auth.signup.api.duplicate",
            f"duplicate signup expected 409 got {second.status_code}",
            status=second.status_code,
            body=_safe_json(second),
            url=url,
            method="POST",
        )


def test_signin_valid(http_client):
    client, cfg = http_client
    email = unique_test_email()
    signup_url = f"{cfg.app_domain}{SIGNUP_PATH}"
    signup_resp = client.post(signup_url, json={"email": email, "password": TEST_PASSWORD})
    if signup_resp.status_code != 201:
        _fail(
            cfg,
            "auth.signin.api.prepare-signup",
            f"signup before login failed: {signup_resp.status_code}",
            status=signup_resp.status_code,
            body=_safe_json(signup_resp),
            url=signup_url,
            method="POST",
        )

    csrf = _get_csrf(client, cfg)
    _login_credentials(
        client,
        cfg,
        email=email,
        password=TEST_PASSWORD,
        csrf_token=csrf,
        scenario="auth.signin.api.callback",
    )
    user = _session_user(client, cfg)
    if not user:
        _fail(
            cfg,
            "auth.signin.api.session",
            "expected session.user after sign-in",
            status=200,
            body={"user": user},
            url=f"{cfg.app_domain}{SESSION_PATH}",
        )
    assert user.get("email") == email


def test_signin_invalid(http_client):
    client, cfg = http_client
    csrf = _get_csrf(client, cfg)
    _login_credentials(
        client,
        cfg,
        email=unique_test_email(),
        password="WrongPass123!",
        csrf_token=csrf,
        scenario="auth.signin.invalid.callback",
    )
    user = _session_user(client, cfg)
    assert user is None
