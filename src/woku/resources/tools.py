"""The unified view over wokus and NPS, CSAT and CES tools (``/v1/tools``)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Mapping
from typing import TYPE_CHECKING, Any

from .._options import RequestOptions
from ..models import Folder, MoveResult, ToolItem, ToolsStats
from ..types import MoveToolItemsParams

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


def _list_query(params: Mapping[str, Any] | None, cursor: str | None) -> dict[str, Any]:
    query = dict(params or {})
    types = query.get("types")
    if isinstance(types, (list, tuple)):
        query["types"] = ",".join(types)
    if cursor:
        query["cursor"] = cursor
    return query


class _BaseToolsPage:
    def __init__(self, response: Mapping[str, Any]) -> None:
        self.folders: list[Folder] = list(response.get("folders") or [])
        self.tools: list[ToolItem] = list(response.get("tools") or [])
        self.next_cursor: str | None = response.get("nextCursor")
        self.facets: dict[str, Any] = dict(response.get("facets") or {})

    def has_next_page(self) -> bool:
        return self.next_cursor is not None


class ToolsPage(_BaseToolsPage):
    """One page of ``tools.list``. Iterate every tool across pages with ``for``."""

    def __init__(self, response: Mapping[str, Any], fetch_next: Any) -> None:
        super().__init__(response)
        self._fetch_next = fetch_next

    def get_next_page(self) -> ToolsPage:
        if self.next_cursor is None:
            raise IndexError("No next page")
        return self._fetch_next(self.next_cursor)

    def iter_pages(self) -> Iterator[ToolsPage]:
        page: ToolsPage = self
        while True:
            yield page
            if not page.has_next_page():
                return
            page = page.get_next_page()

    def __iter__(self) -> Iterator[ToolItem]:
        for page in self.iter_pages():
            yield from page.tools


class AsyncToolsPage(_BaseToolsPage):
    """Async twin of :class:`ToolsPage` (``async for`` over every tool)."""

    def __init__(self, response: Mapping[str, Any], fetch_next: Any) -> None:
        super().__init__(response)
        self._fetch_next = fetch_next

    async def get_next_page(self) -> AsyncToolsPage:
        if self.next_cursor is None:
            raise IndexError("No next page")
        return await self._fetch_next(self.next_cursor)

    async def iter_pages(self) -> AsyncIterator[AsyncToolsPage]:
        page: AsyncToolsPage = self
        while True:
            yield page
            if not page.has_next_page():
                return
            page = await page.get_next_page()

    async def __aiter__(self) -> AsyncIterator[ToolItem]:
        async for page in self.iter_pages():
            for tool in page.tools:
                yield tool


class Tools:
    """Search, headline figures and batch moves across every tool type."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> ToolsPage:
        """List one folder level, or search the company with ``q``/``scope``.

        ``params``: ``folderId``, ``scope`` (``level``/``company``), ``types``
        (list of ``woku``/``nps``/``csat``/``ces``), ``q``, ``sort``, ``limit``,
        ``createdFrom``, ``createdTo``.
        """

        def fetch(cursor: str | None = None) -> ToolsPage:
            response = self._client.request(
                "get",
                "/v1/tools",
                query=_list_query(params, cursor),
                options=options,
            )
            return ToolsPage(response, fetch)

        return fetch()

    def stats(
        self,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> ToolsStats:
        """Headline figures per type (native scales), company or ``folderId``."""
        return self._client.request(
            "get", "/v1/tools/stats", query=params, options=options
        )

    def move(
        self, body: MoveToolItemsParams, options: RequestOptions | None = None
    ) -> MoveResult:
        """Move up to 200 items of mixed types to a folder, or the root (None)."""
        return self._client.request(
            "post", "/v1/tools/move", body=body, options=options
        )


class AsyncTools:
    """Async twin of :class:`Tools`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncToolsPage:
        async def fetch(cursor: str | None = None) -> AsyncToolsPage:
            response = await self._client.request(
                "get",
                "/v1/tools",
                query=_list_query(params, cursor),
                options=options,
            )
            return AsyncToolsPage(response, fetch)

        return await fetch()

    async def stats(
        self,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> ToolsStats:
        return await self._client.request(
            "get", "/v1/tools/stats", query=params, options=options
        )

    async def move(
        self, body: MoveToolItemsParams, options: RequestOptions | None = None
    ) -> MoveResult:
        return await self._client.request(
            "post", "/v1/tools/move", body=body, options=options
        )
