"""External tracker definitions (``/v1/external-trackers``)."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from .._options import RequestOptions
from .._pagination import AsyncPage, SyncPage
from ..models import EntitiesByTrackers, Tracker
from ..types import (
    CreateTrackerParams,
    SearchEntitiesByTrackersParams,
    UpdateTrackerParams,
)

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class ListTrackersParams(TypedDict, total=False):
    includeInactive: bool
    includeUsage: bool
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
            "get", f"/v1/external-trackers/{tracker_id}", options=options
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
            f"/v1/external-trackers/{tracker_id}",
            body=body,
            options=options,
        )

    def activate(
        self, tracker_id: str, options: RequestOptions | None = None
    ) -> Tracker:
        """Activate a tracker definition."""
        return self._client.request(
            "patch", f"/v1/external-trackers/{tracker_id}/activate", options=options
        )

    def deactivate(
        self, tracker_id: str, options: RequestOptions | None = None
    ) -> Tracker:
        """Deactivate a tracker definition."""
        return self._client.request(
            "patch", f"/v1/external-trackers/{tracker_id}/deactivate", options=options
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
            "get", f"/v1/external-trackers/{tracker_id}", options=options
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
            f"/v1/external-trackers/{tracker_id}",
            body=body,
            options=options,
        )

    async def activate(
        self, tracker_id: str, options: RequestOptions | None = None
    ) -> Tracker:
        """Activate a tracker definition."""
        return await self._client.request(
            "patch", f"/v1/external-trackers/{tracker_id}/activate", options=options
        )

    async def deactivate(
        self, tracker_id: str, options: RequestOptions | None = None
    ) -> Tracker:
        """Deactivate a tracker definition."""
        return await self._client.request(
            "patch", f"/v1/external-trackers/{tracker_id}/deactivate", options=options
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
