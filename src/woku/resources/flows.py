"""Read data flows (``/v1/flows``)."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from .._options import RequestOptions
from .._pagination import AsyncPage, SyncPage
from ..models import WokuRecord

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class ListFlowsParams(TypedDict, total=False):
    page: int
    limit: int


class Flows:
    """Read data flows."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: ListFlowsParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[WokuRecord]:
        return self._client.get_page("/v1/flows", params, options)

    def get(self, flow_id: str, options: RequestOptions | None = None) -> WokuRecord:
        return self._client.request("get", f"/v1/flows/{flow_id}", options=options)


class AsyncFlows:
    """Async twin of :class:`Flows`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: ListFlowsParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[WokuRecord]:
        return await self._client.get_page("/v1/flows", params, options)

    async def get(
        self, flow_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._client.request(
            "get", f"/v1/flows/{flow_id}", options=options
        )
