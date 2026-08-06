import sys
from pathlib import Path

_FACTORY_ROOT = Path(__file__).resolve().parents[1]
_TESTS_DIR = Path(__file__).resolve().parent
if str(_FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_FACTORY_ROOT))
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

import pytest

import config.settings as settings


@pytest.fixture(scope="session")
def factory_config():
    return settings


@pytest.fixture(scope="session")
def http_client(factory_config):
    import httpx

    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        yield client, factory_config
