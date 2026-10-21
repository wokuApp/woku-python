"""The participant list of a folder (``/v1/folders/{id}/participants``).

The people expected to answer the tools of a folder and its subfolders, and
who of them did. The list is text, one person per line with a name, an email
and/or a phone (with its country code), separated by commas, semicolons or
tabs; a CSV goes as is. Up to 500 people. Only identified responses can be
matched, so each tool says whether it takes anonymous ones.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from .._options import RequestOptions
from ..models import FolderParticipation, ParticipantsSaveResult, ResendToMissingResult

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


def _path(folder_id: str, suffix: str = "") -> str:
    return f"/v1/folders/{quote(folder_id, safe='')}/participants{suffix}"


class FolderParticipants:
    """Folder participant lists (sync)."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def get(
        self, folder_id: str, options: RequestOptions | None = None
    ) -> FolderParticipation:
        """The list and, per tool of the folder subtree, who answered."""
        return self._client.request("get", _path(folder_id), options=options)

    def replace(
        self, folder_id: str, text: str, options: RequestOptions | None = None
    ) -> ParticipantsSaveResult:
        """Replace the whole list."""
        return self._client.request(
            "put", _path(folder_id), body={"text": text}, options=options
        )

    def add(
        self, folder_id: str, text: str, options: RequestOptions | None = None
    ) -> ParticipantsSaveResult:
        """Add people; the ones already on the list are skipped."""
        return self._client.request(
            "post", _path(folder_id), body={"text": text}, options=options
        )

    def remove(
        self,
        folder_id: str,
        participant_id: str,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        """Remove one person (the ``id`` from ``get``)."""
        return self._client.request(
            "delete",
            _path(folder_id, f"/{quote(participant_id, safe='')}"),
            options=options,
        )

    def clear(
        self, folder_id: str, options: RequestOptions | None = None
    ) -> dict[str, Any]:
        """Delete the whole list. Responses are never touched."""
        return self._client.request("delete", _path(folder_id), options=options)

    def resend_to_missing(
        self,
        folder_id: str,
        body: Mapping[str, Any],
        options: RequestOptions | None = None,
    ) -> ResendToMissingResult:
        """Send a tool again to the people of the list who have not answered it.

        ``body``: ``toolType``, ``toolId``, ``channel`` (``email``/``whatsapp``)
        and optional ``language``.
        """
        return self._client.request(
            "post", _path(folder_id, "/resend"), body=body, options=options
        )


class AsyncFolderParticipants:
    """Folder participant lists (async)."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def get(
        self, folder_id: str, options: RequestOptions | None = None
    ) -> FolderParticipation:
        return await self._client.request("get", _path(folder_id), options=options)

    async def replace(
        self, folder_id: str, text: str, options: RequestOptions | None = None
    ) -> ParticipantsSaveResult:
        return await self._client.request(
            "put", _path(folder_id), body={"text": text}, options=options
        )

    async def add(
        self, folder_id: str, text: str, options: RequestOptions | None = None
    ) -> ParticipantsSaveResult:
        return await self._client.request(
            "post", _path(folder_id), body={"text": text}, options=options
        )

    async def remove(
        self,
        folder_id: str,
        participant_id: str,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        return await self._client.request(
            "delete",
            _path(folder_id, f"/{quote(participant_id, safe='')}"),
            options=options,
        )

    async def clear(
        self, folder_id: str, options: RequestOptions | None = None
    ) -> dict[str, Any]:
        return await self._client.request("delete", _path(folder_id), options=options)

    async def resend_to_missing(
        self,
        folder_id: str,
        body: Mapping[str, Any],
        options: RequestOptions | None = None,
    ) -> ResendToMissingResult:
        return await self._client.request(
            "post", _path(folder_id, "/resend"), body=body, options=options
        )
