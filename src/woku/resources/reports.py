"""Read NPS reports (``/v1/reports``)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from .._options import RequestOptions
from ..models import WokuRecord

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


class Reports:
    """Read NPS reports."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def company_nps(
        self,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Company-level NPS report."""
        return self._client.request(
            "get", "/v1/reports/company-nps", query=params, options=options
        )

    def nps_tool(
        self,
        nps_tool_id: str,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """NPS report for one tool."""
        return self._client.request(
            "get",
            f"/v1/reports/nps-tool/{quote(nps_tool_id, safe='')}",
            query=params,
            options=options,
        )


class AsyncReports:
    """Async twin of :class:`Reports`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def company_nps(
        self,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """Company-level NPS report."""
        return await self._client.request(
            "get", "/v1/reports/company-nps", query=params, options=options
        )

    async def nps_tool(
        self,
        nps_tool_id: str,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        """NPS report for one tool."""
        return await self._client.request(
            "get",
            f"/v1/reports/nps-tool/{quote(nps_tool_id, safe='')}",
            query=params,
            options=options,
        )
