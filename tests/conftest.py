from __future__ import annotations

import pytest

from woku._base_client import BaseClient

BASE = "http://api.test"


@pytest.fixture(autouse=True)
def _fast_and_isolated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Zero out retry backoff and drop any ambient API key from the env."""
    monkeypatch.setattr(
        BaseClient, "_backoff", lambda self, attempt, api_error=None: 0.0
    )
    monkeypatch.delenv("WOKU_API_KEY", raising=False)
