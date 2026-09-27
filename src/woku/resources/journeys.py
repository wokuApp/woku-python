"""Customer journeys (``/v1/journeys``).

Define the moments where you listen to a customer, create a tool per enrollment
or share one within that same moment, and set them off by hand or from your own events.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any, TypedDict
from urllib.parse import quote, urljoin

from pydantic import BaseModel

from .._exceptions import WokuError
from .._options import RequestOptions

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


# Structural dictionary contracts are generated from the same OpenAPI as the
# Pydantic request models. Runtime responses remain ordinary dictionaries.
from .._generated import journeys as _contracts

Journey = _contracts.V1JourneyResponseDto
CreatedJourney = _contracts.V1CreatedJourneyResponseDto
JourneyEnrollment = _contracts.V1JourneyParticipationDto
JourneyEnrollmentPage = _contracts.V1JourneyParticipationPageDto
JourneyConnection = _contracts.V1JourneyConnectionDto
JourneyMomentUrl = _contracts.V1JourneyMomentUrlDto
JourneyMomentPreview = _contracts.V1JourneyPreviewResponseDto
JourneyMoment = _contracts.V1JourneyMomentDto
JourneyPlanMember = _contracts.JourneyPlanMemberDto
JourneyRecipients = _contracts.JourneyRecipientsDto
JourneyInput = _contracts.V1UpdateJourneyBodyDto
CreateJourneyInput = _contracts.V1CreateJourneyBodyDto
JourneyContact = _contracts.V1JourneyContactDto
JourneyTracker = _contracts.V1JourneyTrackerDto
EnrollParams = _contracts.V1EnrollSubjectBodyDto
JourneyEventParams = _contracts.V1EmitJourneyEventBodyDto
EnrollmentResult = _contracts.V1JourneyEnrollmentResponseDto
EventResult = _contracts.V1JourneyEventResponseDto
JourneySecret = _contracts.V1JourneySecretResponseDto
JourneyEntryInfo = _contracts.JourneyEntryInfoDto
PrepareJourneyEntryInput = _contracts.PrepareJourneyEntryDto
PreparedJourneyEntry = _contracts.PreparedJourneyEntryDto


class ListEnrollmentsParams(TypedDict, total=False):
    cursor: str
    limit: int


class StopEnrollmentParams(TypedDict, total=False):
    reason: str


class Journeys:
    """Customer journeys: their moments, and how each one starts."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def entry_info(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> JourneyEntryInfo:
        """Read customer entry metadata without starting an evaluation."""
        return self._client.request(
            "get", f"/v1/journey-entries/{quote(journey_id, safe='')}", options=options
        )

    def prepare_entry(
        self,
        journey_id: str,
        body: PrepareJourneyEntryInput | BaseModel,
        options: RequestOptions | None = None,
    ) -> PreparedJourneyEntry:
        """Prepare a first tool; its valid saved answer confirms the start."""
        return self._client.request(
            "post",
            f"/v1/journey-entries/{quote(journey_id, safe='')}",
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    def list(self, options: RequestOptions | None = None) -> list[Journey]:
        """Every journey of your company."""
        return self._client.request("get", "/v1/journeys", options=options)

    def get(self, journey_id: str, options: RequestOptions | None = None) -> Journey:
        """One journey with its moments."""
        return self._client.request(
            "get", f"/v1/journeys/{quote(journey_id, safe='')}", options=options
        )

    def create(
        self,
        body: JourneyInput | dict[str, Any] | BaseModel,
        options: RequestOptions | None = None,
    ) -> CreatedJourney:
        """Create a journey.

        The response carries the legacy ``woku_signature`` secret once.
        V2 URL tokens and sender HMAC secrets are separate moment credentials.
        """
        return self._client.request(
            "post", "/v1/journeys", body=body, options=options, idempotent=True
        )

    def update(
        self,
        journey_id: str,
        body: JourneyInput | dict[str, Any] | BaseModel,
        options: RequestOptions | None = None,
    ) -> Journey:
        """Rename it, switch it on or off, or replace its moments.

        Replacing the moments mints a new version; the enrollments already
        running keep executing the version they started with.
        """
        return self._client.request(
            "patch",
            f"/v1/journeys/{quote(journey_id, safe='')}",
            body=body,
            options=options,
        )

    def delete(self, journey_id: str, options: RequestOptions | None = None) -> None:
        """Delete a journey. What it already started keeps its own history."""
        return self._client.request(
            "delete", f"/v1/journeys/{quote(journey_id, safe='')}", options=options
        )

    def rotate_webhook_secret(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> JourneySecret:
        """Mint a new signing secret, keeping the previous one valid."""
        return self._client.request(
            "post",
            f"/v1/journeys/{quote(journey_id, safe='')}/webhook-secret",
            body={},
            options={**(options or {}), "max_retries": 0},
        )

    def enroll(
        self,
        journey_id: str,
        body: EnrollParams,
        options: RequestOptions | None = None,
    ) -> EnrollmentResult:
        """Start the journey for one subject."""
        return self._client.request(
            "post",
            f"/v1/journeys/{quote(journey_id, safe='')}/enrollments",
            body=body,
            options=options,
            idempotent=True,
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

    def iter_enrollments(
        self,
        journey_id: str,
        params: ListEnrollmentsParams | None = None,
        options: RequestOptions | None = None,
    ) -> Iterator[JourneyEnrollment]:
        """Walk exact customer cases lazily without repeating a cursor."""
        query = {**dict(params or {}), **dict((options or {}).get("params") or {})}
        seen: set[str] = set()
        while True:
            page = self.list_enrollments(
                journey_id, options={**(options or {}), "params": query}
            )
            yield from page["items"]
            cursor = page.get("nextCursor")
            if not cursor:
                return
            if cursor in seen or cursor == query.get("cursor"):
                raise WokuError(
                    "Enrollment pagination did not advance.", code="pagination_error"
                )
            seen.add(cursor)
            query = {**query, "cursor": cursor}

    def get_enrollment(
        self, journey_id: str, enrollment_id: str, options: RequestOptions | None = None
    ) -> JourneyEnrollment:
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
    ) -> JourneyEnrollment:
        """Stop future work for one case, preserving answers and other cases."""
        return self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/enrollments/{quote(enrollment_id, safe='')}/stop"
            ),
            body=body or {},
            options=options,
            idempotent=True,
        )

    def connections(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> list[JourneyConnection]:
        """Read credential readiness, not proof of a real webhook delivery."""
        return self._client.request(
            "get",
            f"/v1/journeys/{quote(journey_id, safe='')}/connections",
            options=options,
        )

    def mint_moment_url(
        self, journey_id: str, stage_key: str, options: RequestOptions | None = None
    ) -> JourneyMomentUrl:
        """Replace this moment's credential URL and return the new URL once."""
        result: JourneyMomentUrl = self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/moments/{quote(stage_key, safe='')}/url-token"
            ),
            body={},
            options=options,
            idempotent=True,
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
            options={**(options or {}), "max_retries": 0},
        )

    def preview_moment(
        self,
        journey_id: str,
        stage_key: str,
        payload: dict[str, Any],
        options: RequestOptions | None = None,
    ) -> JourneyMomentPreview:
        """Interpret a sample with saved mapping without starting or sending."""
        return self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/moments/{quote(stage_key, safe='')}/preview"
            ),
            body={"payload": payload},
            options={**(options or {}), "max_retries": 0},
        )

    def emit_event(
        self, body: JourneyEventParams, options: RequestOptions | None = None
    ) -> EventResult:
        """Emit one of your own events to every journey that listens for it."""
        return self._client.request(
            "post", "/v1/journey-events", body=body, options=options, idempotent=True
        )


class AsyncJourneys:
    """Async twin of :class:`Journeys`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def entry_info(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> JourneyEntryInfo:
        """Read customer entry metadata without starting an evaluation."""
        return await self._client.request(
            "get", f"/v1/journey-entries/{quote(journey_id, safe='')}", options=options
        )

    async def prepare_entry(
        self,
        journey_id: str,
        body: PrepareJourneyEntryInput | BaseModel,
        options: RequestOptions | None = None,
    ) -> PreparedJourneyEntry:
        """Prepare a first tool; its valid saved answer confirms the start."""
        return await self._client.request(
            "post",
            f"/v1/journey-entries/{quote(journey_id, safe='')}",
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    async def list(self, options: RequestOptions | None = None) -> list[Journey]:
        """Every journey of your company."""
        return await self._client.request("get", "/v1/journeys", options=options)

    async def get(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> Journey:
        """One journey with its moments."""
        return await self._client.request(
            "get", f"/v1/journeys/{quote(journey_id, safe='')}", options=options
        )

    async def create(
        self,
        body: JourneyInput | dict[str, Any] | BaseModel,
        options: RequestOptions | None = None,
    ) -> CreatedJourney:
        """Create a journey; the signing secret comes back once, here."""
        return await self._client.request(
            "post", "/v1/journeys", body=body, options=options, idempotent=True
        )

    async def update(
        self,
        journey_id: str,
        body: JourneyInput | dict[str, Any] | BaseModel,
        options: RequestOptions | None = None,
    ) -> Journey:
        """Rename it, switch it on or off, or replace its moments."""
        return await self._client.request(
            "patch",
            f"/v1/journeys/{quote(journey_id, safe='')}",
            body=body,
            options=options,
        )

    async def delete(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> None:
        """Delete a journey."""
        return await self._client.request(
            "delete", f"/v1/journeys/{quote(journey_id, safe='')}", options=options
        )

    async def rotate_webhook_secret(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> JourneySecret:
        """Mint a new signing secret, keeping the previous one valid."""
        return await self._client.request(
            "post",
            f"/v1/journeys/{quote(journey_id, safe='')}/webhook-secret",
            body={},
            options={**(options or {}), "max_retries": 0},
        )

    async def enroll(
        self,
        journey_id: str,
        body: EnrollParams,
        options: RequestOptions | None = None,
    ) -> EnrollmentResult:
        """Start the journey for one subject."""
        return await self._client.request(
            "post",
            f"/v1/journeys/{quote(journey_id, safe='')}/enrollments",
            body=body,
            options=options,
            idempotent=True,
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

    async def iter_enrollments(
        self,
        journey_id: str,
        params: ListEnrollmentsParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[JourneyEnrollment]:
        """Async cursor iterator; advance while preserving caller request options."""
        query = {**dict(params or {}), **dict((options or {}).get("params") or {})}
        seen: set[str] = set()
        while True:
            page = await self.list_enrollments(
                journey_id, options={**(options or {}), "params": query}
            )
            for item in page["items"]:
                yield item
            cursor = page.get("nextCursor")
            if not cursor:
                return
            if cursor in seen or cursor == query.get("cursor"):
                raise WokuError(
                    "Enrollment pagination did not advance.", code="pagination_error"
                )
            seen.add(cursor)
            query = {**query, "cursor": cursor}

    async def get_enrollment(
        self, journey_id: str, enrollment_id: str, options: RequestOptions | None = None
    ) -> JourneyEnrollment:
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
    ) -> JourneyEnrollment:
        """Stop future work for one case, preserving answers and other cases."""
        return await self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/enrollments/{quote(enrollment_id, safe='')}/stop"
            ),
            body=body or {},
            options=options,
            idempotent=True,
        )

    async def connections(
        self, journey_id: str, options: RequestOptions | None = None
    ) -> list[JourneyConnection]:
        """Read credential readiness, not proof of a real webhook delivery."""
        return await self._client.request(
            "get",
            f"/v1/journeys/{quote(journey_id, safe='')}/connections",
            options=options,
        )

    async def mint_moment_url(
        self, journey_id: str, stage_key: str, options: RequestOptions | None = None
    ) -> JourneyMomentUrl:
        """Replace this moment's credential URL and return the new URL once."""
        result: JourneyMomentUrl = await self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/moments/{quote(stage_key, safe='')}/url-token"
            ),
            body={},
            options=options,
            idempotent=True,
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
            options={**(options or {}), "max_retries": 0},
        )

    async def preview_moment(
        self,
        journey_id: str,
        stage_key: str,
        payload: dict[str, Any],
        options: RequestOptions | None = None,
    ) -> JourneyMomentPreview:
        """Interpret a sample with saved mapping without starting or sending."""
        return await self._client.request(
            "post",
            (
                f"/v1/journeys/{quote(journey_id, safe='')}"
                f"/moments/{quote(stage_key, safe='')}/preview"
            ),
            body={"payload": payload},
            options={**(options or {}), "max_retries": 0},
        )

    async def emit_event(
        self, body: JourneyEventParams, options: RequestOptions | None = None
    ) -> EventResult:
        """Emit one of your own events to every journey that listens for it."""
        return await self._client.request(
            "post", "/v1/journey-events", body=body, options=options, idempotent=True
        )
