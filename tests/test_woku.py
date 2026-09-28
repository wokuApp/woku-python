from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from woku import AsyncWoku, PermissionDeniedError, Woku

BASE = "http://api.test"


def woku() -> Woku:
    return Woku(api_key="sk_test", base_url=BASE)


def async_woku() -> AsyncWoku:
    return AsyncWoku(api_key="sk_test", base_url=BASE)


def _body(request: httpx.Request) -> object:
    return json.loads(request.content) if request.content else None


# --- sync facade ------------------------------------------------------------


@respx.mock
def test_trackers_create_posts_with_idempotency_key() -> None:
    route = respx.post(f"{BASE}/v1/external-trackers").mock(
        return_value=httpx.Response(
            200, json={"_id": "trk1", "name": "Store", "system": "retail"}
        )
    )
    tracker = woku().trackers.create({"name": "Store", "system": "retail"})
    assert tracker["_id"] == "trk1"
    request = route.calls.last.request
    assert _body(request) == {"name": "Store", "system": "retail"}
    assert request.headers.get("x-woku-idempotency-key")


@respx.mock
def test_trackers_assign_to_woku_does_not_claim_unsupported_idempotency() -> None:
    route = respx.post(f"{BASE}/v1/external-trackers/wokus/w1").mock(
        return_value=httpx.Response(200, json={"name": "crm", "value": "TX-1"})
    )
    woku().trackers.assign_to_woku("w1", {"name": "crm", "value": "TX-1"})
    assert _body(route.calls.last.request) == {"name": "crm", "value": "TX-1"}
    assert route.calls.last.request.headers.get("x-woku-idempotency-key") is None


@respx.mock
def test_trackers_remove_from_woku_url_encodes_tracker_name() -> None:
    route = respx.delete(f"{BASE}/v1/external-trackers/wokus/w1/crm%20id").mock(
        return_value=httpx.Response(200, json={"deleted": True})
    )
    woku().trackers.remove_from_woku("w1", "crm id")
    assert (
        route.calls.last.request.url.raw_path
        == b"/v1/external-trackers/wokus/w1/crm%20id"
    )


@respx.mock
def test_nps_tools_create_and_get_singular_path() -> None:
    respx.post(f"{BASE}/v1/nps-tools").mock(
        return_value=httpx.Response(200, json={"_id": "nt1", "name": "Survey"})
    )
    respx.get(f"{BASE}/v1/nps-tool/nt1").mock(
        return_value=httpx.Response(200, json={"_id": "nt1", "name": "Survey"})
    )
    created = woku().nps_tools.create({"name": "Survey", "npsMessage": "How likely?"})
    assert created["_id"] == "nt1"
    fetched = woku().nps_tools.get("nt1")
    assert fetched["name"] == "Survey"


@respx.mock
def test_nps_send_invitations_posts_the_exact_wire_body() -> None:
    route = respx.post(f"{BASE}/v1/nps/invitations").mock(
        return_value=httpx.Response(202, json={"accepted": 2, "rejected": 0})
    )
    result = woku().nps.send_invitations(
        {"channel": "email", "npsToolId": "nt1", "recipients": ["a@b.c", "d@e.f"]}
    )
    assert result["accepted"] == 2
    # The server DTO requires channel + string[] recipients; assert the exact
    # shape so a wrong example can never silently reach the wire again.
    assert _body(route.calls.last.request) == {
        "channel": "email",
        "npsToolId": "nt1",
        "recipients": ["a@b.c", "d@e.f"],
    }
    assert route.calls.last.request.headers.get("x-woku-idempotency-key")


@respx.mock
def test_pydantic_model_body_serializes_by_alias_dropping_unset() -> None:
    from woku._generated.models import CreateExternalTrackerDefinitionDTO

    route = respx.post(f"{BASE}/v1/external-trackers").mock(
        return_value=httpx.Response(200, json={"_id": "trk1"})
    )
    # A typed model with an unset optional field must serialize to only the set
    # fields (exclude_unset), matching the dict path.
    woku().trackers.create(
        CreateExternalTrackerDefinitionDTO(name="Store", system="retail")
    )
    assert _body(route.calls.last.request) == {"name": "Store", "system": "retail"}


@respx.mock
def test_ticket_destinations_test_sends_confirm_true() -> None:
    route = respx.post(f"{BASE}/v1/ticket-destinations/d1/test").mock(
        return_value=httpx.Response(200, json={"ok": True, "message": "reachable"})
    )
    out = woku().ticket_destinations.test("d1")
    assert out["ok"] is True
    assert _body(route.calls.last.request) == {"confirm": True}


@respx.mock
def test_action_plans_reply_sends_text_and_confirm() -> None:
    route = respx.post(f"{BASE}/v1/action-plans/p1/conversation").mock(
        return_value=httpx.Response(202, json={"posted": True})
    )
    woku().action_plans.reply("p1", "please refine step 2")
    assert _body(route.calls.last.request) == {
        "text": "please refine step 2",
        "confirm": True,
    }


@respx.mock
def test_tickets_list_paginates_and_auto_iterates() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params.get("page") or 1)
        if page == 1:
            return httpx.Response(
                200,
                json={
                    "data": [{"_id": "a", "title": "A"}],
                    "total": 2,
                    "page": 1,
                    "limit": 1,
                },
            )
        return httpx.Response(
            200,
            json={
                "data": [{"_id": "b", "title": "B"}],
                "total": 2,
                "page": 2,
                "limit": 1,
            },
        )

    respx.get(f"{BASE}/v1/tickets").mock(side_effect=handler)
    ids = [t["_id"] for t in woku().tickets.list({"limit": 1})]
    assert ids == ["a", "b"]


@respx.mock
def test_dispatches_stats_reads_stats_path() -> None:
    route = respx.get(f"{BASE}/v1/dispatches/stats").mock(
        return_value=httpx.Response(
            200, json={"total": 10, "delivered": 8, "responseRate": 0.4}
        )
    )
    stats = woku().dispatches.stats({"channel": "email"})
    assert stats["responseRate"] == 0.4
    assert stats["total"] == 10
    assert route.calls.last.request.url.params.get("channel") == "email"


@respx.mock
def test_move_woku_to_root_sends_explicit_null_folder() -> None:
    route = respx.patch(f"{BASE}/v1/wokus/w1/move").mock(
        return_value=httpx.Response(200, json={"_id": "w1", "folderId": None})
    )
    woku().wokus.move("w1", {"folderId": None})
    assert _body(route.calls.last.request) == {"folderId": None}


# --- async facade -----------------------------------------------------------


@respx.mock
async def test_async_trackers_create_and_tickets_iterate() -> None:
    respx.post(f"{BASE}/v1/external-trackers").mock(
        return_value=httpx.Response(200, json={"_id": "trk1"})
    )

    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params.get("page") or 1)
        if page == 1:
            return httpx.Response(
                200, json={"data": [{"_id": "a"}], "total": 2, "page": 1, "limit": 1}
            )
        return httpx.Response(
            200, json={"data": [{"_id": "b"}], "total": 2, "page": 2, "limit": 1}
        )

    respx.get(f"{BASE}/v1/tickets").mock(side_effect=handler)

    async with async_woku() as w:
        tracker = await w.trackers.create({"name": "Store", "system": "retail"})
        assert tracker["_id"] == "trk1"
        page = await w.tickets.list({"limit": 1})
        ids = [t["_id"] async for t in page]
    assert ids == ["a", "b"]


@respx.mock
async def test_async_reply_sends_text_and_confirm() -> None:
    route = respx.post(f"{BASE}/v1/action-plans/p1/conversation").mock(
        return_value=httpx.Response(202, json={"posted": True})
    )
    async with async_woku() as w:
        await w.action_plans.reply("p1", "hi")
    assert _body(route.calls.last.request) == {"text": "hi", "confirm": True}


@respx.mock
def test_follow_ups_reads_safe_conversation_with_encoded_id_and_options() -> None:
    from woku._generated.models import FollowUpConversationDto

    conversation = {
        "_id": "fu /1",
        "companyId": "c1",
        "origin": {"tool": "nps", "refId": "n1"},
        "reviewType": "textnote",
        "originalReview": "Slow",
        "state": "completed",
        "reason": "summary_generation_failed",
        "channel": "email",
        "messages": [
            {
                "role": "client",
                "content": "Still waiting",
                "timestamp": "2026-09-27T12:00:00Z",
            }
        ],
        "summaryVersion": 1,
    }
    route = respx.get(f"{BASE}/v1/follow-ups/fu%20%2F1").mock(
        return_value=httpx.Response(200, json={"data": conversation})
    )
    out = woku().follow_ups.get("fu /1", {"headers": {"x-request-context": "support"}})
    assert out == conversation
    assert out["reason"] == "summary_generation_failed"
    assert (
        FollowUpConversationDto.model_validate(out).model_dump()["reason"]
        == "summary_generation_failed"
    )
    assert route.calls.last.request.url.raw_path == b"/v1/follow-ups/fu%20%2F1"
    assert route.calls.last.request.headers["authorization"] == "Bearer sk_test"
    assert route.calls.last.request.headers["x-request-context"] == "support"


@respx.mock
async def test_async_follow_ups_reads_safe_conversation() -> None:
    conversation = {
        "_id": "f1",
        "origin": {"tool": "ces", "refId": "e1"},
        "messages": [],
        "state": "pending",
    }
    respx.get(f"{BASE}/v1/follow-ups/f1").mock(
        return_value=httpx.Response(200, json={"data": conversation})
    )
    async with async_woku() as client:
        assert await client.follow_ups.get("f1") == conversation


@pytest.mark.parametrize("asynchronous", [False, True])
@respx.mock
async def test_follow_ups_propagates_forbidden_without_returning_data(
    asynchronous: bool,
) -> None:
    respx.get(f"{BASE}/v1/follow-ups/other-company").mock(
        return_value=httpx.Response(403, json={"message": "Unavailable"})
    )
    if asynchronous:
        async with async_woku() as client:
            with pytest.raises(PermissionDeniedError):
                await client.follow_ups.get("other-company")
    else:
        with woku() as client:
            with pytest.raises(PermissionDeniedError):
                client.follow_ups.get("other-company")


@pytest.mark.parametrize(
    "fixture",
    json.loads((Path(__file__).parent / "fixtures/follow-up.json").read_text()),
)
@respx.mock
async def test_follow_up_semantics_preserved_by_sync_async_ticket_reads(
    fixture: dict[str, Any],
) -> None:
    ticket = fixture["ticket"]
    respx.get(f"{BASE}/v1/tickets/{ticket['_id']}").mock(
        return_value=httpx.Response(200, json=ticket)
    )
    respx.get(f"{BASE}/v1/tickets").mock(
        return_value=httpx.Response(
            200, json={"data": [ticket], "page": 1, "limit": 10, "total": 1}
        )
    )
    with woku() as client:
        detail = client.tickets.get(ticket["_id"])
        page = client.tickets.list()
        assert detail == ticket
        assert page.data == [ticket]
        assert (
            detail.get("followUp", {}).get("appliedSummaryVersion", 0) >= 1
        ) == fixture["enriched"]
    async with async_woku() as client:
        detail = await client.tickets.get(ticket["_id"])
        page = await client.tickets.list()
        assert detail == ticket
        assert page.data == [ticket]
        assert (
            detail.get("followUp", {}).get("appliedSummaryVersion", 0) >= 1
        ) == fixture["enriched"]
