"""Support and plans by folder (folder-voc-routing)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from woku import AsyncWoku, Woku, WokuAPIError

BASE = "https://api.test"


@respx.mock
def test_destinations_and_groups_by_folder() -> None:
    destination = respx.post(f"{BASE}/v1/ticket-destinations").mock(
        return_value=httpx.Response(201, json={"_id": "d1"})
    )
    group = respx.post(f"{BASE}/v1/action-plan-groups").mock(
        return_value=httpx.Response(201, json={"_id": "g1"})
    )
    with Woku(api_key="sk_test", base_url=BASE) as woku:
        woku.ticket_destinations.create(
            {
                "name": "Store support",
                "kind": "email",
                "config": {"emails": ["support@acme.com"]},
                "scopeKind": "folder",
                "folderId": "f1",
            }
        )
        woku.action_plan_groups.create(
            {
                "name": "Stores",
                "scopeKind": "folder",
                "folderId": "f1",
                "members": [{"userId": "u1", "role": "admin"}],
            }
        )
    assert json.loads(destination.calls[0].request.content)["folderId"] == "f1"
    assert json.loads(group.calls[0].request.content)["scopeKind"] == "folder"


@respx.mock
def test_lists_filter_by_folder() -> None:
    destinations = respx.get(f"{BASE}/v1/ticket-destinations").mock(
        return_value=httpx.Response(200, json=[])
    )
    groups = respx.get(f"{BASE}/v1/action-plan-groups").mock(
        return_value=httpx.Response(200, json=[])
    )
    tickets = respx.get(f"{BASE}/v1/tickets").mock(
        return_value=httpx.Response(
            200, json={"data": [], "total": 0, "page": 1, "limit": 20}
        )
    )
    with Woku(api_key="sk_test", base_url=BASE) as woku:
        woku.ticket_destinations.list(params={"folderId": "f1"})
        woku.ticket_destinations.list()
        woku.action_plan_groups.list({"folderId": "f1"})
        list(woku.tickets.list({"folderId": "f1"}))
    assert destinations.calls[0].request.url.params["folderId"] == "f1"
    assert "folderId" not in destinations.calls[1].request.url.params
    assert groups.calls[0].request.url.params["folderId"] == "f1"
    assert tickets.calls[0].request.url.params["folderId"] == "f1"


@respx.mock
@pytest.mark.asyncio
async def test_delete_folder_with_dependents_needs_confirmation() -> None:
    def reply(request: httpx.Request) -> httpx.Response:
        if request.url.params.get("confirmDependents") == "true":
            return httpx.Response(200, json={"deleted": True, "id": "f1"})
        return httpx.Response(
            409,
            json={
                "code": "FOLDER_HAS_DEPENDENTS",
                "message": "Deleting this folder also deletes...",
                "dependents": {"destinations": [], "groups": []},
            },
        )

    respx.delete(f"{BASE}/v1/folders/f1").mock(side_effect=reply)
    async with AsyncWoku(api_key="sk_test", base_url=BASE) as woku:
        with pytest.raises(WokuAPIError) as error:
            await woku.folders.delete("f1")
        assert error.value.status == 409
        assert await woku.folders.delete("f1", confirm_dependents=True) == {
            "deleted": True,
            "id": "f1",
        }
