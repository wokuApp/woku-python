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
    (
        "report_subscriptions",
        "list",
        [{"scopeType": "nps", "scopeId": "n1"}],
        "GET",
        "/v1/report-subscriptions",
        "/v1/report-subscriptions",
    ),
    (
        "report_subscriptions",
        "create",
        [
            {
                "scopeType": "folder",
                "scopeId": "f1",
                "frequency": "monthly",
                "recipients": ["ana@acme.cl"],
            }
        ],
        "POST",
        "/v1/report-subscriptions",
        "/v1/report-subscriptions",
    ),
    (
        "report_subscriptions",
        "update",
        ["s1", {"active": False}],
        "PATCH",
        "/v1/report-subscriptions/s1",
        "/v1/report-subscriptions/{id}",
    ),
    (
        "report_subscriptions",
        "delete",
        ["s1"],
        "DELETE",
        "/v1/report-subscriptions/s1",
        "/v1/report-subscriptions/{id}",
    ),
    (
        "report_subscriptions",
        "send",
        ["s1"],
        "POST",
        "/v1/report-subscriptions/s1/send",
        "/v1/report-subscriptions/{id}/send",
    ),
    (
        "folder_participants",
        "get",
        ["f1"],
        "GET",
        "/v1/folders/f1/participants",
        "/v1/folders/{id}/participants",
    ),
    (
        "folder_participants",
        "replace",
        ["f1", "Ana, ana@acme.cl"],
        "PUT",
        "/v1/folders/f1/participants",
        "/v1/folders/{id}/participants",
    ),
    (
        "folder_participants",
        "add",
        ["f1", "bo@acme.cl"],
        "POST",
        "/v1/folders/f1/participants",
        "/v1/folders/{id}/participants",
    ),
    (
        "folder_participants",
        "remove",
        ["f1", "p1"],
        "DELETE",
        "/v1/folders/f1/participants/p1",
        "/v1/folders/{id}/participants/{participantId}",
    ),
    (
        "folder_participants",
        "clear",
        ["f1"],
        "DELETE",
        "/v1/folders/f1/participants",
        "/v1/folders/{id}/participants",
    ),
    (
        "folder_participants",
        "resend_to_missing",
        ["f1", {"toolType": "nps", "toolId": "n1", "channel": "email"}],
        "POST",
        "/v1/folders/f1/participants/resend",
        "/v1/folders/{id}/participants/resend",
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
        return_value=httpx.Response(200, text="{}")
    )
    sdk: Any = (AsyncWoku if asynchronous else Woku)(
        api_key="sk_test", base_url="https://api.test"
    )
    try:
        await _call(getattr(sdk, resource), name, args)
        assert route.call_count == 1
    finally:
        if asynchronous:
            await sdk.aclose()
        else:
            sdk.close()


@respx.mock
def test_participants_travel_as_the_text_body() -> None:
    route = respx.post("https://api.test/v1/folders/f1/participants").mock(
        return_value=httpx.Response(
            200, json={"count": 1, "total": 3, "invalidLines": [], "duplicates": 0}
        )
    )
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        result = woku.folder_participants.add("f1", "Ana, ana@acme.cl")
    assert result["total"] == 3
    assert json.loads(route.calls[0].request.content) == {"text": "Ana, ana@acme.cl"}


@respx.mock
def test_folder_csv_takes_a_period() -> None:
    route = respx.get("https://api.test/v1/folders/f1/csv").mock(
        return_value=httpx.Response(200, text="a,b")
    )
    with Woku(api_key="sk_test", base_url="https://api.test") as woku:
        assert (
            woku.folders.csv(
                "f1",
                {"from": "2026-09-01T00:00:00.000Z", "to": "2026-10-01T00:00:00.000Z"},
            )
            == "a,b"
        )
    query = route.calls[0].request.url.params
    assert query["from"] == "2026-09-01T00:00:00.000Z"
    assert query["to"] == "2026-10-01T00:00:00.000Z"
