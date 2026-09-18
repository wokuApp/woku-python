"""Customer journeys (``/v1/journeys``).

Define the moments where you listen to a customer, assign a tool you already
have to each one, and set them off by hand or from your own events.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

from .._options import RequestOptions
from ..models import WokuRecord

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class JourneyContact(TypedDict, total=False):
    email: str
    phone: str


class JourneyTracker(TypedDict):
    name: str
    value: str


class EnrollParams(TypedDict, total=False):
    """Who is enrolled and how to reach them."""

    subjectKey: str
    contact: JourneyContact
    trackers: list[JourneyTracker]
    metadata: dict[str, Any]


class JourneyEventParams(TypedDict, total=False):
    """One of your own events. Names starting with ``journey.`` are reserved."""

    event: str
    subjectKey: str
    contact: JourneyContact
    trackers: list[JourneyTracker]
    metadata: dict[str, Any]


class Journeys:
    """Customer journeys: their moments, and how each one starts."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(self, options: RequestOptions | None = None) -> list[WokuRecord]:
        """Every journey of your company."""
        return self._client.request("get", "/v1/journeys", options=options)

    def get(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """One journey with its moments."""
        return self._client.request(
            "get", f"/v1/journeys/{journey_id}", options=options
        )

    def create(
        self, body: dict[str, Any], options: RequestOptions | None = None
    ) -> WokuRecord:
        """Create a journey.

        The response carries ``webhookSecret`` once and only here: it is what
        signs this journey's inbound calls, so store it now.
        """
        return self._client.request(
            "post", "/v1/journeys", body=body, options=options
        )

    def update(
        self,
        journey_id: str,
        body: dict[str, Any],
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Rename it, switch it on or off, or replace its moments.

        Replacing the moments mints a new version; the enrollments already
        running keep executing the version they started with.
        """
        return self._client.request(
            "patch", f"/v1/journeys/{journey_id}", body=body, options=options
        )

    def delete(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> None:
        """Delete a journey. What it already started keeps its own history."""
        return self._client.request(
            "delete", f"/v1/journeys/{journey_id}", options=options
        )

    def rotate_webhook_secret(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Mint a new signing secret, keeping the previous one valid."""
        return self._client.request(
            "post",
            f"/v1/journeys/{journey_id}/webhook-secret",
            body={},
            options=options,
        )

    def enroll(
        self,
        journey_id: str,
        body: EnrollParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Start the journey for one subject."""
        return self._client.request(
            "post",
            f"/v1/journeys/{journey_id}/enrollments",
            body=body,
            options=options,
        )

    def emit_event(
        self, body: JourneyEventParams, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Emit one of your own events to every journey that listens for it."""
        return self._client.request(
            "post", "/v1/journey-events", body=body, options=options
        )


class AsyncJourneys:
    """Async twin of :class:`Journeys`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self, options: RequestOptions | None = None
    ) -> list[WokuRecord]:
        """Every journey of your company."""
        return await self._client.request("get", "/v1/journeys", options=options)

    async def get(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """One journey with its moments."""
        return await self._client.request(
            "get", f"/v1/journeys/{journey_id}", options=options
        )

    async def create(
        self, body: dict[str, Any], options: RequestOptions | None = None
    ) -> WokuRecord:
        """Create a journey; the signing secret comes back once, here."""
        return await self._client.request(
            "post", "/v1/journeys", body=body, options=options
        )

    async def update(
        self,
        journey_id: str,
        body: dict[str, Any],
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Rename it, switch it on or off, or replace its moments."""
        return await self._client.request(
            "patch", f"/v1/journeys/{journey_id}", body=body, options=options
        )

    async def delete(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> None:
        """Delete a journey."""
        return await self._client.request(
            "delete", f"/v1/journeys/{journey_id}", options=options
        )

    async def rotate_webhook_secret(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Mint a new signing secret, keeping the previous one valid."""
        return await self._client.request(
            "post",
            f"/v1/journeys/{journey_id}/webhook-secret",
            body={},
            options=options,
        )

    async def enroll(
        self,
        journey_id: str,
        body: EnrollParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Start the journey for one subject."""
        return await self._client.request(
            "post",
            f"/v1/journeys/{journey_id}/enrollments",
            body=body,
            options=options,
        )

    async def emit_event(
        self, body: JourneyEventParams, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Emit one of your own events to every journey that listens for it."""
        return await self._client.request(
            "post", "/v1/journey-events", body=body, options=options
        )
