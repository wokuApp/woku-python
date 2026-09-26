"""Read forms and send form invitations (``/v1/forms``)."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from urllib.parse import quote

from .._options import RequestOptions
from .._pagination import AsyncPage, SyncPage
from ..models import InvitationsResult, WokuRecord
from ..types import SendInvitationsParams

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class ListFormsParams(TypedDict, total=False):
    page: int
    limit: int


class Forms:
    """Read forms and send form invitations."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: ListFormsParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[WokuRecord]:
        return self._client.get_page("/v1/forms", params, options)

    def get(self, form_id: str, options: RequestOptions | None = None) -> WokuRecord:
        return self._client.request(
            "get", f"/v1/forms/{quote(form_id, safe='')}", options=options
        )

    def list_responses(
        self,
        form_id: str,
        params: ListFormsParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[WokuRecord]:
        """List the responses of a form (paginated)."""
        return self._client.get_page(
            f"/v1/forms/{quote(form_id, safe='')}/responses", params, options
        )

    def send_invitations(
        self,
        form_id: str,
        body: SendInvitationsParams,
        options: RequestOptions | None = None,
    ) -> InvitationsResult:
        """Send a form by email or WhatsApp (idempotent)."""
        return self._client.request(
            "post",
            f"/v1/forms/{quote(form_id, safe='')}/invitations",
            body=body,
            idempotent=True,
            options=options,
        )


class AsyncForms:
    """Async twin of :class:`Forms`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: ListFormsParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[WokuRecord]:
        return await self._client.get_page("/v1/forms", params, options)

    async def get(
        self, form_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._client.request(
            "get", f"/v1/forms/{quote(form_id, safe='')}", options=options
        )

    async def list_responses(
        self,
        form_id: str,
        params: ListFormsParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[WokuRecord]:
        """List the responses of a form (paginated)."""
        return await self._client.get_page(
            f"/v1/forms/{quote(form_id, safe='')}/responses", params, options
        )

    async def send_invitations(
        self,
        form_id: str,
        body: SendInvitationsParams,
        options: RequestOptions | None = None,
    ) -> InvitationsResult:
        """Send a form by email or WhatsApp (idempotent)."""
        return await self._client.request(
            "post",
            f"/v1/forms/{quote(form_id, safe='')}/invitations",
            body=body,
            idempotent=True,
            options=options,
        )
