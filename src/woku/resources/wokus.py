"""Manage wokus (feedback collection tools) (``/v1/wokus``)."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from urllib.parse import quote

from .._options import RequestOptions
from .._pagination import AsyncPage, SyncPage
from ..models import DeletedResult, InvitationsResult, Woku, WokuRecord
from ..types import (
    CreateWokuParams,
    MoveWokuParams,
    SendInvitationsParams,
    ShareWokuParams,
    UpdateWokuParams,
    UpdateWokuSettingsParams,
)

if TYPE_CHECKING:
    from .._client import AsyncWoku
    from .._client import Woku as WokuClient


class ListWokusParams(TypedDict, total=False):
    page: int
    limit: int


class Wokus:
    """Manage wokus."""

    def __init__(self, client: WokuClient) -> None:
        self._client = client

    def list(
        self,
        params: ListWokusParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[Woku]:
        return self._client.get_page("/v1/wokus", params, options)

    def create(
        self, body: CreateWokuParams, options: RequestOptions | None = None
    ) -> Woku:
        return self._client.request(
            "post",
            "/v1/wokus",
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    def get(self, woku_id: str, options: RequestOptions | None = None) -> Woku:
        """Get one woku with aggregated review stats."""
        return self._client.request(
            "get", f"/v1/wokus/{quote(woku_id, safe='')}", options=options
        )

    def update(
        self,
        woku_id: str,
        body: UpdateWokuParams,
        options: RequestOptions | None = None,
    ) -> Woku:
        return self._client.request(
            "patch", f"/v1/wokus/{quote(woku_id, safe='')}", body=body, options=options
        )

    def delete(
        self, woku_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        return self._client.request(
            "delete", f"/v1/wokus/{quote(woku_id, safe='')}", options=options
        )

    def update_settings(
        self,
        woku_id: str,
        body: UpdateWokuSettingsParams,
        options: RequestOptions | None = None,
    ) -> Woku:
        """Apply the boolean settings idempotently (closed/reviewsDisabled/...)."""
        return self._client.request(
            "patch",
            f"/v1/wokus/{quote(woku_id, safe='')}/settings",
            body=body,
            options=options,
        )

    def move(
        self,
        woku_id: str,
        body: MoveWokuParams,
        options: RequestOptions | None = None,
    ) -> Woku:
        """Move the woku into a folder, or to the root with ``{"folderId": None}``."""
        return self._client.request(
            "patch",
            f"/v1/wokus/{quote(woku_id, safe='')}/move",
            body=body,
            options=options,
        )

    def list_reviews(
        self,
        woku_id: str,
        params: ListWokusParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[WokuRecord]:
        """List the reviews of a woku (paginated)."""
        return self._client.get_page(
            f"/v1/wokus/{quote(woku_id, safe='')}/reviews", params, options
        )

    def send_invitations(
        self,
        woku_id: str,
        body: SendInvitationsParams,
        options: RequestOptions | None = None,
    ) -> InvitationsResult:
        """Send a woku review invitation by email or WhatsApp (idempotent)."""
        return self._client.request(
            "post",
            f"/v1/wokus/{quote(woku_id, safe='')}/invitations",
            body=body,
            idempotent=True,
            options=options,
        )

    def share(
        self,
        woku_id: str,
        body: ShareWokuParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Share a woku review link by email."""
        return self._client.request(
            "post",
            f"/v1/wokus/{quote(woku_id, safe='')}/share",
            body=body,
            options=options,
        )


class AsyncWokus:
    """Async twin of :class:`Wokus`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: ListWokusParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[Woku]:
        return await self._client.get_page("/v1/wokus", params, options)

    async def create(
        self, body: CreateWokuParams, options: RequestOptions | None = None
    ) -> Woku:
        return await self._client.request(
            "post",
            "/v1/wokus",
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    async def get(self, woku_id: str, options: RequestOptions | None = None) -> Woku:
        """Get one woku with aggregated review stats."""
        return await self._client.request(
            "get", f"/v1/wokus/{quote(woku_id, safe='')}", options=options
        )

    async def update(
        self,
        woku_id: str,
        body: UpdateWokuParams,
        options: RequestOptions | None = None,
    ) -> Woku:
        return await self._client.request(
            "patch", f"/v1/wokus/{quote(woku_id, safe='')}", body=body, options=options
        )

    async def delete(
        self, woku_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        return await self._client.request(
            "delete", f"/v1/wokus/{quote(woku_id, safe='')}", options=options
        )

    async def update_settings(
        self,
        woku_id: str,
        body: UpdateWokuSettingsParams,
        options: RequestOptions | None = None,
    ) -> Woku:
        """Apply the boolean settings idempotently (closed/reviewsDisabled/...)."""
        return await self._client.request(
            "patch",
            f"/v1/wokus/{quote(woku_id, safe='')}/settings",
            body=body,
            options=options,
        )

    async def move(
        self,
        woku_id: str,
        body: MoveWokuParams,
        options: RequestOptions | None = None,
    ) -> Woku:
        """Move the woku into a folder, or to the root with ``{"folderId": None}``."""
        return await self._client.request(
            "patch",
            f"/v1/wokus/{quote(woku_id, safe='')}/move",
            body=body,
            options=options,
        )

    async def list_reviews(
        self,
        woku_id: str,
        params: ListWokusParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[WokuRecord]:
        """List the reviews of a woku (paginated)."""
        return await self._client.get_page(
            f"/v1/wokus/{quote(woku_id, safe='')}/reviews", params, options
        )

    async def send_invitations(
        self,
        woku_id: str,
        body: SendInvitationsParams,
        options: RequestOptions | None = None,
    ) -> InvitationsResult:
        """Send a woku review invitation by email or WhatsApp (idempotent)."""
        return await self._client.request(
            "post",
            f"/v1/wokus/{quote(woku_id, safe='')}/invitations",
            body=body,
            idempotent=True,
            options=options,
        )

    async def share(
        self,
        woku_id: str,
        body: ShareWokuParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Share a woku review link by email."""
        return await self._client.request(
            "post",
            f"/v1/wokus/{quote(woku_id, safe='')}/share",
            body=body,
            options=options,
        )
