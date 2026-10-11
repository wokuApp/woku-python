"""Folders that organize wokus and NPS, CSAT and CES tools (``/v1/folders``).

To list what a folder contains use ``woku.tools.list({"folderId": ...})``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from .._options import RequestOptions
from ..models import DeletedResult, Folder, WokuRecord
from ..types import CreateFolderParams, UpdateFolderParams

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


def _path(folder_id: str, suffix: str = "") -> str:
    return f"/v1/folders/{quote(folder_id, safe='')}{suffix}"


class Folders:
    """Manage folders (sync)."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> list[Folder]:
        """Every folder of the company, or the subfolders of ``parentFolderId``."""
        return self._client.request("get", "/v1/folders", query=params, options=options)

    def get(self, folder_id: str, options: RequestOptions | None = None) -> Folder:
        return self._client.request("get", _path(folder_id), options=options)

    def create(
        self, body: CreateFolderParams, options: RequestOptions | None = None
    ) -> Folder:
        return self._client.request(
            "post", "/v1/folders", body=body, idempotent=True, options=options
        )

    def update(
        self,
        folder_id: str,
        body: UpdateFolderParams,
        options: RequestOptions | None = None,
    ) -> Folder:
        """Rename or recolor a folder (``{"color": None}`` clears the color)."""
        return self._client.request(
            "patch", _path(folder_id), body=body, options=options
        )

    def move(
        self,
        folder_id: str,
        body: Mapping[str, Any],
        options: RequestOptions | None = None,
    ) -> Folder:
        """Move under ``{"parentFolderId": id}``, or to the root with ``None``."""
        return self._client.request(
            "patch", _path(folder_id, "/move"), body=body, options=options
        )

    def delete(
        self, folder_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        """Delete a folder. Its content moves up to the parent; nothing is deleted."""
        return self._client.request("delete", _path(folder_id), options=options)

    def report(
        self,
        folder_id: str,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """AI report over every tool of the folder and its subfolders."""
        return self._client.request(
            "get", _path(folder_id, "/report"), query=params, options=options
        )

    def csv(self, folder_id: str, options: RequestOptions | None = None) -> str:
        """CSV text with one row per response of every tool of the subtree."""
        return self._client.request("get", _path(folder_id, "/csv"), options=options)


class AsyncFolders:
    """Async twin of :class:`Folders`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> list[Folder]:
        return await self._client.request(
            "get", "/v1/folders", query=params, options=options
        )

    async def get(
        self, folder_id: str, options: RequestOptions | None = None
    ) -> Folder:
        return await self._client.request("get", _path(folder_id), options=options)

    async def create(
        self, body: CreateFolderParams, options: RequestOptions | None = None
    ) -> Folder:
        return await self._client.request(
            "post", "/v1/folders", body=body, idempotent=True, options=options
        )

    async def update(
        self,
        folder_id: str,
        body: UpdateFolderParams,
        options: RequestOptions | None = None,
    ) -> Folder:
        return await self._client.request(
            "patch", _path(folder_id), body=body, options=options
        )

    async def move(
        self,
        folder_id: str,
        body: Mapping[str, Any],
        options: RequestOptions | None = None,
    ) -> Folder:
        return await self._client.request(
            "patch", _path(folder_id, "/move"), body=body, options=options
        )

    async def delete(
        self, folder_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        return await self._client.request("delete", _path(folder_id), options=options)

    async def report(
        self,
        folder_id: str,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return await self._client.request(
            "get", _path(folder_id, "/report"), query=params, options=options
        )

    async def csv(self, folder_id: str, options: RequestOptions | None = None) -> str:
        return await self._client.request(
            "get", _path(folder_id, "/csv"), options=options
        )
