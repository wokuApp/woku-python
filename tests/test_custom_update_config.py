from __future__ import annotations

import json

import httpx
import respx

from woku import Woku
from woku.types import CustomTicketDestinationConfig


@respx.mock
def test_custom_update_config_keeps_typed_contract_on_the_wire() -> None:
    config: CustomTicketDestinationConfig = {
        "url": "https://sac.example.com/tickets",
        "update": {
            "mode": "remote-id",
            "url": "https://sac.example.com/tickets/{{remoteId}}",
            "method": "PATCH",
            "responseIdPath": "result.id",
        },
    }
    route = respx.post("http://api.test/v1/ticket-destinations").mock(
        return_value=httpx.Response(201, json={"_id": "destination_1"})
    )
    with Woku(api_key="sk_test", base_url="http://api.test") as client:
        client.ticket_destinations.create(
            {
                "name": "Support",
                "kind": "custom",
                "config": config,
                "credentials": {"authType": "none"},
            }
        )
    assert json.loads(route.calls.last.request.content)["config"] == config


@respx.mock
def test_generated_custom_update_body_keeps_the_remote_id_placeholder() -> None:
    from woku._generated.models import V1CreateTicketDestinationDto

    body = V1CreateTicketDestinationDto.model_validate(
        {
            "name": "Support",
            "kind": "custom",
            "config": {
                "url": "https://sac.example.com/tickets",
                "update": {
                    "mode": "remote-id",
                    "url": "https://sac.example.com/tickets/{{remoteId}}",
                    "responseIdPath": "result.id",
                },
            },
            "credentials": {"authType": "none"},
        }
    )
    route = respx.post("http://api.test/v1/ticket-destinations").mock(
        return_value=httpx.Response(201, json={"_id": "destination_1"})
    )
    with Woku(api_key="sk_test", base_url="http://api.test") as client:
        client.ticket_destinations.create(body)
    sent = json.loads(route.calls.last.request.content)
    assert (
        sent["config"]["update"]["url"]
        == "https://sac.example.com/tickets/{{remoteId}}"
    )
