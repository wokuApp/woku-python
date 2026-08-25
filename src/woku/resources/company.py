"""The caller company and its API key (``/v1/companies/me``)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .._options import RequestOptions
from ..models import ApiKeyResult, WokuRecord

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class Company:
    """The caller company and its API key."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def me(self, options: RequestOptions | None = None) -> WokuRecord:
        """Get the caller company."""
        return self._client.request("get", "/v1/companies/me", options=options)

    def rotate_key(self, options: RequestOptions | None = None) -> ApiKeyResult:
        """Rotate the secret key. The returned key replaces the current one."""
        return self._client.request(
            "post", "/v1/companies/me/rotate-key", options=options
        )

    def revoke_key(self, options: RequestOptions | None = None) -> WokuRecord:
        """Revoke the secret key (all subsequent requests become unauthorized)."""
        return self._client.request(
            "post", "/v1/companies/me/revoke-key", options=options
        )


class AsyncCompany:
    """Async twin of :class:`Company`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def me(self, options: RequestOptions | None = None) -> WokuRecord:
        """Get the caller company."""
        return await self._client.request("get", "/v1/companies/me", options=options)

    async def rotate_key(self, options: RequestOptions | None = None) -> ApiKeyResult:
        """Rotate the secret key. The returned key replaces the current one."""
        return await self._client.request(
            "post", "/v1/companies/me/rotate-key", options=options
        )

    async def revoke_key(self, options: RequestOptions | None = None) -> WokuRecord:
        """Revoke the secret key (all subsequent requests become unauthorized)."""
        return await self._client.request(
            "post", "/v1/companies/me/revoke-key", options=options
        )
