"""Data Studio apps: spec, live data, edits, versions and data tables."""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, BinaryIO
from urllib.parse import quote

from .._options import RequestOptions
from .._pagination import AsyncPage, SyncPage
from ..models import (
    DataApp,
    DataAppChange,
    DataAppPublication,
    DataAppQueryResults,
    DataAppTable,
    DataAppView,
)
from ..types import (
    EditDataAppParams,
    PublishDataAppVersionParams,
    RunDataAppQueriesParams,
)

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku


def _app(app_id: str) -> str:
    return f"/v1/data-apps/{quote(app_id, safe='')}"


class DataApps:
    """Every change makes a new version; personal data never comes back."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self, params: dict | None = None, options: RequestOptions | None = None
    ) -> SyncPage[DataApp]:
        return self._client.get_page("/v1/data-apps", params, options)

    def get(
        self,
        app_id: str,
        *,
        version: int | None = None,
        options: RequestOptions | None = None,
    ) -> DataAppView:
        """One version of an app: the current one unless ``version`` is given."""
        query = {"version": version} if version is not None else None
        return self._client.request("get", _app(app_id), query=query, options=options)

    def run_queries(
        self,
        app_id: str,
        body: RunDataAppQueriesParams,
        options: RequestOptions | None = None,
    ) -> DataAppQueryResults:
        """Live results of queries of the app, with filter values."""
        return self._client.request(
            "post", f"{_app(app_id)}/queries", body=body, options=options
        )

    def edit(
        self,
        app_id: str,
        body: EditDataAppParams,
        options: RequestOptions | None = None,
    ) -> DataAppChange:
        """Apply operations on the current version, all or none."""
        return self._client.request(
            "post", f"{_app(app_id)}/operations", body=body, options=options
        )

    def restore(
        self, app_id: str, version: int, options: RequestOptions | None = None
    ) -> DataAppChange:
        """Bring back an earlier version as a new one."""
        return self._client.request(
            "post", f"{_app(app_id)}/versions/{version}/restore", options=options
        )

    def build(
        self, app_id: str, options: RequestOptions | None = None
    ) -> DataAppChange:
        """Build the current sketch with live data."""
        return self._client.request("post", f"{_app(app_id)}/build", options=options)

    def publish(
        self,
        app_id: str,
        version: int,
        body: PublishDataAppVersionParams | None = None,
        options: RequestOptions | None = None,
    ) -> DataAppPublication:
        """Show a version in the shared link; the first time needs ``accessKey``."""
        return self._client.request(
            "post",
            f"{_app(app_id)}/versions/{version}/publish",
            body=body or {},
            options=options,
        )

    def list_tables(
        self, app_id: str, options: RequestOptions | None = None
    ) -> builtins.list[DataAppTable]:
        result = self._client.request("get", f"{_app(app_id)}/tables", options=options)
        return result["data"]

    def upload_table(
        self,
        app_id: str,
        file: bytes | BinaryIO,
        *,
        filename: str,
        content_type: str = "application/octet-stream",
        options: RequestOptions | None = None,
    ) -> DataAppTable:
        """Upload a data file once (CSV, XLSX, JSON or XML).

        The same file name makes a new version of that table.
        """
        return self._client.request(
            "post",
            f"{_app(app_id)}/tables",
            files={"file": (filename, file, content_type)},
            options={**(options or {}), "max_retries": 0},
        )


class AsyncDataApps:
    """Every change makes a new version; personal data never comes back."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self, params: dict | None = None, options: RequestOptions | None = None
    ) -> AsyncPage[DataApp]:
        return await self._client.get_page("/v1/data-apps", params, options)

    async def get(
        self,
        app_id: str,
        *,
        version: int | None = None,
        options: RequestOptions | None = None,
    ) -> DataAppView:
        """One version of an app: the current one unless ``version`` is given."""
        query = {"version": version} if version is not None else None
        return await self._client.request(
            "get", _app(app_id), query=query, options=options
        )

    async def run_queries(
        self,
        app_id: str,
        body: RunDataAppQueriesParams,
        options: RequestOptions | None = None,
    ) -> DataAppQueryResults:
        """Live results of queries of the app, with filter values."""
        return await self._client.request(
            "post", f"{_app(app_id)}/queries", body=body, options=options
        )

    async def edit(
        self,
        app_id: str,
        body: EditDataAppParams,
        options: RequestOptions | None = None,
    ) -> DataAppChange:
        """Apply operations on the current version, all or none."""
        return await self._client.request(
            "post", f"{_app(app_id)}/operations", body=body, options=options
        )

    async def restore(
        self, app_id: str, version: int, options: RequestOptions | None = None
    ) -> DataAppChange:
        """Bring back an earlier version as a new one."""
        return await self._client.request(
            "post", f"{_app(app_id)}/versions/{version}/restore", options=options
        )

    async def build(
        self, app_id: str, options: RequestOptions | None = None
    ) -> DataAppChange:
        """Build the current sketch with live data."""
        return await self._client.request(
            "post", f"{_app(app_id)}/build", options=options
        )

    async def publish(
        self,
        app_id: str,
        version: int,
        body: PublishDataAppVersionParams | None = None,
        options: RequestOptions | None = None,
    ) -> DataAppPublication:
        """Show a version in the shared link; the first time needs ``accessKey``."""
        return await self._client.request(
            "post",
            f"{_app(app_id)}/versions/{version}/publish",
            body=body or {},
            options=options,
        )

    async def list_tables(
        self, app_id: str, options: RequestOptions | None = None
    ) -> builtins.list[DataAppTable]:
        result = await self._client.request(
            "get", f"{_app(app_id)}/tables", options=options
        )
        return result["data"]

    async def upload_table(
        self,
        app_id: str,
        file: bytes | BinaryIO,
        *,
        filename: str,
        content_type: str = "application/octet-stream",
        options: RequestOptions | None = None,
    ) -> DataAppTable:
        """Upload a data file once (CSV, XLSX, JSON or XML).

        The same file name makes a new version of that table.
        """
        return await self._client.request(
            "post",
            f"{_app(app_id)}/tables",
            files={"file": (filename, file, content_type)},
            options={**(options or {}), "max_retries": 0},
        )
