from __future__ import annotations

import json

import httpx
import respx

from woku import AsyncWoku, Woku

BASE = "http://api.test"


@respx.mock
def test_list_and_stop_exact_journey_case() -> None:
    listing = respx.get(f"{BASE}/v1/journeys/j1/enrollments").mock(
        return_value=httpx.Response(
            200, json={"items": [{"id": "case1"}], "nextCursor": "next1"}
        )
    )
    stopping = respx.post(f"{BASE}/v1/journeys/j1/enrollments/case1/stop").mock(
        return_value=httpx.Response(200, json={"id": "case1", "lifecycle": "stopped"})
    )
    with Woku(api_key="sk_test", base_url=BASE) as sdk:
        assert (
            sdk.journeys.list_enrollments("j1", {"cursor": "last1"})["nextCursor"]
            == "next1"
        )
        result = sdk.journeys.stop_enrollment(
            "j1", "case1", {"reason": "Cancelled"}, {"idempotency_key": "stop1"}
        )
    assert result["lifecycle"] == "stopped"
    assert listing.calls.last.request.url.params["cursor"] == "last1"
    assert json.loads(stopping.calls.last.request.content) == {"reason": "Cancelled"}
    assert stopping.calls.last.request.headers["x-woku-idempotency-key"] == "stop1"


@respx.mock
async def test_async_journey_connections_and_case_operations() -> None:
    respx.get(f"{BASE}/v1/journeys/j1/enrollments/case1").mock(
        return_value=httpx.Response(200, json={"id": "case1"})
    )
    respx.get(f"{BASE}/v1/journeys/j1/enrollments").mock(
        return_value=httpx.Response(200, json={"items": []})
    )
    respx.post(f"{BASE}/v1/journeys/j1/enrollments/case1/stop").mock(
        return_value=httpx.Response(200, json={"lifecycle": "stopped"})
    )
    respx.get(f"{BASE}/v1/journeys/j1/connections").mock(
        return_value=httpx.Response(200, json=[])
    )
    respx.post(f"{BASE}/v1/journeys/j1/moments/sale/url-token").mock(
        return_value=httpx.Response(200, json={"url": "/hook"})
    )
    preview = respx.post(f"{BASE}/v1/journeys/j1/moments/sale/preview").mock(
        return_value=httpx.Response(200, json={"subjectKey": "order1"})
    )
    async with AsyncWoku(api_key="sk_test", base_url=BASE) as sdk:
        assert (await sdk.journeys.get_enrollment("j1", "case1"))["id"] == "case1"
        assert (await sdk.journeys.list_enrollments("j1"))["items"] == []
        assert (await sdk.journeys.stop_enrollment("j1", "case1"))[
            "lifecycle"
        ] == "stopped"
        assert await sdk.journeys.connections("j1") == []
        assert (await sdk.journeys.mint_moment_url("j1", "sale"))[
            "url"
        ] == "http://api.test/hook"
        await sdk.journeys.preview_moment("j1", "sale", {"order": "order1"})
    assert json.loads(preview.calls.last.request.content) == {
        "payload": {"order": "order1"}
    }


def test_generated_journey_body_preserves_dynamic_content_and_schema_alias() -> None:
    from woku._generated.models import V1CreateJourneyBodyDto

    moment = {
        "key": "delivery",
        "name": "Delivery",
        "tool": "woku",
        "toolScope": "per_enrollment",
        "enabled": True,
        "channel": "email",
        "trigger": {"type": "webhook"},
        "sequence": {
            "attemptOffsetsMs": [0, 86400000],
            "deadlineMs": 259200000,
            "cooldownAfterResponseMs": 0,
        },
        "webhook": {
            "contentMode": "webhook",
            "schema": {"type": "object", "properties": {"id": {"type": "string"}}},
            "payload": {
                "subjectKey": "id",
                "email": "customer.email",
                "clientFields": [{"key": "tier", "path": "customer.tier"}],
            },
            "content": {
                "description": {
                    "mode": "javascript",
                    "value": "return payload.late ? 'Late delivery' : 'Delivery';",
                },
                "descriptionEn": {"mode": "literal", "value": "Delivery experience"},
                "imageUrlPath": "order.image",
                "trackers": [{"name": "Order", "path": "id"}],
                "folderSecondaryKey": {
                    "mode": "javascript",
                    "value": "return payload.id;",
                },
            },
        },
    }
    model = V1CreateJourneyBodyDto.model_validate(
        {"name": "Hybrid", "moments": [moment]}
    )
    serialized = model.model_dump(mode="json", by_alias=True, exclude_none=True)
    assert serialized["moments"][0] == moment


@respx.mock
def test_prepared_entry_keeps_response_capability_without_enrollment() -> None:
    respx.get(f"{BASE}/v1/journey-entries/j1").mock(
        return_value=httpx.Response(
            200, json={"tool": "woku", "requiresReference": True}
        )
    )
    preparation = respx.post(f"{BASE}/v1/journey-entries/j1").mock(
        return_value=httpx.Response(
            201,
            json={"toolId": "t1", "token": "jent_test", "tool": "woku"},
        )
    )
    with Woku(api_key="sk_test", base_url=BASE) as sdk:
        assert sdk.journeys.entry_info("j1")["requiresReference"] is True
        entry = sdk.journeys.prepare_entry(
            "j1",
            {
                "requestId": "07c19e38-5cf4-4ef5-9e26-88802610c510",
                "email": "client@example.com",
            },
        )
    assert entry["token"] == "jent_test"
    assert "start" not in json.loads(preparation.calls.last.request.content)


@respx.mock
def test_enrollment_iterator_advances_a_query_override() -> None:
    requested: list[str] = []

    def respond(request: httpx.Request) -> httpx.Response:
        cursor = request.url.params.get("cursor", "")
        requested.append(cursor)
        return httpx.Response(
            200,
            json={
                "items": [{"id": cursor}],
                "nextCursor": None if cursor == "second" else "second",
            },
        )

    respx.get(f"{BASE}/v1/journeys/j1/enrollments").mock(side_effect=respond)
    with Woku(api_key="sk_test", base_url=BASE) as sdk:
        results = list(
            sdk.journeys.iter_enrollments(
                "j1", options={"params": {"cursor": "initial"}}
            )
        )
    assert [item["id"] for item in results] == ["initial", "second"]
    assert requested == ["initial", "second"]


@respx.mock
async def test_async_enrollment_iterator_rejects_a_repeated_cursor() -> None:
    import pytest

    from woku import WokuError

    respx.get(f"{BASE}/v1/journeys/j1/enrollments").mock(
        return_value=httpx.Response(200, json={"items": [], "nextCursor": "same"})
    )
    async with AsyncWoku(api_key="sk_test", base_url=BASE) as sdk:
        with pytest.raises(WokuError) as error:
            async for _ in sdk.journeys.iter_enrollments("j1"):
                pass
    assert error.value.code == "pagination_error"
