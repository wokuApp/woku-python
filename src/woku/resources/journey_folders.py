"""Keep customer journeys in folders (``/v1/journey-folders``).

Layout: ``Viajes > journey > moment``. Each journey and moment exposes its folder
in ``journeys.get`` (``folderId``, ``momentFolders``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .._options import RequestOptions
from ..models import JourneyFoldersStatus

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class JourneyFolders:
    """Journey folder organization (sync)."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def status(self, options: RequestOptions | None = None) -> JourneyFoldersStatus:
        """Whether the organization is on, running, and what is left without a folder."""
        return self._client.request("get", "/v1/journey-folders", options=options)

    def organize(self, options: RequestOptions | None = None) -> JourneyFoldersStatus:
        """Switch the organization on and run the one-off pass in the background.

        Tools of existing journeys without a folder move into their moment folder;
        tools that already have a folder are never touched. Raises a conflict
        error (409) while a pass is already running; poll :meth:`status`.
        """
        return self._client.request(
            "post", "/v1/journey-folders/organize", options=options
        )


class AsyncJourneyFolders:
    """Async twin of :class:`JourneyFolders`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def status(
        self, options: RequestOptions | None = None
    ) -> JourneyFoldersStatus:
        return await self._client.request("get", "/v1/journey-folders", options=options)

    async def organize(
        self, options: RequestOptions | None = None
    ) -> JourneyFoldersStatus:
        return await self._client.request(
            "post", "/v1/journey-folders/organize", options=options
        )
