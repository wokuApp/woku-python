"""Send NPS / CSAT / CES surveys and read their responses."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from urllib.parse import quote

from .._options import RequestOptions
from .._pagination import AsyncPage, SyncPage
from ..models import InvitationsResult, WokuRecord
from ..types import (
    SendCesInvitationsParams,
    SendCsatInvitationsParams,
    SendNpsInvitationsParams,
)

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class ListResponsesParams(TypedDict, total=False):
    page: int
    limit: int


class Nps:
    """Send the NPS survey and read its responses (``/v1/nps``)."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def send_invitations(
        self,
        body: SendNpsInvitationsParams,
        options: RequestOptions | None = None,
    ) -> InvitationsResult:
        """Send the NPS survey by email or WhatsApp (idempotent)."""
        return self._client.request(
            "post", "/v1/nps/invitations", body=body, idempotent=True, options=options
        )

    def list_responses(
        self,
        params: ListResponsesParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[WokuRecord]:
        """List NPS responses (paginated)."""
        return self._client.get_page("/v1/nps", params, options)

    def get_response(
        self, response_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Get one NPS response."""
        return self._client.request(
            "get", f"/v1/nps/{quote(response_id, safe='')}", options=options
        )


class Csat:
    """Send the CSAT survey and read its responses (``/v1/csat``)."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def send_invitations(
        self,
        body: SendCsatInvitationsParams,
        options: RequestOptions | None = None,
    ) -> InvitationsResult:
        return self._client.request(
            "post", "/v1/csat/invitations", body=body, idempotent=True, options=options
        )

    def list_responses(
        self,
        params: ListResponsesParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[WokuRecord]:
        return self._client.get_page("/v1/csat", params, options)

    def get_response(
        self, response_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return self._client.request(
            "get", f"/v1/csat/{quote(response_id, safe='')}", options=options
        )


class Ces:
    """Send the CES survey and read its responses (``/v1/ces``)."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def send_invitations(
        self,
        body: SendCesInvitationsParams,
        options: RequestOptions | None = None,
    ) -> InvitationsResult:
        return self._client.request(
            "post", "/v1/ces/invitations", body=body, idempotent=True, options=options
        )

    def list_responses(
        self,
        params: ListResponsesParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[WokuRecord]:
        return self._client.get_page("/v1/ces", params, options)

    def get_response(
        self, response_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return self._client.request(
            "get", f"/v1/ces/{quote(response_id, safe='')}", options=options
        )


class AsyncNps:
    """Async twin of :class:`Nps`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def send_invitations(
        self,
        body: SendNpsInvitationsParams,
        options: RequestOptions | None = None,
    ) -> InvitationsResult:
        return await self._client.request(
            "post", "/v1/nps/invitations", body=body, idempotent=True, options=options
        )

    async def list_responses(
        self,
        params: ListResponsesParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[WokuRecord]:
        return await self._client.get_page("/v1/nps", params, options)

    async def get_response(
        self, response_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._client.request(
            "get", f"/v1/nps/{quote(response_id, safe='')}", options=options
        )


class AsyncCsat:
    """Async twin of :class:`Csat`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def send_invitations(
        self,
        body: SendCsatInvitationsParams,
        options: RequestOptions | None = None,
    ) -> InvitationsResult:
        return await self._client.request(
            "post", "/v1/csat/invitations", body=body, idempotent=True, options=options
        )

    async def list_responses(
        self,
        params: ListResponsesParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[WokuRecord]:
        return await self._client.get_page("/v1/csat", params, options)

    async def get_response(
        self, response_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._client.request(
            "get", f"/v1/csat/{quote(response_id, safe='')}", options=options
        )


class AsyncCes:
    """Async twin of :class:`Ces`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def send_invitations(
        self,
        body: SendCesInvitationsParams,
        options: RequestOptions | None = None,
    ) -> InvitationsResult:
        return await self._client.request(
            "post", "/v1/ces/invitations", body=body, idempotent=True, options=options
        )

    async def list_responses(
        self,
        params: ListResponsesParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[WokuRecord]:
        return await self._client.get_page("/v1/ces", params, options)

    async def get_response(
        self, response_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._client.request(
            "get", f"/v1/ces/{quote(response_id, safe='')}", options=options
        )
