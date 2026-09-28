"""Authorized read-only follow-up conversations."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._options import RequestOptions
from ..models import FollowUpConversation

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class FollowUps:
    def __init__(self, client: Woku) -> None:
        self._client = client

    def get(
        self, conversation_id: str, options: RequestOptions | None = None
    ) -> FollowUpConversation:
        result = self._client.request(
            "get", f"/v1/follow-ups/{quote(conversation_id, safe='')}", options=options
        )
        return result["data"]


class AsyncFollowUps:
    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def get(
        self, conversation_id: str, options: RequestOptions | None = None
    ) -> FollowUpConversation:
        result = await self._client.request(
            "get", f"/v1/follow-ups/{quote(conversation_id, safe='')}", options=options
        )
        return result["data"]
