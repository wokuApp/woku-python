"""External tracker definitions (``/v1/external-trackers``)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict
from urllib.parse import quote

from .._options import RequestOptions
from .._pagination import AsyncPage, SyncPage
from ..models import EntitiesByTrackers, Tracker, WokuRecord
from ..types import (
    AssignTrackerByNameParams,
    CreateTrackerParams,
    SearchEntitiesByTrackersParams,
    UpdateTrackerParams,
)

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku

#: A VoC entity type that can carry tracker values.
TrackerEntityType = Literal["nps", "csat", "ces", "form", "flow"]


class ListTrackersParams(TypedDict, total=False):
    includeInactive: bool
    includeUsage: bool
    page: int
    limit: int


class SearchWokusByTrackerParams(TypedDict, total=False):
    name: str
    value: str
    page: int
    limit: int


class Trackers:
    """Manage external tracker definitions."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: ListTrackersParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[Tracker]:
        """List the company tracker definitions (paginated)."""
        return self._client.get_page("/v1/external-trackers", params, options)

    def create(
        self, body: CreateTrackerParams, options: RequestOptions | None = None
    ) -> Tracker:
        """Create a tracker definition (idempotent)."""
        return self._client.request(
            "post",
            "/v1/external-trackers",
            body=body,
            idempotent=True,
            options=options,
        )

    def get(self, tracker_id: str, options: RequestOptions | None = None) -> Tracker:
        """Get one tracker definition."""
        return self._client.request(
            "get",
            f"/v1/external-trackers/{quote(tracker_id, safe='')}",
            options=options,
        )

    def update(
        self,
        tracker_id: str,
        body: UpdateTrackerParams,
        options: RequestOptions | None = None,
    ) -> Tracker:
        """Update a tracker definition."""
        return self._client.request(
            "patch",
            f"/v1/external-trackers/{quote(tracker_id, safe='')}",
            body=body,
            options=options,
        )

    def activate(
        self, tracker_id: str, options: RequestOptions | None = None
    ) -> Tracker:
        """Activate a tracker definition."""
        return self._client.request(
            "patch",
            f"/v1/external-trackers/{quote(tracker_id, safe='')}/activate",
            options=options,
        )

    def deactivate(
        self, tracker_id: str, options: RequestOptions | None = None
    ) -> Tracker:
        """Deactivate a tracker definition."""
        return self._client.request(
            "patch",
            f"/v1/external-trackers/{quote(tracker_id, safe='')}/deactivate",
            options=options,
        )

    def search_entities(
        self,
        body: SearchEntitiesByTrackersParams,
        options: RequestOptions | None = None,
    ) -> EntitiesByTrackers:
        """Search VoC entities whose trackers match every filter (AND)."""
        return self._client.request(
            "post",
            "/v1/external-trackers/search-entities",
            body=body,
            options=options,
        )

    def list_woku_values(
        self, woku_id: str, options: RequestOptions | None = None
    ) -> list[WokuRecord]:
        """List the tracker values assigned to a woku."""
        return self._client.request(
            "get",
            f"/v1/external-trackers/wokus/{quote(woku_id, safe='')}",
            options=options,
        )

    def assign_to_woku(
        self,
        woku_id: str,
        body: AssignTrackerByNameParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Assign (upsert) a tracker value to a woku by tracker name."""
        return self._client.request(
            "post",
            f"/v1/external-trackers/wokus/{quote(woku_id, safe='')}",
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    def remove_from_woku(
        self,
        woku_id: str,
        tracker_name: str,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Remove a tracker value from a woku by tracker name."""
        return self._client.request(
            "delete",
            (
                f"/v1/external-trackers/wokus/{quote(woku_id, safe='')}"
                f"/{quote(tracker_name, safe='')}"
            ),
            options=options,
        )

    def search_wokus(
        self,
        params: SearchWokusByTrackerParams,
        options: RequestOptions | None = None,
    ) -> SyncPage[WokuRecord]:
        """Search wokus by an exact (tracker name, value) pair (paginated)."""
        return self._client.get_page("/v1/external-trackers/search", params, options)

    def list_entity_values(
        self,
        entity_type: TrackerEntityType,
        entity_id: str,
        options: RequestOptions | None = None,
    ) -> list[WokuRecord]:
        """List the tracker values assigned to a VoC entity."""
        return self._client.request(
            "get",
            (
                f"/v1/external-trackers/{quote(entity_type, safe='')}"
                f"/{quote(entity_id, safe='')}"
            ),
            options=options,
        )

    def assign_to_entity(
        self,
        entity_type: TrackerEntityType,
        entity_id: str,
        body: AssignTrackerByNameParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Assign (upsert) a tracker value to a VoC entity by tracker name."""
        return self._client.request(
            "post",
            (
                f"/v1/external-trackers/{quote(entity_type, safe='')}"
                f"/{quote(entity_id, safe='')}"
            ),
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    def remove_from_entity(
        self,
        entity_type: TrackerEntityType,
        entity_id: str,
        tracker_name: str,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Remove a tracker value from a VoC entity by tracker name."""
        return self._client.request(
            "delete",
            f"/v1/external-trackers/{quote(entity_type, safe='')}"
            f"/{quote(entity_id, safe='')}"
            f"/{quote(tracker_name, safe='')}",
            options=options,
        )


class AsyncTrackers:
    """Async twin of :class:`Trackers`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: ListTrackersParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[Tracker]:
        """List the company tracker definitions (paginated)."""
        return await self._client.get_page("/v1/external-trackers", params, options)

    async def create(
        self, body: CreateTrackerParams, options: RequestOptions | None = None
    ) -> Tracker:
        """Create a tracker definition (idempotent)."""
        return await self._client.request(
            "post",
            "/v1/external-trackers",
            body=body,
            idempotent=True,
            options=options,
        )

    async def get(
        self, tracker_id: str, options: RequestOptions | None = None
    ) -> Tracker:
        """Get one tracker definition."""
        return await self._client.request(
            "get",
            f"/v1/external-trackers/{quote(tracker_id, safe='')}",
            options=options,
        )

    async def update(
        self,
        tracker_id: str,
        body: UpdateTrackerParams,
        options: RequestOptions | None = None,
    ) -> Tracker:
        """Update a tracker definition."""
        return await self._client.request(
            "patch",
            f"/v1/external-trackers/{quote(tracker_id, safe='')}",
            body=body,
            options=options,
        )

    async def activate(
        self, tracker_id: str, options: RequestOptions | None = None
    ) -> Tracker:
        """Activate a tracker definition."""
        return await self._client.request(
            "patch",
            f"/v1/external-trackers/{quote(tracker_id, safe='')}/activate",
            options=options,
        )

    async def deactivate(
        self, tracker_id: str, options: RequestOptions | None = None
    ) -> Tracker:
        """Deactivate a tracker definition."""
        return await self._client.request(
            "patch",
            f"/v1/external-trackers/{quote(tracker_id, safe='')}/deactivate",
            options=options,
        )

    async def search_entities(
        self,
        body: SearchEntitiesByTrackersParams,
        options: RequestOptions | None = None,
    ) -> EntitiesByTrackers:
        """Search VoC entities whose trackers match every filter (AND)."""
        return await self._client.request(
            "post",
            "/v1/external-trackers/search-entities",
            body=body,
            options=options,
        )

    async def list_woku_values(
        self, woku_id: str, options: RequestOptions | None = None
    ) -> list[WokuRecord]:
        """List the tracker values assigned to a woku."""
        return await self._client.request(
            "get",
            f"/v1/external-trackers/wokus/{quote(woku_id, safe='')}",
            options=options,
        )

    async def assign_to_woku(
        self,
        woku_id: str,
        body: AssignTrackerByNameParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Assign (upsert) a tracker value to a woku by tracker name."""
        return await self._client.request(
            "post",
            f"/v1/external-trackers/wokus/{quote(woku_id, safe='')}",
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    async def remove_from_woku(
        self,
        woku_id: str,
        tracker_name: str,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Remove a tracker value from a woku by tracker name."""
        return await self._client.request(
            "delete",
            (
                f"/v1/external-trackers/wokus/{quote(woku_id, safe='')}"
                f"/{quote(tracker_name, safe='')}"
            ),
            options=options,
        )

    async def search_wokus(
        self,
        params: SearchWokusByTrackerParams,
        options: RequestOptions | None = None,
    ) -> AsyncPage[WokuRecord]:
        """Search wokus by an exact (tracker name, value) pair (paginated)."""
        return await self._client.get_page(
            "/v1/external-trackers/search", params, options
        )

    async def list_entity_values(
        self,
        entity_type: TrackerEntityType,
        entity_id: str,
        options: RequestOptions | None = None,
    ) -> list[WokuRecord]:
        """List the tracker values assigned to a VoC entity."""
        return await self._client.request(
            "get",
            (
                f"/v1/external-trackers/{quote(entity_type, safe='')}"
                f"/{quote(entity_id, safe='')}"
            ),
            options=options,
        )

    async def assign_to_entity(
        self,
        entity_type: TrackerEntityType,
        entity_id: str,
        body: AssignTrackerByNameParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Assign (upsert) a tracker value to a VoC entity by tracker name."""
        return await self._client.request(
            "post",
            (
                f"/v1/external-trackers/{quote(entity_type, safe='')}"
                f"/{quote(entity_id, safe='')}"
            ),
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    async def remove_from_entity(
        self,
        entity_type: TrackerEntityType,
        entity_id: str,
        tracker_name: str,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Remove a tracker value from a VoC entity by tracker name."""
        return await self._client.request(
            "delete",
            f"/v1/external-trackers/{quote(entity_type, safe='')}"
            f"/{quote(entity_id, safe='')}"
            f"/{quote(tracker_name, safe='')}",
            options=options,
        )
