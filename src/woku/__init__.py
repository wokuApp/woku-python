"""woku - official server-side SDK for the Woku management API.

Authenticate with your company secret key and manage trackers, VoC tools
(NPS/CSAT/CES), wokus, forms, flows, action plans, tickets, delivery and
captures over the public ``/v1`` API.

::

    from woku import Woku

    woku = Woku(api_key="sk_...")
    tracker = woku.trackers.create({"name": "Store", "system": "retail"})
"""

from __future__ import annotations

from ._client import AsyncWoku, Woku
from ._exceptions import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PayloadTooLargeError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
    WokuAPIError,
    WokuConnectionError,
    WokuError,
    WokuTimeoutError,
)
from ._options import RequestOptions
from ._pagination import AsyncPage, PageResponse, SyncPage
from ._version import __version__

__all__ = [
    "AsyncPage",
    "AsyncWoku",
    "AuthenticationError",
    "BadRequestError",
    "ConflictError",
    "InternalServerError",
    "NotFoundError",
    "PageResponse",
    "PermissionDeniedError",
    "PayloadTooLargeError",
    "RateLimitError",
    "RequestOptions",
    "SyncPage",
    "UnprocessableEntityError",
    "Woku",
    "WokuAPIError",
    "WokuConnectionError",
    "WokuError",
    "WokuTimeoutError",
    "__version__",
]
