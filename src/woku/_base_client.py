"""Shared, transport-agnostic client logic for the sync and async clients."""

from __future__ import annotations

import json
import os
import random
import uuid
from collections.abc import Mapping
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

from pydantic import BaseModel

from ._exceptions import WokuAPIError, WokuError
from ._version import __version__

DEFAULT_BASE_URL = "https://clientapi.woku.app"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 2
RETRY_BASE_SECONDS = 0.5
RETRY_CAP_SECONDS = 8.0
RETRYABLE_STATUS = frozenset({408, 429, 500, 502, 503, 504})
IDEMPOTENCY_HEADER = "X-Woku-Idempotency-Key"

_REQUEST_ID_HEADERS = ("x-request-id", "request-id", "x-woku-request-id")


class BaseClient:
    """Holds config and pure request-shaping helpers shared by both clients."""

    base_url: str
    timeout: float
    max_retries: int

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        resolved_key = (
            api_key if api_key is not None else os.environ.get("WOKU_API_KEY")
        )
        if not resolved_key:
            raise WokuError(
                "Missing API key: pass api_key= or set WOKU_API_KEY.",
                code="config_error",
            )
        self._api_key = resolved_key
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = DEFAULT_TIMEOUT if timeout is None else timeout
        self.max_retries = DEFAULT_MAX_RETRIES if max_retries is None else max_retries
        self._default_headers = dict(default_headers or {})

    def _resolve_idempotency_key(
        self,
        method: str,
        idempotent: bool,
        explicit: str | None,
    ) -> str | None:
        if explicit is not None:
            return explicit
        if idempotent and method.upper() == "POST":
            return f"idmp_{uuid.uuid4().hex}"
        return None

    def _build_headers(
        self,
        method: str,
        idempotency_key: str | None,
        extra_headers: Mapping[str, str] | None,
    ) -> dict[str, str]:
        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": f"woku-python/{__version__}",
        }
        headers.update(self._default_headers)
        if extra_headers:
            headers.update(extra_headers)
        # Authorization is applied last so caller headers can never unset the
        # secret key (the documented guarantee on RequestOptions.headers).
        headers["Authorization"] = f"Bearer {self._api_key}"
        if idempotency_key is not None and method.upper() == "POST":
            headers[IDEMPOTENCY_HEADER] = idempotency_key
        return headers

    def _backoff(self, attempt: int, api_error: WokuAPIError | None = None) -> float:
        """Honor ``Retry-After`` (seconds) when present, else full jitter."""
        retry_after = api_error.retry_after_seconds if api_error is not None else None
        if retry_after is not None:
            return min(retry_after, RETRY_CAP_SECONDS)
        ceiling = min(RETRY_CAP_SECONDS, RETRY_BASE_SECONDS * (2**attempt))
        return random.random() * ceiling


def retry_after_from_headers(headers: Mapping[str, str]) -> float | None:
    """Parse ``Retry-After`` (a number of seconds or an HTTP date)."""
    raw = headers.get("retry-after")
    if not raw:
        return None
    raw = raw.strip()
    try:
        return max(0.0, float(raw))
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None
    if when is None:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())


def serialize_body(body: Any) -> Any:
    """Turn a request body into a JSON-serializable value.

    Pydantic models are dumped by alias, dropping fields the caller never set so
    a partial update sends only what changed. Mappings pass through as-is.
    """
    if body is None:
        return None
    if isinstance(body, BaseModel):
        return body.model_dump(mode="json", by_alias=True, exclude_unset=True)
    return body


def clean_query(query: Mapping[str, Any] | None) -> dict[str, Any]:
    """Drop ``None`` values; leave lists for the transport to expand."""
    if not query:
        return {}
    return {key: value for key, value in query.items() if value is not None}


def parse_body(text: str) -> Any:
    if not text:
        return None
    try:
        return json.loads(text)
    except ValueError:
        return text


def request_id_from(headers: Mapping[str, str]) -> str | None:
    for name in _REQUEST_ID_HEADERS:
        value = headers.get(name)
        if value:
            return value
    return None
