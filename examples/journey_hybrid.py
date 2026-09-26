"""Prepare a disabled four-moment journey; never enroll or send from this example."""

from __future__ import annotations

from pathlib import Path
from time import time
from typing import Any

from woku import Woku
from woku._generated.models import V1CreateJourneyBodyDto

DAY = 86_400_000


def prepare_hybrid_journey(sdk: Woku, image_path: Path) -> str:
    with image_path.open("rb") as image:
        media = sdk.media.upload(
            image, filename=image_path.name, content_type="image/jpeg"
        )
    defaults: dict[str, Any] = {
        "enabled": True,
        "toolScope": "shared",
        "channel": "email",
        "sequence": {
            "attemptOffsetsMs": [0, DAY],
            "deadlineMs": 3 * DAY,
            "cooldownAfterResponseMs": 0,
        },
    }
    moments = [
        {
            **defaults,
            "key": "sale",
            "name": "Purchase",
            "tool": "csat",
            "trigger": {"type": "manual"},
            "toolSpec": {"subject": {"es": "la compra", "en": "the purchase"}},
        },
        {
            **defaults,
            "key": "delivery",
            "name": "Delivery",
            "tool": "woku",
            "toolScope": "per_enrollment",
            "trigger": {"type": "webhook"},
            "description": "Delivery experience",
            "toolSpec": {
                "descriptionEn": "Delivery experience",
                "fileId": media["fileId"],
            },
            "fallbackFromStage": "sale",
            "fallbackAfterMs": 10 * DAY,
            "webhook": {
                "contentMode": "webhook",
                "verification": {"mode": "url_token"},
                "schema": {
                    "type": "object",
                    "properties": {
                        "order": {"type": "string"},
                        "late": {"type": "boolean"},
                        "email": {"type": "string"},
                    },
                },
                "payload": {"subjectKey": "order", "email": "email"},
                "content": {
                    "description": {
                        "mode": "javascript",
                        "value": (
                            "return payload.late ? 'Delayed delivery' "
                            ": 'Delivery experience';"
                        ),
                    },
                    "descriptionEn": {
                        "mode": "literal",
                        "value": "Delivery experience",
                    },
                },
            },
        },
        {
            **defaults,
            "key": "use",
            "name": "Product use",
            "tool": "ces",
            "trigger": {
                "type": "afterStage",
                "anchor": "sent",
                "stage": "delivery",
                "delayMs": 10 * DAY,
            },
            "toolSpec": {
                "subject": {"es": "usar el producto", "en": "using the product"}
            },
        },
        {
            **defaults,
            "key": "loyalty",
            "name": "Recommendation",
            "tool": "nps",
            "trigger": {
                "type": "afterStage",
                "anchor": "sent",
                "stage": "use",
                "delayMs": 10 * DAY,
            },
            "toolSpec": {"audience": {"es": "esta empresa", "en": "this business"}},
        },
    ]
    body = V1CreateJourneyBodyDto.model_validate(
        {
            "name": f"Hybrid Python SDK {int(time())}",
            "authoringVersion": 2,
            "startMode": "operator",
            "enabled": False,
            "moments": moments,
            "recipients": {
                "ticketsEnabled": False,
                "plansEnabled": False,
                "ticketEmails": [],
                "planMembers": [],
            },
        }
    )
    created = sdk.journeys.create(body)
    sdk.journeys.preview_moment(
        created["id"],
        "delivery",
        {"order": "order-123", "late": True, "email": "client@example.com"},
    )
    return created["id"]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    arguments = parser.parse_args()
    with Woku() as woku:
        print(prepare_hybrid_journey(woku, arguments.image))
