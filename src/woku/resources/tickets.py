"""Support tickets and SAC ticket destinations.

Covers ``/v1/tickets`` and ``/v1/ticket-destinations``.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, TypedDict
from urllib.parse import quote

from .._options import RequestOptions
from .._pagination import AsyncPage, SyncPage
from ..models import Severity, TestConnectionResult, Ticket, TicketStats, WokuRecord
from ..types import (
    CreateTicketDestinationParams,
    UpdateTicketDestinationParams,
    UpdateTicketParams,
)

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class ListTicketsParams(TypedDict, total=False):
    tool: str
    severity: Severity
    search: str
    destinationId: str
    createdFrom: str
    createdTo: str
    page: int
    limit: int


class TicketStatsParams(TypedDict, total=False):
    destinationId: str
    createdFrom: str
    createdTo: str


class Tickets:
    """Read and curate support tickets. Tickets are AI-generated."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: ListTicketsParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[Ticket]:
        return self._client.get_page("/v1/tickets", params, options)

    def stats(
        self,
        params: TicketStatsParams | None = None,
        options: RequestOptions | None = None,
    ) -> TicketStats:
        """Aggregate counts by tool and by SAC destination."""
        return self._client.request(
            "get", "/v1/tickets/stats", query=params, options=options
        )

    def get(self, ticket_id: str, options: RequestOptions | None = None) -> Ticket:
        return self._client.request(
            "get", f"/v1/tickets/{quote(ticket_id, safe='')}", options=options
        )

    def update(
        self,
        ticket_id: str,
        body: UpdateTicketParams,
        options: RequestOptions | None = None,
    ) -> Ticket:
        return self._client.request(
            "patch",
            f"/v1/tickets/{quote(ticket_id, safe='')}",
            body=body,
            options=options,
        )


class TicketDestinations:
    """Manage SAC ticket destinations."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(self, options: RequestOptions | None = None) -> builtins.list[WokuRecord]:
        return self._client.request("get", "/v1/ticket-destinations", options=options)

    def get(
        self, destination_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return self._client.request(
            "get",
            f"/v1/ticket-destinations/{quote(destination_id, safe='')}",
            options=options,
        )

    def create(
        self,
        body: CreateTicketDestinationParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return self._client.request(
            "post",
            "/v1/ticket-destinations",
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    def update(
        self,
        destination_id: str,
        body: UpdateTicketDestinationParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return self._client.request(
            "patch",
            f"/v1/ticket-destinations/{quote(destination_id, safe='')}",
            body=body,
            options=options,
        )

    def delete(
        self, destination_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return self._client.request(
            "delete",
            f"/v1/ticket-destinations/{quote(destination_id, safe='')}",
            options=options,
        )

    def test(
        self, destination_id: str, options: RequestOptions | None = None
    ) -> TestConnectionResult:
        """Send a real connectivity test to a saved destination.

        Requires ``confirm: true`` (sent automatically); the test reaches the
        live destination.
        """
        return self._client.request(
            "post",
            f"/v1/ticket-destinations/{quote(destination_id, safe='')}/test",
            body={"confirm": True},
            options=options,
        )


class AsyncTickets:
    """Async twin of :class:`Tickets`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: ListTicketsParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[Ticket]:
        return await self._client.get_page("/v1/tickets", params, options)

    async def stats(
        self,
        params: TicketStatsParams | None = None,
        options: RequestOptions | None = None,
    ) -> TicketStats:
        """Aggregate counts by tool and by SAC destination."""
        return await self._client.request(
            "get", "/v1/tickets/stats", query=params, options=options
        )

    async def get(
        self, ticket_id: str, options: RequestOptions | None = None
    ) -> Ticket:
        return await self._client.request(
            "get", f"/v1/tickets/{quote(ticket_id, safe='')}", options=options
        )

    async def update(
        self,
        ticket_id: str,
        body: UpdateTicketParams,
        options: RequestOptions | None = None,
    ) -> Ticket:
        return await self._client.request(
            "patch",
            f"/v1/tickets/{quote(ticket_id, safe='')}",
            body=body,
            options=options,
        )


class AsyncTicketDestinations:
    """Async twin of :class:`TicketDestinations`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self, options: RequestOptions | None = None
    ) -> builtins.list[WokuRecord]:
        return await self._client.request(
            "get", "/v1/ticket-destinations", options=options
        )

    async def get(
        self, destination_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._client.request(
            "get",
            f"/v1/ticket-destinations/{quote(destination_id, safe='')}",
            options=options,
        )

    async def create(
        self,
        body: CreateTicketDestinationParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return await self._client.request(
            "post",
            "/v1/ticket-destinations",
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    async def update(
        self,
        destination_id: str,
        body: UpdateTicketDestinationParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return await self._client.request(
            "patch",
            f"/v1/ticket-destinations/{quote(destination_id, safe='')}",
            body=body,
            options=options,
        )

    async def delete(
        self, destination_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._client.request(
            "delete",
            f"/v1/ticket-destinations/{quote(destination_id, safe='')}",
            options=options,
        )

    async def test(
        self, destination_id: str, options: RequestOptions | None = None
    ) -> TestConnectionResult:
        """Send a real connectivity test to a saved destination (``confirm`` sent)."""
        return await self._client.request(
            "post",
            f"/v1/ticket-destinations/{quote(destination_id, safe='')}/test",
            body={"confirm": True},
            options=options,
        )
