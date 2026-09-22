"""Customer journeys (``/v1/journeys``).

Define the moments where you listen to a customer, create a tool per enrollment
or share one within that same moment, and set them off by hand or from your own events.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypedDict
from urllib.parse import quote, urljoin

from .._options import RequestOptions
from ..models import WokuRecord

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class JourneyRecipients(TypedDict):
    ticketEmails: list[str]
    planEmails: list[str]


class JourneyInput(TypedDict, total=False):
    """V2 supports operator, first-answer and webhook initiation."""

    name: str
    enabled: bool
    authoringVersion: Literal[1, 2]
    startMode: Literal["operator", "response", "webhook"]
    recipients: JourneyRecipients
    moments: list[dict[str, Any]]


class ListEnrollmentsParams(TypedDict, total=False):
    cursor: str
    limit: int


class StopEnrollmentParams(TypedDict, total=False):
    reason: str


class JourneyEnrollmentPage(TypedDict, total=False):
    items: list[WokuRecord]
    nextCursor: str


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

    def get(self, journey_id: str, options: RequestOptions | None = None) -> WokuRecord:
        """One journey with its moments."""
        return self._client.request(
            "get", f"/v1/journeys/{journey_id}", options=options
        )

    def create(
        self, body: JourneyInput | dict[str, Any], options: RequestOptions | None = None
    ) -> WokuRecord:
        """Create a journey.

        The response carries ``webhookSecret`` once and only here: it is what
        signs this journey's inbound calls, so store it now.
        """
        return self._client.request("post", "/v1/journeys", body=body, options=options)

    def update(
        self,
        journey_id: str,
        body: JourneyInput | dict[str, Any],
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Rename it, switch it on or off, or replace its moments.

        Replacing the moments mints a new version; the enrollments already
        running keep executing the version they started with.
        """
        return self._client.request(
            "patch", f"/v1/journeys/{journey_id}", body=body, options=options
        )

    def delete(self, journey_id: str, options: RequestOptions | None = None) -> None:
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

    def list_enrollments(
        self,
        journey_id: str,
        params: ListEnrollmentsParams | None = None,
        options: RequestOptions | None = None,
    ) -> JourneyEnrollmentPage:
        """List exact cases; pass nextCursor as cursor for the next page."""
        return self._client.request(
            "get",
            f"/v1/journeys/{quote(journey_id, safe='')}/enrollments",
            query=params,
            options=options,
        )

    def get_enrollment(
        self, journey_id: str, enrollment_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Read one case's history and next step."""
        return self._client.request(
            "get",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/enrollments/{quote(enrollment_id, safe='')}"
            ),
            options=options,
        )

    def stop_enrollment(
        self,
        journey_id: str,
        enrollment_id: str,
        body: StopEnrollmentParams | None = None,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Stop future work for one case, preserving answers and other cases."""
        return self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/enrollments/{quote(enrollment_id, safe='')}/stop"
            ),
            body=body or {},
            options=options,
        )

    def connections(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> list[WokuRecord]:
        """Read credential readiness, not proof of a real webhook delivery."""
        return self._client.request(
            "get",
            f"/v1/journeys/{quote(journey_id, safe='')}/connections",
            options=options,
        )

    def mint_moment_url(
        self, journey_id: str, stage_key: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Replace this moment's credential URL and return the new URL once."""
        result: WokuRecord = self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/moments/{quote(stage_key, safe='')}/url-token"
            ),
            body={},
            options=options,
        )

        return {**result, "url": urljoin(self._client.base_url, result["url"])}

    def set_sender_secret(
        self,
        journey_id: str,
        stage_key: str,
        sender_secret: str,
        options: RequestOptions | None = None,
    ) -> None:
        """Store an external sender's signing secret encrypted."""
        return self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/moments/{quote(stage_key, safe='')}/sender-secret"
            ),
            body={"senderSecret": sender_secret},
            options=options,
        )

    def preview_moment(
        self,
        journey_id: str,
        stage_key: str,
        payload: dict[str, Any],
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Interpret a sample with saved mapping without starting or sending."""
        return self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/moments/{quote(stage_key, safe='')}/preview"
            ),
            body={"payload": payload},
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

    async def list(self, options: RequestOptions | None = None) -> list[WokuRecord]:
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
        self, body: JourneyInput | dict[str, Any], options: RequestOptions | None = None
    ) -> WokuRecord:
        """Create a journey; the signing secret comes back once, here."""
        return await self._client.request(
            "post", "/v1/journeys", body=body, options=options
        )

    async def update(
        self,
        journey_id: str,
        body: JourneyInput | dict[str, Any],
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

    async def list_enrollments(
        self,
        journey_id: str,
        params: ListEnrollmentsParams | None = None,
        options: RequestOptions | None = None,
    ) -> JourneyEnrollmentPage:
        """List exact cases; pass nextCursor as cursor for the next page."""
        return await self._client.request(
            "get",
            f"/v1/journeys/{quote(journey_id, safe='')}/enrollments",
            query=params,
            options=options,
        )

    async def get_enrollment(
        self, journey_id: str, enrollment_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Read one case's history and next step."""
        return await self._client.request(
            "get",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/enrollments/{quote(enrollment_id, safe='')}"
            ),
            options=options,
        )

    async def stop_enrollment(
        self,
        journey_id: str,
        enrollment_id: str,
        body: StopEnrollmentParams | None = None,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Stop future work for one case, preserving answers and other cases."""
        return await self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/enrollments/{quote(enrollment_id, safe='')}/stop"
            ),
            body=body or {},
            options=options,
        )

    async def connections(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> list[WokuRecord]:
        """Read credential readiness, not proof of a real webhook delivery."""
        return await self._client.request(
            "get",
            f"/v1/journeys/{quote(journey_id, safe='')}/connections",
            options=options,
        )

    async def mint_moment_url(
        self, journey_id: str, stage_key: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Replace this moment's credential URL and return the new URL once."""
        result: WokuRecord = await self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/moments/{quote(stage_key, safe='')}/url-token"
            ),
            body={},
            options=options,
        )

        return {**result, "url": urljoin(self._client.base_url, result["url"])}

    async def set_sender_secret(
        self,
        journey_id: str,
        stage_key: str,
        sender_secret: str,
        options: RequestOptions | None = None,
    ) -> None:
        """Store an external sender's signing secret encrypted."""
        return await self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/moments/{quote(stage_key, safe='')}/sender-secret"
            ),
            body={"senderSecret": sender_secret},
            options=options,
        )

    async def preview_moment(
        self,
        journey_id: str,
        stage_key: str,
        payload: dict[str, Any],
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Interpret a sample with saved mapping without starting or sending."""
        return await self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/moments/{quote(stage_key, safe='')}/preview"
            ),
            body={"payload": payload},
            options=options,
        )

    async def emit_event(
        self, body: JourneyEventParams, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Emit one of your own events to every journey that listens for it."""
        return await self._client.request(
            "post", "/v1/journey-events", body=body, options=options
        )
