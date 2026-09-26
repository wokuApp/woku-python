from __future__ import annotations

import inspect
import json
from typing import Any

import httpx
import pytest
import respx

from woku import AsyncWoku, InternalServerError, Woku

CASES = [
    ("list", "GET", "/v1/journeys", [], False),
    ("get", "GET", "/v1/journeys/j1", ["j1"], False),
    ("create", "POST", "/v1/journeys", [{"name": "Hybrid"}], True),
    ("update", "PATCH", "/v1/journeys/j1", ["j1", {"enabled": False}], False),
    ("delete", "DELETE", "/v1/journeys/j1", ["j1"], False),
    ("rotate_webhook_secret", "POST", "/v1/journeys/j1/webhook-secret", ["j1"], False),
    (
        "enroll",
        "POST",
        "/v1/journeys/j1/enrollments",
        ["j1", {"email": "client@example.com", "metadata": {"tier": "gold"}}],
        True,
    ),
    (
        "list_enrollments",
        "GET",
        "/v1/journeys/j1/enrollments",
        ["j1", {"limit": 50}],
        False,
    ),
    ("get_enrollment", "GET", "/v1/journeys/j1/enrollments/e1", ["j1", "e1"], False),
    (
        "stop_enrollment",
        "POST",
        "/v1/journeys/j1/enrollments/e1/stop",
        ["j1", "e1", {"reason": "Cancelled"}],
        True,
    ),
    ("connections", "GET", "/v1/journeys/j1/connections", ["j1"], False),
    (
        "mint_moment_url",
        "POST",
        "/v1/journeys/j1/moments/sale/url-token",
        ["j1", "sale"],
        True,
    ),
    (
        "set_sender_secret",
        "POST",
        "/v1/journeys/j1/moments/sale/sender-secret",
        ["j1", "sale", "sender-secret-test"],
        False,
    ),
    (
        "preview_moment",
        "POST",
        "/v1/journeys/j1/moments/sale/preview",
        ["j1", "sale", {"late": True}],
        False,
    ),
    (
        "emit_event",
        "POST",
        "/v1/journey-events",
        [{"name": "delivery", "subjectKey": "case", "metadata": {"late": True}}],
        True,
    ),
    ("entry_info", "GET", "/v1/journey-entries/j1", ["j1"], False),
    (
        "prepare_entry",
        "POST",
        "/v1/journey-entries/j1",
        ["j1", {"email": "client@example.com", "requestId": "request"}],
        False,
    ),
]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("name,method,path,args,protected", CASES)
@respx.mock
async def test_full_journey_contract(
    name: str,
    method: str,
    path: str,
    args: list[Any],
    protected: bool,
    asynchronous: bool,
) -> None:
    keys: list[str | None] = []

    def respond(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer sk_test"
        assert request.headers["x-contract"] == "v4"
        keys.append(request.headers.get("x-woku-idempotency-key"))
        if name == "preview_moment":
            assert json.loads(request.content) == {"payload": {"late": True}}
        return httpx.Response(
            503 if len(keys) == 1 else 200,
            json={"id": "j1", "items": [], "url": "/hook"},
            headers={"Retry-After": "0"},
        )

    route = respx.route(method=method, url=f"https://api.test{path}").mock(
        side_effect=respond
    )
    sdk: Any = (AsyncWoku if asynchronous else Woku)(
        api_key="sk_test", base_url="https://api.test", max_retries=1
    )
    try:

        async def invoke() -> Any:
            result = getattr(sdk.journeys, name)(
                *args, options={"headers": {"x-contract": "v4"}}
            )
            return await result if inspect.isawaitable(result) else result

        if method == "GET" or protected:
            await invoke()
            assert route.call_count == 2
            assert keys[0] == keys[1]
            if protected:
                assert keys[0]
        else:
            with pytest.raises(InternalServerError):
                await invoke()
            assert route.call_count == 1
    finally:
        if asynchronous:
            await sdk.aclose()
        else:
            sdk.close()
