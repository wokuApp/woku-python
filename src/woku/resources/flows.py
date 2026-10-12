"""Survey flows (``/v1/flows``): ordered steps of wokus and NPS, CSAT, CES tools."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from urllib.parse import quote

from .._options import RequestOptions
from .._pagination import AsyncPage, SyncPage
from ..models import DeletedResult, Flow, WokuRecord
from ..types import CreateFlowParams, UpdateFlowParams

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class ListFlowsParams(TypedDict, total=False):
    page: int
    limit: int


def _path(flow_id: str) -> str:
    return f"/v1/flows/{quote(flow_id, safe='')}"


class Flows:
    """Manage survey flows (sync)."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: ListFlowsParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[Flow]:
        """List the flows of the company, with their ordered ``steps``."""
        return self._client.get_page("/v1/flows", params, options)

    def get(self, flow_id: str, options: RequestOptions | None = None) -> WokuRecord:
        """The data of a flow: ordered steps with their tools, wokus and branding."""
        return self._client.request("get", _path(flow_id), options=options)

    def create(
        self, body: CreateFlowParams, options: RequestOptions | None = None
    ) -> Flow:
        """Create a flow from 1 to 20 ordered steps (each tool once, all yours)."""
        return self._client.request(
            "post", "/v1/flows", body=body, idempotent=True, options=options
        )

    def update(
        self,
        flow_id: str,
        body: UpdateFlowParams,
        options: RequestOptions | None = None,
    ) -> Flow:
        """Rename a flow or replace its full ordered list of steps."""
        return self._client.request("patch", _path(flow_id), body=body, options=options)

    def delete(
        self, flow_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        """Delete a flow. Its tools and their responses stay."""
        return self._client.request("delete", _path(flow_id), options=options)


class AsyncFlows:
    """Async twin of :class:`Flows`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: ListFlowsParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[Flow]:
        return await self._client.get_page("/v1/flows", params, options)

    async def get(
        self, flow_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._client.request("get", _path(flow_id), options=options)

    async def create(
        self, body: CreateFlowParams, options: RequestOptions | None = None
    ) -> Flow:
        return await self._client.request(
            "post", "/v1/flows", body=body, idempotent=True, options=options
        )

    async def update(
        self,
        flow_id: str,
        body: UpdateFlowParams,
        options: RequestOptions | None = None,
    ) -> Flow:
        return await self._client.request(
            "patch", _path(flow_id), body=body, options=options
        )

    async def delete(
        self, flow_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        return await self._client.request("delete", _path(flow_id), options=options)
