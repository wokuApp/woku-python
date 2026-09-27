from __future__ import annotations

import httpx
import pytest
import respx

from woku import (
    AsyncWoku,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
    Woku,
    WokuConnectionError,
    WokuError,
    WokuTimeoutError,
)
from woku._base_client import BaseClient

_REAL_BACKOFF = BaseClient._backoff
BASE = "http://api.test"


def client(**overrides: object) -> Woku:
    kwargs: dict[str, object] = {"max_retries": 2, **overrides}
    return Woku(api_key="sk_test", base_url=BASE, **kwargs)  # type: ignore[arg-type]


def async_client(**overrides: object) -> AsyncWoku:
    kwargs: dict[str, object] = {"max_retries": 2, **overrides}
    return AsyncWoku(api_key="sk_test", base_url=BASE, **kwargs)  # type: ignore[arg-type]


# --- config -----------------------------------------------------------------


def test_missing_api_key_raises() -> None:
    with pytest.raises(WokuError):
        Woku(base_url=BASE)


def test_bare_string_api_key_ok() -> None:
    assert Woku("sk").base_url == "https://clientapi.woku.app"


# --- request / error mapping (sync) -----------------------------------------


@respx.mock
def test_sends_auth_and_user_agent_and_parses_body() -> None:
    route = respx.get(f"{BASE}/v1/thing").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    out = client().request("get", "/v1/thing")
    assert out == {"ok": True}
    request = route.calls.last.request
    assert request.headers["authorization"] == "Bearer sk_test"
    assert "woku-python/" in request.headers["user-agent"]


@respx.mock
def test_maps_404_to_not_found_with_request_id() -> None:
    respx.get(f"{BASE}/v1/thing").mock(
        return_value=httpx.Response(
            404,
            json={"statusCode": 404, "message": "Nope"},
            headers={"x-request-id": "req_abc"},
        )
    )
    with pytest.raises(NotFoundError) as exc:
        client(max_retries=0).request("get", "/v1/thing")
    err = exc.value
    assert err.status == 404
    assert err.request_id == "req_abc"
    assert "Nope" in str(err)
    assert "req_abc" in str(err)


@respx.mock
def test_maps_400_with_joined_validation_messages() -> None:
    respx.post(f"{BASE}/v1/thing").mock(
        return_value=httpx.Response(
            400, json={"statusCode": 400, "message": ["a is bad", "b is bad"]}
        )
    )
    with pytest.raises(BadRequestError) as exc:
        client().request("post", "/v1/thing", body={})
    assert "a is bad, b is bad" in str(exc.value)


@respx.mock
def test_maps_429_reading_retry_after_from_the_header() -> None:
    respx.get(f"{BASE}/v1/thing").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "2"}, json={})
    )
    with pytest.raises(RateLimitError) as exc:
        client(max_retries=0).request("get", "/v1/thing")
    assert exc.value.retry_after_seconds == 2.0


@respx.mock
def test_retry_after_falls_back_to_body_field() -> None:
    respx.get(f"{BASE}/v1/thing").mock(
        return_value=httpx.Response(429, json={"retryAfter": 5})
    )
    with pytest.raises(RateLimitError) as exc:
        client(max_retries=0).request("get", "/v1/thing")
    assert exc.value.retry_after_seconds == 5.0


@respx.mock
def test_maps_every_status_to_its_error_subclass() -> None:
    cases = [
        (401, AuthenticationError),
        (403, PermissionDeniedError),
        (409, ConflictError),
        (422, UnprocessableEntityError),
        (503, InternalServerError),
    ]
    for status, cls in cases:
        respx.get(f"{BASE}/v1/thing").mock(return_value=httpx.Response(status))
        with pytest.raises(cls) as exc:
            client(max_retries=0).request("get", "/v1/thing")
        assert exc.value.status == status  # type: ignore[attr-defined]
        respx.reset()


# --- retries (sync) ---------------------------------------------------------


@respx.mock
def test_retries_get_on_500_then_succeeds() -> None:
    route = respx.get(f"{BASE}/v1/thing").mock(
        side_effect=[
            httpx.Response(500),
            httpx.Response(500),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    out = client().request("get", "/v1/thing")
    assert out == {"ok": True}
    assert route.call_count == 3


@respx.mock
def test_retries_idempotent_create_with_stable_key() -> None:
    keys: set[str] = set()
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        keys.add(request.headers.get("x-woku-idempotency-key", ""))
        if calls["n"] < 2:
            return httpx.Response(503)
        return httpx.Response(201, json={"_id": "t1"})

    respx.post(f"{BASE}/v1/things").mock(side_effect=handler)
    out = client().request("post", "/v1/things", body={"name": "x"}, idempotent=True)
    assert out == {"_id": "t1"}
    assert calls["n"] == 2
    assert len(keys) == 1
    assert "" not in keys


@respx.mock
def test_does_not_retry_non_idempotent_post_on_500() -> None:
    route = respx.post(f"{BASE}/v1/things/send").mock(return_value=httpx.Response(500))
    with pytest.raises(WokuError):
        client().request("post", "/v1/things/send", body={})
    assert route.call_count == 1


@respx.mock
def test_retries_get_on_network_error() -> None:
    route = respx.get(f"{BASE}/v1/thing").mock(
        side_effect=[httpx.ConnectError("boom"), httpx.Response(200, json={"ok": True})]
    )
    out = client().request("get", "/v1/thing")
    assert out == {"ok": True}
    assert route.call_count == 2


@respx.mock
def test_raises_connection_error_after_exhausting_retries() -> None:
    respx.get(f"{BASE}/v1/thing").mock(side_effect=httpx.ConnectError("down"))
    with pytest.raises(WokuConnectionError):
        client(max_retries=1).request("get", "/v1/thing")


@respx.mock
def test_timeout_maps_to_timeout_error() -> None:
    respx.get(f"{BASE}/v1/slow").mock(side_effect=httpx.ReadTimeout("slow"))
    with pytest.raises(WokuTimeoutError):
        client(max_retries=0).request("get", "/v1/slow")


# --- async parity -----------------------------------------------------------


@respx.mock
async def test_async_returns_body_and_maps_error() -> None:
    respx.get(f"{BASE}/v1/thing").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    async with async_client() as woku:
        assert await woku.request("get", "/v1/thing") == {"ok": True}

    respx.get(f"{BASE}/v1/missing").mock(return_value=httpx.Response(404, json={}))
    async with async_client(max_retries=0) as woku:
        with pytest.raises(NotFoundError):
            await woku.request("get", "/v1/missing")


@respx.mock
async def test_async_retries_get_on_500_then_succeeds() -> None:
    route = respx.get(f"{BASE}/v1/thing").mock(
        side_effect=[httpx.Response(503), httpx.Response(200, json={"ok": True})]
    )
    async with async_client() as woku:
        assert await woku.request("get", "/v1/thing") == {"ok": True}
    assert route.call_count == 2


# --- config / headers -------------------------------------------------------


@respx.mock
def test_exhausts_retries_then_raises_mapped_error() -> None:
    route = respx.get(f"{BASE}/v1/thing").mock(return_value=httpx.Response(503))
    with pytest.raises(InternalServerError):
        client(max_retries=2).request("get", "/v1/thing")
    assert route.call_count == 3  # 1 initial + 2 retries


def test_api_key_resolved_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WOKU_API_KEY", "sk_env")
    assert Woku(base_url=BASE).base_url == BASE  # no api_key arg, reads the env


@respx.mock
def test_caller_headers_cannot_unset_authorization() -> None:
    route = respx.get(f"{BASE}/v1/thing").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    client().request(
        "get",
        "/v1/thing",
        options={"headers": {"Authorization": "Bearer HIJACK", "X-Extra": "1"}},
    )
    assert route.calls.last.request.headers["authorization"] == "Bearer sk_test"


@respx.mock
def test_authorization_headers_are_case_insensitive() -> None:
    route = respx.get(f"{BASE}/v1/thing").mock(
        return_value=httpx.Response(200, json={})
    )
    with client(default_headers={"authorization": "default"}) as sdk:
        sdk.request(
            "get", "/v1/thing", options={"headers": {"AUTHORIZATION": "caller"}}
        )
    assert route.calls.last.request.headers.get_list("authorization") == [
        "Bearer sk_test"
    ]


@respx.mock
def test_custom_http_client_cannot_override_the_configured_api_origin() -> None:
    route = respx.get(f"{BASE}/v1/thing").mock(
        return_value=httpx.Response(200, json={})
    )
    with httpx.Client(base_url="https://other.test") as transport:
        with client(http_client=transport) as sdk:
            sdk.request("get", "/v1/thing")
    assert route.call_count == 1


@respx.mock
def test_absolute_api_paths_are_rejected_before_auth_can_leave_the_origin() -> None:
    with client() as sdk:
        for path in ["https://other.test/v1/thing", "//other.test/v1/thing"]:
            with pytest.raises(WokuError) as error:
                sdk.request("get", path)
            assert error.value.code == "config_error"


@respx.mock
def test_long_retry_after_is_not_shortened(monkeypatch: pytest.MonkeyPatch) -> None:
    delays: list[float] = []
    monkeypatch.setattr(BaseClient, "_backoff", _REAL_BACKOFF)
    monkeypatch.setattr("time.sleep", delays.append)
    respx.get(f"{BASE}/v1/thing").mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "10"}),
            httpx.Response(200, json={}),
        ]
    )
    with client() as sdk:
        sdk.request("get", "/v1/thing")
    assert delays == [10.0]


@respx.mock
def test_explicit_idempotency_header_has_one_value_despite_casing() -> None:
    route = respx.post(f"{BASE}/v1/journeys").mock(
        return_value=httpx.Response(200, json={})
    )
    with client() as sdk:
        sdk.request(
            "post",
            "/v1/journeys",
            body={},
            idempotent=True,
            options={
                "idempotency_key": "operation",
                "headers": {"x-woku-idempotency-key": "other"},
            },
        )
    assert route.calls.last.request.headers.get_list("x-woku-idempotency-key") == [
        "operation"
    ]


@respx.mock
def test_nested_api_validation_envelope_retains_details() -> None:
    body = {
        "statusCode": 400,
        "message": {
            "message": ["trigger anchor is required", "invalid moment"],
            "error": "Bad Request",
        },
    }
    respx.post(f"{BASE}/v1/journeys").mock(return_value=httpx.Response(400, json=body))
    with client() as sdk, pytest.raises(BadRequestError) as error:
        sdk.journeys.create({"name": "Invalid"})
    assert "trigger anchor is required, invalid moment" in str(error.value)
    assert error.value.body == body
