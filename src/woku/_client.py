"""The sync (:class:`Woku`) and async (:class:`AsyncWoku`) entry points."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Mapping
from types import TracebackType
from typing import Any

import httpx

from ._base_client import (
    IDEMPOTENCY_HEADER,
    RETRYABLE_STATUS,
    BaseClient,
    clean_query,
    parse_body,
    request_id_from,
    retry_after_from_headers,
    serialize_body,
)
from ._exceptions import WokuAPIError, WokuConnectionError, WokuTimeoutError
from ._options import RequestOptions
from ._pagination import AsyncPage, PageResponse, SyncPage, is_page_response
from .resources.action_plans import (
    ActionPlanGroups,
    ActionPlans,
    AsyncActionPlanGroups,
    AsyncActionPlans,
)
from .resources.company import AsyncCompany, Company
from .resources.dispatches import AsyncDispatches, Dispatches
from .resources.flows import AsyncFlows, Flows
from .resources.forms import AsyncForms, Forms
from .resources.quarantines import AsyncQuarantines, Quarantines
from .resources.reports import AsyncReports, Reports
from .resources.surveys import AsyncCes, AsyncCsat, AsyncNps, Ces, Csat, Nps
from .resources.tickets import (
    AsyncTicketDestinations,
    AsyncTickets,
    TicketDestinations,
    Tickets,
)
from .resources.trackers import AsyncTrackers, Trackers
from .resources.voc_tools import (
    AsyncCesTools,
    AsyncCsatTools,
    AsyncNpsTools,
    CesTools,
    CsatTools,
    NpsTools,
)
from .resources.wokus import AsyncWokus, Wokus


def _as_page_response(response: Any) -> PageResponse:
    if is_page_response(response):
        return response
    items = response if isinstance(response, list) else []
    return {"data": items, "total": len(items), "page": 1, "limit": len(items)}


class Woku(BaseClient):
    """Synchronous entry point to the Woku management API.

    ::

        from woku import Woku

        woku = Woku(api_key="sk_...")
        tracker = woku.trackers.create({"name": "Store", "system": "retail"})
        for ticket in woku.tickets.list({"severity": "high"}):
            print(ticket["title"])
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        default_headers: Mapping[str, str] | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
        )
        self._http = http_client or httpx.Client(base_url=self.base_url)

        self.trackers = Trackers(self)
        self.nps_tools = NpsTools(self)
        self.csat_tools = CsatTools(self)
        self.ces_tools = CesTools(self)
        self.nps = Nps(self)
        self.csat = Csat(self)
        self.ces = Ces(self)
        self.wokus = Wokus(self)
        self.forms = Forms(self)
        self.flows = Flows(self)
        self.action_plans = ActionPlans(self)
        self.action_plan_groups = ActionPlanGroups(self)
        self.tickets = Tickets(self)
        self.ticket_destinations = TicketDestinations(self)
        self.dispatches = Dispatches(self)
        self.reports = Reports(self)
        self.company = Company(self)
        self.quarantines = Quarantines(self)

    def request(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        idempotent: bool = False,
        query: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> Any:
        """Issue one request and return the parsed JSON body."""
        opts: RequestOptions = options or {}
        merged_query = clean_query(
            {**(dict(query) if query else {}), **dict(opts.get("params") or {})}
        )
        idempotency_key = self._resolve_idempotency_key(
            method, idempotent, opts.get("idempotency_key")
        )
        headers = self._build_headers(method, idempotency_key, opts.get("headers"))
        json_body = serialize_body(body)
        max_retries = opts.get("max_retries", self.max_retries)
        timeout = opts.get("timeout", self.timeout)
        retryable = method.upper() == "GET" or IDEMPOTENCY_HEADER in headers

        attempt = 0
        while True:
            try:
                response = self._http.request(
                    method.upper(),
                    path,
                    params=merged_query or None,
                    json=json_body,
                    headers=headers,
                    timeout=timeout,
                )
            except httpx.TimeoutException as exc:
                if retryable and attempt < max_retries:
                    time.sleep(self._backoff(attempt))
                    attempt += 1
                    continue
                raise WokuTimeoutError() from exc
            except httpx.HTTPError as exc:
                if retryable and attempt < max_retries:
                    time.sleep(self._backoff(attempt))
                    attempt += 1
                    continue
                raise WokuConnectionError(str(exc) or "Network request failed") from exc

            status = response.status_code
            if 200 <= status < 300:
                return parse_body(response.text)
            api_error = WokuAPIError.from_response(
                status,
                parse_body(response.text),
                request_id_from(response.headers),
                retry_after_from_headers(response.headers),
            )
            if retryable and attempt < max_retries and status in RETRYABLE_STATUS:
                time.sleep(self._backoff(attempt, api_error))
                attempt += 1
                continue
            raise api_error

    def get_page(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[Any]:
        """Issue a GET that returns a paginated envelope and wrap it in a page."""
        base = dict(params or {})

        def fetch(page_number: int) -> SyncPage[Any]:
            return self.get_page(path, {**base, "page": page_number}, options)

        response = self.request("get", path, query=base, options=options)
        return SyncPage(_as_page_response(response), fetch)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> Woku:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()


class AsyncWoku(BaseClient):
    """Asynchronous twin of :class:`Woku` (awaitable methods, ``async for`` pages).

    ::

        from woku import AsyncWoku

        async with AsyncWoku(api_key="sk_...") as woku:
            tracker = await woku.trackers.create({"name": "Store", "system": "retail"})
            async for ticket in await woku.tickets.list({"severity": "high"}):
                print(ticket["title"])
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        default_headers: Mapping[str, str] | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
        )
        self._http = http_client or httpx.AsyncClient(base_url=self.base_url)

        self.trackers = AsyncTrackers(self)
        self.nps_tools = AsyncNpsTools(self)
        self.csat_tools = AsyncCsatTools(self)
        self.ces_tools = AsyncCesTools(self)
        self.nps = AsyncNps(self)
        self.csat = AsyncCsat(self)
        self.ces = AsyncCes(self)
        self.wokus = AsyncWokus(self)
        self.forms = AsyncForms(self)
        self.flows = AsyncFlows(self)
        self.action_plans = AsyncActionPlans(self)
        self.action_plan_groups = AsyncActionPlanGroups(self)
        self.tickets = AsyncTickets(self)
        self.ticket_destinations = AsyncTicketDestinations(self)
        self.dispatches = AsyncDispatches(self)
        self.reports = AsyncReports(self)
        self.company = AsyncCompany(self)
        self.quarantines = AsyncQuarantines(self)

    async def request(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        idempotent: bool = False,
        query: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> Any:
        """Issue one request and return the parsed JSON body."""
        opts: RequestOptions = options or {}
        merged_query = clean_query(
            {**(dict(query) if query else {}), **dict(opts.get("params") or {})}
        )
        idempotency_key = self._resolve_idempotency_key(
            method, idempotent, opts.get("idempotency_key")
        )
        headers = self._build_headers(method, idempotency_key, opts.get("headers"))
        json_body = serialize_body(body)
        max_retries = opts.get("max_retries", self.max_retries)
        timeout = opts.get("timeout", self.timeout)
        retryable = method.upper() == "GET" or IDEMPOTENCY_HEADER in headers

        attempt = 0
        while True:
            try:
                response = await self._http.request(
                    method.upper(),
                    path,
                    params=merged_query or None,
                    json=json_body,
                    headers=headers,
                    timeout=timeout,
                )
            except httpx.TimeoutException as exc:
                if retryable and attempt < max_retries:
                    await asyncio.sleep(self._backoff(attempt))
                    attempt += 1
                    continue
                raise WokuTimeoutError() from exc
            except httpx.HTTPError as exc:
                if retryable and attempt < max_retries:
                    await asyncio.sleep(self._backoff(attempt))
                    attempt += 1
                    continue
                raise WokuConnectionError(str(exc) or "Network request failed") from exc

            status = response.status_code
            if 200 <= status < 300:
                return parse_body(response.text)
            api_error = WokuAPIError.from_response(
                status,
                parse_body(response.text),
                request_id_from(response.headers),
                retry_after_from_headers(response.headers),
            )
            if retryable and attempt < max_retries and status in RETRYABLE_STATUS:
                await asyncio.sleep(self._backoff(attempt, api_error))
                attempt += 1
                continue
            raise api_error

    async def get_page(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[Any]:
        """Issue a GET that returns a paginated envelope and wrap it in a page."""
        base = dict(params or {})

        async def fetch(page_number: int) -> AsyncPage[Any]:
            return await self.get_page(path, {**base, "page": page_number}, options)

        response = await self.request("get", path, query=base, options=options)
        return AsyncPage(_as_page_response(response), fetch)

    async def aclose(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    async def __aenter__(self) -> AsyncWoku:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()
