"""Delivery tracking over invitation dispatches (``/v1/dispatches``)."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from .._options import RequestOptions
from .._pagination import AsyncPage, SyncPage
from ..models import Channel, Dispatch, DispatchStats, DispatchStatus

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class ListDispatchesParams(TypedDict, total=False):
    channel: Channel
    responseType: str
    targetId: str
    status: DispatchStatus
    createdFrom: str
    createdTo: str
    page: int
    limit: int


class DispatchStatsParams(TypedDict, total=False):
    channel: Channel
    responseType: str
    targetId: str
    createdFrom: str
    createdTo: str


class Dispatches:
    """Delivery tracking over invitation dispatches."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: ListDispatchesParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[Dispatch]:
        """List the invitation dispatches (delivery status, no recipient PII)."""
        return self._client.get_page("/v1/dispatches", params, options)

    def stats(
        self,
        params: DispatchStatsParams | None = None,
        options: RequestOptions | None = None,
    ) -> DispatchStats:
        """Response-rate metrics over the dispatches."""
        return self._client.request(
            "get", "/v1/dispatches/stats", query=params, options=options
        )


class AsyncDispatches:
    """Async twin of :class:`Dispatches`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: ListDispatchesParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[Dispatch]:
        """List the invitation dispatches (delivery status, no recipient PII)."""
        return await self._client.get_page("/v1/dispatches", params, options)

    async def stats(
        self,
        params: DispatchStatsParams | None = None,
        options: RequestOptions | None = None,
    ) -> DispatchStats:
        """Response-rate metrics over the dispatches."""
        return await self._client.request(
            "get", "/v1/dispatches/stats", query=params, options=options
        )
