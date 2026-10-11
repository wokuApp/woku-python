from __future__ import annotations

import inspect
import json
from typing import Any

import httpx
import pytest
import respx

from woku import AsyncWoku, Woku

SPEC = json.load(open("openapi/openapi-v1.json", encoding="utf-8"))

# (resource, method name, args, HTTP method, request path, OpenAPI path)
CASES = [
    ("folders", "list", [], "GET", "/v1/folders", "/v1/folders"),
    ("folders", "get", ["f1"], "GET", "/v1/folders/f1", "/v1/folders/{id}"),
    (
        "folders",
        "create",
        [{"name": "Post-sale"}],
        "POST",
        "/v1/folders",
        "/v1/folders",
    ),
    (
        "folders",
        "update",
        ["f1", {"color": None}],
        "PATCH",
        "/v1/folders/f1",
        "/v1/folders/{id}",
    ),
    (
        "folders",
        "move",
        ["f1", {"parentFolderId": None}],
        "PATCH",
        "/v1/folders/f1/move",
        "/v1/folders/{id}/move",
    ),
    ("folders", "delete", ["f1"], "DELETE", "/v1/folders/f1", "/v1/folders/{id}"),
    (
        "folders",
        "report",
        ["f1", {"lang": "es"}],
        "GET",
        "/v1/folders/f1/report",
        "/v1/folders/{id}/report",
    ),
    ("folders", "csv", ["f1"], "GET", "/v1/folders/f1/csv", "/v1/folders/{id}/csv"),
    (
        "journey_folders",
        "status",
        [],
        "GET",
        "/v1/journey-folders",
        "/v1/journey-folders",
    ),
    (
        "journey_folders",
        "organize",
        [],
        "POST",
        "/v1/journey-folders/organize",
        "/v1/journey-folders/organize",
    ),
    (
        "tools",
        "stats",
        [{"folderId": "f1"}],
        "GET",
        "/v1/tools/stats",
        "/v1/tools/stats",
    ),
    (
        "tools",
        "move",
        [{"items": [{"type": "csat", "id": "t1"}], "folderId": None}],
        "POST",
        "/v1/tools/move",
        "/v1/tools/move",
    ),
    (
        "nps_tools",
        "move",
        ["t1", {"folderId": "f1"}],
        "PATCH",
        "/v1/nps-tools/t1/move",
        "/v1/nps-tools/{id}/move",
    ),
    (
        "csat_tools",
        "move",
        ["t1", {"folderId": None}],
        "PATCH",
        "/v1/csat-tools/t1/move",
        "/v1/csat-tools/{id}/move",
    ),
    (
        "ces_tools",
        "move",
        ["t1", {"folderId": "f1"}],
        "PATCH",
        "/v1/ces-tools/t1/move",
        "/v1/ces-tools/{id}/move",
    ),
]


async def _call(target: Any, name: str, args: list[Any]) -> Any:
    result = getattr(target, name)(*args)
    return await result if inspect.isawaitable(result) else result


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("resource,name,args,method,path,spec_path", CASES)
@respx.mock
async def test_operations_match_the_public_contract(
    resource: str,
    name: str,
    args: list[Any],
    method: str,
    path: str,
    spec_path: str,
    asynchronous: bool,
) -> None:
    assert method.lower() in SPEC["paths"][spec_path]
    route = respx.route(method=method, url=f"https://api.test{path}").mock(
        return_value=httpx.Response(
            200,
            text="a,b" if path.endswith("/csv") else "{}",
        )
    )
    sdk: Any = (AsyncWoku if asynchronous else Woku)(
        api_key="sk_test", base_url="https://api.test"
    )
    try:
        await _call(getattr(sdk, resource), name, args)
        assert route.call_count == 1
        assert route.calls[0].request.headers["authorization"] == "Bearer sk_test"
    finally:
        if asynchronous:
            await sdk.aclose()
        else:
            sdk.close()


@respx.mock
def test_folder_create_is_idempotent_and_csv_returns_text() -> None:
    keys: list[str | None] = []

    def respond(request: httpx.Request) -> httpx.Response:
        keys.append(request.headers.get("x-woku-idempotency-key"))
        return httpx.Response(201, json={"id": "f1"})

    respx.post("https://api.test/v1/folders").mock(side_effect=respond)
    respx.get("https://api.test/v1/folders/f1/csv").mock(
        return_value=httpx.Response(200, text="Carpeta,Tipo\nViajes,NPS")
    )
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        woku.folders.create({"name": "Post-sale"})
        assert keys[0]
        assert woku.folders.csv("f1") == "Carpeta,Tipo\nViajes,NPS"


def _tool(tool_id: str) -> dict[str, Any]:
    return {"type": "csat", "id": tool_id, "name": tool_id, "folderId": None}


@respx.mock
def test_tools_list_joins_types_and_follows_the_cursor() -> None:
    seen: list[dict[str, str]] = []

    def respond(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        seen.append(params)
        if "cursor" not in params:
            return httpx.Response(
                200,
                json={
                    "folders": [{"id": "f1", "name": "Viajes"}],
                    "tools": [_tool("a"), _tool("b")],
                    "nextCursor": "c1",
                    "facets": {"types": {}},
                },
            )
        return httpx.Response(
            200,
            json={
                "folders": [],
                "tools": [_tool("c")],
                "nextCursor": None,
                "facets": {"types": {}},
            },
        )

    respx.get("https://api.test/v1/tools").mock(side_effect=respond)
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        page = woku.tools.list({"folderId": "f1", "types": ["nps", "csat"], "limit": 2})
        assert page.folders[0]["name"] == "Viajes"
        assert [tool["id"] for tool in page] == ["a", "b", "c"]
    assert seen[0]["types"] == "nps,csat"
    assert seen[0]["folderId"] == "f1"
    assert seen[1]["cursor"] == "c1"


@respx.mock
async def test_async_tools_list_iterates_all_pages() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        first = "cursor" not in request.url.params
        return httpx.Response(
            200,
            json={
                "folders": [],
                "tools": [_tool("a")] if first else [_tool("b")],
                "nextCursor": "c1" if first else None,
                "facets": {"types": {}},
            },
        )

    respx.get("https://api.test/v1/tools").mock(side_effect=respond)
    async with AsyncWoku(api_key="sk_test", base_url="https://api.test") as woku:
        page = await woku.tools.list()
        ids = [tool["id"] async for tool in page]
    assert ids == ["a", "b"]


@respx.mock
def test_get_next_page_without_cursor_raises() -> None:
    respx.get("https://api.test/v1/tools").mock(
        return_value=httpx.Response(
            200,
            json={"folders": [], "tools": [], "nextCursor": None, "facets": {}},
        )
    )
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        with pytest.raises(IndexError):
            woku.tools.list().get_next_page()


def test_create_bodies_accept_folder_id_in_the_contract() -> None:
    schemas = SPEC["components"]["schemas"]
    for name in (
        "CreateNpsToolBodyDTO",
        "CreateCsatToolBodyDTO",
        "CreateCesToolBodyDTO",
    ):
        assert "folderId" in schemas[name]["properties"]


@respx.mock
def test_organize_journey_folders_raises_409_while_running() -> None:
    from woku import ConflictError

    respx.post("https://api.test/v1/journey-folders/organize").mock(
        return_value=httpx.Response(409, json={"message": "Already organizing"})
    )
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        with pytest.raises(ConflictError):
            woku.journey_folders.organize()


@respx.mock
def test_journey_status_and_folder_fields() -> None:
    respx.get("https://api.test/v1/journey-folders").mock(
        return_value=httpx.Response(
            200,
            json={
                "enabled": True,
                "enabledAt": None,
                "organizedAt": None,
                "organizing": True,
                "pending": {"journeys": 1, "tools": 5},
            },
        )
    )
    respx.get("https://api.test/v1/journeys").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": "j1",
                    "enabled": True,
                    "version": 1,
                    "moments": [],
                    "folderId": "f1",
                    "momentFolders": {"sale": "f2"},
                }
            ],
        )
    )
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        assert woku.journey_folders.status()["pending"]["tools"] == 5
        journey = woku.journeys.list()[0]
        assert journey["folderId"] == "f1"
        assert journey["momentFolders"]["sale"] == "f2"
