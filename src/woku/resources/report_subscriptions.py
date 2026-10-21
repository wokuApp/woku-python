"""Reports emailed on a schedule (``/v1/report-subscriptions``).

The PDF of a folder (every tool of its subtree, optionally with the CSV) or of
one tool, monthly, every two weeks, weekly or once, to up to 10 recipients who
need no woku account. Each email goes as the company with a one-click
unsubscribe.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from .._options import RequestOptions
from ..models import DeletedResult, ReportSubscription, ReportSubscriptionSendResult

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku

_BASE = "/v1/report-subscriptions"


def _path(subscription_id: str, suffix: str = "") -> str:
    return f"{_BASE}/{quote(subscription_id, safe='')}{suffix}"


class ReportSubscriptions:
    """Scheduled report emails (sync)."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> list[ReportSubscription]:
        """Every scheduled report, or those of one ``scopeType`` + ``scopeId``."""
        return self._client.request("get", _BASE, query=params, options=options)

    def create(
        self, body: Mapping[str, Any], options: RequestOptions | None = None
    ) -> ReportSubscription:
        """Schedule a report.

        ``body``: ``scopeType`` (``folder``/``woku``/``nps``/``csat``/``ces``),
        ``scopeId``, ``frequency`` (``monthly``/``biweekly``/``weekly``/``once``),
        ``recipients`` (1-10 emails), ``includeCsv`` (folder only), ``locale``,
        and for ``once``: ``periodFrom``/``periodTo`` (ISO, ``to`` exclusive) and
        ``sendAt`` (ISO; omit to send it within minutes).
        """
        return self._client.request("post", _BASE, body=body, options=options)

    def update(
        self,
        subscription_id: str,
        body: Mapping[str, Any],
        options: RequestOptions | None = None,
    ) -> ReportSubscription:
        """Edit a recurring report, or pause (``active: False``) and resume it."""
        return self._client.request(
            "patch", _path(subscription_id), body=body, options=options
        )

    def delete(
        self, subscription_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        return self._client.request("delete", _path(subscription_id), options=options)

    def send(
        self, subscription_id: str, options: RequestOptions | None = None
    ) -> ReportSubscriptionSendResult:
        """Send it now: the last complete period, or a one-off's own period."""
        return self._client.request(
            "post", _path(subscription_id, "/send"), options=options
        )


class AsyncReportSubscriptions:
    """Scheduled report emails (async)."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> list[ReportSubscription]:
        return await self._client.request("get", _BASE, query=params, options=options)

    async def create(
        self, body: Mapping[str, Any], options: RequestOptions | None = None
    ) -> ReportSubscription:
        return await self._client.request("post", _BASE, body=body, options=options)

    async def update(
        self,
        subscription_id: str,
        body: Mapping[str, Any],
        options: RequestOptions | None = None,
    ) -> ReportSubscription:
        return await self._client.request(
            "patch", _path(subscription_id), body=body, options=options
        )

    async def delete(
        self, subscription_id: str, options: RequestOptions | None = None
    ) -> DeletedResult:
        return await self._client.request(
            "delete", _path(subscription_id), options=options
        )

    async def send(
        self, subscription_id: str, options: RequestOptions | None = None
    ) -> ReportSubscriptionSendResult:
        return await self._client.request(
            "post", _path(subscription_id, "/send"), options=options
        )
