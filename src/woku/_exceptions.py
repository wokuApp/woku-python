"""Error hierarchy for the Woku SDK.

Every failure is a :class:`WokuError`. Transport failures (DNS/TLS/timeout) are
:class:`WokuConnectionError`; HTTP error responses are :class:`WokuAPIError`
subclasses keyed by status. API errors carry the server ``request_id`` (echo it
when reporting an issue) and the parsed body.
"""

from __future__ import annotations

from typing import Any, Union

WokuErrorBody = Union[dict[str, Any], str, None]


class WokuError(Exception):
    """Base class for every SDK error."""

    #: Stable, machine-readable code (e.g. ``not_found``, ``rate_limited``).
    code: str | None

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code


class WokuConnectionError(WokuError):
    """The request never got a usable HTTP response.

    DNS/TCP failure, TLS error, timeout or a cancelled request. Safe to retry
    (the SDK already retries these up to ``max_retries``).
    """

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message, code=code or "connection_error")


class WokuTimeoutError(WokuConnectionError):
    """The request exceeded the configured timeout."""

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message, code="timeout")


class WokuAPIError(WokuError):
    """The server returned a non-2xx HTTP status."""

    #: HTTP status code.
    status: int
    #: Server correlation id, if the response carried one.
    request_id: str | None
    #: Parsed response body (or the raw text when it was not JSON).
    body: WokuErrorBody

    def __init__(
        self,
        status: int,
        body: WokuErrorBody,
        message: str,
        request_id: str | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message, code=code or _code_for_status(status))
        self.status = status
        self.body = body
        self.request_id = request_id

    @classmethod
    def from_response(
        cls,
        status: int,
        body: WokuErrorBody,
        request_id: str | None = None,
    ) -> WokuAPIError:
        """Build the most specific error subclass for a status + body."""
        message = _message_from(status, body, request_id)
        subclass = _STATUS_TO_CLASS.get(status)
        if subclass is not None:
            return subclass(status, body, message, request_id)
        if status >= 500:
            return InternalServerError(status, body, message, request_id)
        return cls(status, body, message, request_id)


class BadRequestError(WokuAPIError):
    """400 - malformed request or failed validation."""


class AuthenticationError(WokuAPIError):
    """401 - missing or invalid API key."""


class PermissionDeniedError(WokuAPIError):
    """403 - the key is valid but not allowed to access the resource."""


class NotFoundError(WokuAPIError):
    """404 - the resource does not exist (or is not visible to this company)."""


class ConflictError(WokuAPIError):
    """409 - the request conflicts with the resource state."""


class UnprocessableEntityError(WokuAPIError):
    """422 - semantically invalid request."""


class RateLimitError(WokuAPIError):
    """429 - rate limited. ``retry_after_seconds`` mirrors ``Retry-After``."""

    retry_after_seconds: float | None

    def __init__(
        self,
        status: int,
        body: WokuErrorBody,
        message: str,
        request_id: str | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(status, body, message, request_id, code)
        self.retry_after_seconds = None
        if isinstance(body, dict):
            retry_after = body.get("retryAfter")
            if isinstance(retry_after, (int, float)) and not isinstance(
                retry_after, bool
            ):
                self.retry_after_seconds = float(retry_after)


class InternalServerError(WokuAPIError):
    """5xx - the server failed to process the request."""


_STATUS_TO_CLASS: dict[int, type[WokuAPIError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: RateLimitError,
}

_STATUS_TO_CODE: dict[int, str] = {
    400: "bad_request",
    401: "authentication_error",
    403: "permission_denied",
    404: "not_found",
    409: "conflict",
    422: "unprocessable_entity",
    429: "rate_limited",
}


def _code_for_status(status: int) -> str:
    code = _STATUS_TO_CODE.get(status)
    if code is not None:
        return code
    return "internal_server_error" if status >= 500 else "api_error"


def _message_from(
    status: int,
    body: WokuErrorBody,
    request_id: str | None,
) -> str:
    detail = f"HTTP {status}"
    if isinstance(body, str) and body.strip():
        detail = body.strip()
    elif isinstance(body, dict):
        message = body.get("message")
        if isinstance(message, list):
            detail = ", ".join(str(item) for item in message)
        elif isinstance(message, str) and message:
            detail = message
        elif isinstance(body.get("error"), str):
            detail = body["error"]
    if request_id:
        return f"{status} {detail} (request_id: {request_id})"
    return f"{status} {detail}"
