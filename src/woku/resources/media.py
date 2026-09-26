"""Image and MP4 media uploads for journey moments and standalone Wokus."""

from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO

from .._generated import journeys as _contracts
from .._options import RequestOptions

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


MediaUploadResult = _contracts.WokuMediaUploadResultDto


class Media:
    def __init__(self, client: Woku) -> None:
        self._client = client

    def upload(
        self,
        file: bytes | BinaryIO,
        *,
        filename: str,
        content_type: str = "application/octet-stream",
        options: RequestOptions | None = None,
    ) -> MediaUploadResult:
        """Upload once without closing the caller's file handle."""
        return self._client.request(
            "post",
            "/v1/woku-media",
            files={"file": (filename, file, content_type)},
            options={**(options or {}), "max_retries": 0},
        )


class AsyncMedia:
    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def upload(
        self,
        file: bytes | BinaryIO,
        *,
        filename: str,
        content_type: str = "application/octet-stream",
        options: RequestOptions | None = None,
    ) -> MediaUploadResult:
        """Upload once without closing the caller's file handle."""
        return await self._client.request(
            "post",
            "/v1/woku-media",
            files={"file": (filename, file, content_type)},
            options={**(options or {}), "max_retries": 0},
        )
