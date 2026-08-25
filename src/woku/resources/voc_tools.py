"""VoC tool definitions: NPS / CSAT / CES (``/v1/{nps,csat,ces}-tools``).

Note the read path is singular (``/v1/nps-tool/{id}``) while list and the CRUD
mutations use the plural (``/v1/nps-tools``), matching the server routes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from .._options import RequestOptions
from .._pagination import AsyncPage, SyncPage
from ..models import CesTool, CsatTool, DeletedResult, NpsTool
from ..types import (
    CreateCesToolParams,
    CreateCsatToolParams,
    CreateNpsToolParams,
    UpdateCesToolParams,
    UpdateCsatToolParams,
    UpdateNpsToolParams,
)

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class ListToolsParams(TypedDict, total=False):
    page: int
    limit: int


class NpsTools:
    """Manage NPS tool definitions."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: ListToolsParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[NpsTool]:
        return self._client.get_page("/v1/nps-tools", params, options)

    def create(
        self, body: CreateNpsToolParams, options: RequestOptions | None = None
    ) -> NpsTool:
        return self._client.request(
            "post", "/v1/nps-tools", body=body, idempotent=True, options=options
        )

    def get(self, tool_id: str, options: RequestOptions | None = None) -> NpsTool:
        return self._client.request("get", f"/v1/nps-tool/{tool_id}", options=options)

    def update(
        self,
        tool_id: str,
        body: UpdateNpsToolParams,
        options: RequestOptions | None = None,
    ) -> NpsTool:
        return self._client.request(
            "patch", f"/v1/nps-tools/{tool_id}", body=body, options=options
        )

    def delete(
        self, tool_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        return self._client.request(
            "delete", f"/v1/nps-tools/{tool_id}", options=options
        )


class CsatTools:
    """Manage CSAT tool definitions."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: ListToolsParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[CsatTool]:
        return self._client.get_page("/v1/csat-tools", params, options)

    def create(
        self, body: CreateCsatToolParams, options: RequestOptions | None = None
    ) -> CsatTool:
        return self._client.request(
            "post", "/v1/csat-tools", body=body, idempotent=True, options=options
        )

    def get(self, tool_id: str, options: RequestOptions | None = None) -> CsatTool:
        return self._client.request("get", f"/v1/csat-tool/{tool_id}", options=options)

    def update(
        self,
        tool_id: str,
        body: UpdateCsatToolParams,
        options: RequestOptions | None = None,
    ) -> CsatTool:
        return self._client.request(
            "patch", f"/v1/csat-tools/{tool_id}", body=body, options=options
        )

    def delete(
        self, tool_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        return self._client.request(
            "delete", f"/v1/csat-tools/{tool_id}", options=options
        )


class CesTools:
    """Manage CES tool definitions."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: ListToolsParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[CesTool]:
        return self._client.get_page("/v1/ces-tools", params, options)

    def create(
        self, body: CreateCesToolParams, options: RequestOptions | None = None
    ) -> CesTool:
        return self._client.request(
            "post", "/v1/ces-tools", body=body, idempotent=True, options=options
        )

    def get(self, tool_id: str, options: RequestOptions | None = None) -> CesTool:
        return self._client.request("get", f"/v1/ces-tool/{tool_id}", options=options)

    def update(
        self,
        tool_id: str,
        body: UpdateCesToolParams,
        options: RequestOptions | None = None,
    ) -> CesTool:
        return self._client.request(
            "patch", f"/v1/ces-tools/{tool_id}", body=body, options=options
        )

    def delete(
        self, tool_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        return self._client.request(
            "delete", f"/v1/ces-tools/{tool_id}", options=options
        )


class AsyncNpsTools:
    """Async twin of :class:`NpsTools`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: ListToolsParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[NpsTool]:
        return await self._client.get_page("/v1/nps-tools", params, options)

    async def create(
        self, body: CreateNpsToolParams, options: RequestOptions | None = None
    ) -> NpsTool:
        return await self._client.request(
            "post", "/v1/nps-tools", body=body, idempotent=True, options=options
        )

    async def get(self, tool_id: str, options: RequestOptions | None = None) -> NpsTool:
        return await self._client.request(
            "get", f"/v1/nps-tool/{tool_id}", options=options
        )

    async def update(
        self,
        tool_id: str,
        body: UpdateNpsToolParams,
        options: RequestOptions | None = None,
    ) -> NpsTool:
        return await self._client.request(
            "patch", f"/v1/nps-tools/{tool_id}", body=body, options=options
        )

    async def delete(
        self, tool_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        return await self._client.request(
            "delete", f"/v1/nps-tools/{tool_id}", options=options
        )


class AsyncCsatTools:
    """Async twin of :class:`CsatTools`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: ListToolsParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[CsatTool]:
        return await self._client.get_page("/v1/csat-tools", params, options)

    async def create(
        self, body: CreateCsatToolParams, options: RequestOptions | None = None
    ) -> CsatTool:
        return await self._client.request(
            "post", "/v1/csat-tools", body=body, idempotent=True, options=options
        )

    async def get(
        self, tool_id: str, options: RequestOptions | None = None
    ) -> CsatTool:
        return await self._client.request(
            "get", f"/v1/csat-tool/{tool_id}", options=options
        )

    async def update(
        self,
        tool_id: str,
        body: UpdateCsatToolParams,
        options: RequestOptions | None = None,
    ) -> CsatTool:
        return await self._client.request(
            "patch", f"/v1/csat-tools/{tool_id}", body=body, options=options
        )

    async def delete(
        self, tool_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        return await self._client.request(
            "delete", f"/v1/csat-tools/{tool_id}", options=options
        )


class AsyncCesTools:
    """Async twin of :class:`CesTools`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: ListToolsParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[CesTool]:
        return await self._client.get_page("/v1/ces-tools", params, options)

    async def create(
        self, body: CreateCesToolParams, options: RequestOptions | None = None
    ) -> CesTool:
        return await self._client.request(
            "post", "/v1/ces-tools", body=body, idempotent=True, options=options
        )

    async def get(self, tool_id: str, options: RequestOptions | None = None) -> CesTool:
        return await self._client.request(
            "get", f"/v1/ces-tool/{tool_id}", options=options
        )

    async def update(
        self,
        tool_id: str,
        body: UpdateCesToolParams,
        options: RequestOptions | None = None,
    ) -> CesTool:
        return await self._client.request(
            "patch", f"/v1/ces-tools/{tool_id}", body=body, options=options
        )

    async def delete(
        self, tool_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        return await self._client.request(
            "delete", f"/v1/ces-tools/{tool_id}", options=options
        )
