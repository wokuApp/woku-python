"""Check respondent quarantine status (``/v1/quarantines``)."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from .._options import RequestOptions
from ..models import WokuRecord

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class QuarantineCheckParams(TypedDict, total=False):
    email: str
    phone: str | int


class Quarantines:
    """Check respondent quarantine status."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def check(
        self,
        params: QuarantineCheckParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Check whether a contact is quarantined."""
        return self._client.request(
            "get", "/v1/quarantines/check", query=params, options=options
        )


class AsyncQuarantines:
    """Async twin of :class:`Quarantines`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def check(
        self,
        params: QuarantineCheckParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Check whether a contact is quarantined."""
        return await self._client.request(
            "get", "/v1/quarantines/check", query=params, options=options
        )
