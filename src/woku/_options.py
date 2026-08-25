"""Per-call request overrides."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypedDict


class RequestOptions(TypedDict, total=False):
    """Per-call overrides accepted by every resource method's ``options`` arg.

    All keys are optional. Anything omitted falls back to the client default.
    """

    #: Abort the request after N seconds (overrides the client default).
    timeout: float
    #: Retry budget for this call (overrides the client default).
    max_retries: int
    #: Idempotency key for a POST. Creates generate one automatically; pass your
    #: own to make a specific call safe to retry with the same result.
    idempotency_key: str
    #: Extra headers merged over the defaults (Authorization cannot be unset).
    headers: Mapping[str, str]
    #: Extra query params merged over the method's own params.
    params: Mapping[str, Any]
