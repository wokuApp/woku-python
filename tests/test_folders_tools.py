from __future__ import annotations

import inspect
import json
from typing import Any

import httpx
import pytest
import respx

from woku import AsyncWoku, Woku, WokuAPIError

SPEC = json.load(open("openapi/openapi-v1.json", encoding="utf-8"))

# (resource, method name, args, HTTP method, request path, OpenAPI path)
CASES = [
    ("folders", "list", [], "GET", "/v1/folders", "/v1/folders"),
    ("folders", "get", ["f1"], "GET", "/v1/folders/f1", "/v1/folders/{id}"),
    (
        "folders",
        "metrics",
        ["f1", {"days": 7}],
        "GET",
        "/v1/folders/f1/metrics",
        "/v1/folders/{id}/metrics",
    ),
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
        [
            "f1",
            {
                "color": None,
                "whatsappAlertRecipients": [
                    {"whatsappId": "56912345678", "name": "Ana"}
                ],
            },
        ],
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
    ("folders", "pdf", ["f1"], "GET", "/v1/folders/f1/pdf", "/v1/folders/{id}/pdf"),
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
    ("flows", "list", [], "GET", "/v1/flows", "/v1/flows"),
    ("flows", "get", ["fl1"], "GET", "/v1/flows/fl1", "/v1/flows/{id}"),
    (
        "flows",
        "create",
        [{"name": "Post-purchase", "steps": [{"type": "csat", "toolId": "c1"}]}],
        "POST",
        "/v1/flows",
        "/v1/flows",
    ),
    (
        "flows",
        "update",
        ["fl1", {"steps": [{"type": "woku", "toolId": "w1"}]}],
        "PATCH",
        "/v1/flows/fl1",
        "/v1/flows/{id}",
    ),
    ("flows", "delete", ["fl1"], "DELETE", "/v1/flows/fl1", "/v1/flows/{id}"),
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


@respx.mock
def test_folder_metrics_sends_the_period_as_days() -> None:
    reply = {
        "days": 0,
        "tools": [],
        "daily": [],
        "distribution": {"woku": [], "nps": [], "csat": [], "ces": []},
    }
    route = respx.get("https://api.test/v1/folders/f1/metrics").mock(
        return_value=httpx.Response(200, json=reply)
    )
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        assert woku.folders.metrics("f1", {"days": 0}) == reply
    assert route.calls[0].request.url.params["days"] == "0"


@respx.mock
def test_tools_list_sends_every_tracker_chip_as_a_repeated_parameter() -> None:
    route = respx.get("https://api.test/v1/tools").mock(
        return_value=httpx.Response(
            200,
            json={
                "folders": [],
                "foldersNextCursor": None,
                "tools": [],
                "nextCursor": None,
                "facets": {"types": {}},
            },
        )
    )
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        woku.tools.list({"trackers": ["TRR:00482", "OC:2024"]})
    assert route.calls[0].request.url.params.get_list("trackers") == [
        "TRR:00482",
        "OC:2024",
    ]


PDF_BYTES = b"%PDF-1.4\x00\xff\xfe binary"


@respx.mock
def test_folder_pdf_returns_raw_bytes_and_asks_for_pdf() -> None:
    route = respx.get("https://api.test/v1/folders/f1/pdf").mock(
        return_value=httpx.Response(
            200, content=PDF_BYTES, headers={"content-type": "application/pdf"}
        )
    )
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        assert woku.folders.pdf("f1", {"lang": "es"}) == PDF_BYTES
    request = route.calls[0].request
    assert request.headers["accept"] == "application/pdf"
    assert request.url.params["lang"] == "es"


@respx.mock
def test_folder_pdf_error_is_an_api_error() -> None:
    respx.get("https://api.test/v1/folders/nope/pdf").mock(
        return_value=httpx.Response(
            404, json={"error": {"message": "Folder not found"}}
        )
    )
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        with pytest.raises(WokuAPIError):
            woku.folders.pdf("nope")


@respx.mock
async def test_async_folder_pdf_returns_raw_bytes() -> None:
    respx.get("https://api.test/v1/folders/f1/pdf").mock(
        return_value=httpx.Response(200, content=PDF_BYTES)
    )
    async with AsyncWoku(api_key="sk_test", base_url="https://api.test") as woku:
        assert await woku.folders.pdf("f1") == PDF_BYTES


@respx.mock
def test_tools_list_pages_the_folders() -> None:
    seen: list[dict[str, str]] = []

    def respond(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        seen.append(params)
        if "foldersCursor" not in params:
            return httpx.Response(
                200,
                json={
                    "folders": [{"id": "f1", "name": "A"}],
                    "foldersNextCursor": "fc1",
                    "tools": [_tool("a")],
                    "nextCursor": "c1",
                    "facets": {"types": {}},
                },
            )
        return httpx.Response(
            200,
            json={
                "folders": [{"id": "f2", "name": "B"}],
                "foldersNextCursor": None,
                "tools": [],
                "nextCursor": None,
                "facets": {"types": {}},
            },
        )

    respx.get("https://api.test/v1/tools").mock(side_effect=respond)
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        page = woku.tools.list({"foldersLimit": 12})
        assert page.has_more_folders()
        more = page.get_more_folders()
        assert [f["id"] for f in more.folders] == ["f2"]
        assert more.tools == []
        assert not more.has_more_folders()
        with pytest.raises(IndexError):
            more.get_more_folders()
    assert seen[0]["foldersLimit"] == "12"
    assert seen[1]["foldersCursor"] == "fc1"
    assert seen[1]["foldersLimit"] == "12"
    assert "cursor" not in seen[1]


@respx.mock
def test_paging_the_tools_does_not_repeat_the_folders_cursor() -> None:
    seen: list[dict[str, str]] = []

    def respond(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        seen.append(params)
        first = "cursor" not in params
        return httpx.Response(
            200,
            json={
                "folders": [],
                "foldersNextCursor": "fc1" if first else None,
                "tools": [_tool("a" if first else "b")],
                "nextCursor": "c1" if first else None,
                "facets": {"types": {}},
            },
        )

    respx.get("https://api.test/v1/tools").mock(side_effect=respond)
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        page = woku.tools.list({"foldersLimit": 5})
        page.get_next_page()
    assert "foldersCursor" not in seen[1]


@respx.mock
async def test_async_tools_list_pages_the_folders() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        first = "foldersCursor" not in request.url.params
        return httpx.Response(
            200,
            json={
                "folders": [{"id": "f1" if first else "f2", "name": "x"}],
                "foldersNextCursor": "fc1" if first else None,
                "tools": [],
                "nextCursor": None,
                "facets": {"types": {}},
            },
        )

    respx.get("https://api.test/v1/tools").mock(side_effect=respond)
    async with AsyncWoku(api_key="sk_test", base_url="https://api.test") as woku:
        page = await woku.tools.list({"foldersLimit": 1})
        more = await page.get_more_folders()
    assert [f["id"] for f in more.folders] == ["f2"]


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


@respx.mock
def test_flow_create_sends_ordered_steps_with_an_idempotency_key() -> None:
    seen: list[tuple[str | None, Any]] = []
    steps = [
        {"type": "nps", "toolId": "n1"},
        {"type": "csat", "toolId": "c1"},
        {"type": "woku", "toolId": "w1"},
    ]

    def respond(request: httpx.Request) -> httpx.Response:
        seen.append(
            (request.headers.get("x-woku-idempotency-key"), json.loads(request.content))
        )
        return httpx.Response(201, json={"_id": "fl1", "name": "A", "steps": steps})

    respx.post("https://api.test/v1/flows").mock(side_effect=respond)
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        flow = woku.flows.create({"name": "A", "steps": steps})
    assert seen[0][0]
    assert seen[0][1] == {"name": "A", "steps": steps}
    assert [step["type"] for step in flow["steps"]] == ["nps", "csat", "woku"]


@pytest.mark.parametrize(
    "dto",
    [
        "CreateNpsToolBodyDTO",
        "UpdateNpsToolBodyDTO",
        "CreateCsatToolBodyDTO",
        "UpdateCsatToolBodyDTO",
        "CreateCesToolBodyDTO",
        "UpdateCesToolBodyDTO",
    ],
)
def test_survey_tool_bodies_accept_the_response_settings(dto: str) -> None:
    properties = SPEC["components"]["schemas"][dto]["properties"]
    assert "anonymousDisabled" in properties
    assert "onlyOneResponsePerClient" in properties


@respx.mock
def test_survey_tool_settings_only_update_and_read_back() -> None:
    seen: list[Any] = []

    def respond(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "_id": "c1",
                "name": "Delivery",
                "question": "q",
                "anonymousDisabled": False,
                "onlyOneResponsePerClient": True,
            },
        )

    respx.patch("https://api.test/v1/csat-tools/c1").mock(side_effect=respond)
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        tool = woku.csat_tools.update("c1", {"onlyOneResponsePerClient": True})
    assert seen == [{"onlyOneResponsePerClient": True}]
    assert tool["onlyOneResponsePerClient"] is True
    assert tool["anonymousDisabled"] is False
