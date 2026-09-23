<div align="center">

# woku

Official **server-side** SDK for the [Woku](https://woku.app) management API.

[![PyPI](https://img.shields.io/pypi/v/woku)](https://pypi.org/project/woku/)
[![Python](https://img.shields.io/pypi/pyversions/woku)](https://pypi.org/project/woku/)
[![License](https://img.shields.io/pypi/l/woku)](./LICENSE)

</div>

## Why

Manage your entire Woku account from your backend with one typed client:
trackers, VoC tools (NPS/CSAT/CES), wokus, forms, flows, action plans,
support tickets, delivery tracking and survey sends over the public `/v1` API.

- **Sync and async** clients (`Woku` / `AsyncWoku`) on top of `httpx`.
- **Typed** request bodies (Pydantic v2 models generated from the OpenAPI spec)
  and response shapes.
- **Automatic retries** with full-jitter backoff and `Retry-After` support.
- **Idempotent creates**: creates carry an auto-generated `Idempotency-Key`, so
  a retry after a blip never creates twice. Action calls (`send`, `test`,
  `reply`) are never silently replayed.
- **Auto-paginated** lists: `for ticket in woku.tickets.list(): ...`.
- **Typed errors** with the server `request_id` for support.

> **Server-only.** The secret key grants full management access. Keep it on your
> backend, never in a browser, mobile app or other client you do not control.

## Install

```bash
pip install woku
# or: uv add woku
```

Requires Python 3.9+.

## Quickstart

```python
from woku import Woku

woku = Woku(api_key="sk_...")  # or set WOKU_API_KEY and call Woku()

# Create a tracker definition (idempotent).
tracker = woku.trackers.create({"name": "Store #1", "system": "retail"})

# Create an NPS tool.
tool = woku.nps_tools.create(
    {"name": "Post-purchase", "npsMessage": "How likely are you to recommend us?"}
)

# Tag the NPS tool with the tracker, so every response is grouped by store.
woku.trackers.assign_to_entity(
    "nps", tool["_id"], {"name": tracker["name"], "value": "TX-42"}
)

# Send it, then read delivery + response rate.
woku.nps.send_invitations(
    {"channel": "email", "npsToolId": tool["_id"], "recipients": ["ana@example.com"]}
)

stats = woku.dispatches.stats({"channel": "email"})
print(stats["responseRate"])
```

The key is read from `WOKU_API_KEY` when you omit `api_key`. You can also pass
it directly: `Woku("sk_...")`.

Request bodies accept either a plain dict (as above) or a generated Pydantic
model from `woku._generated.models`.

### Customer journeys

Set `authoringVersion: 2` and choose `startMode`: `operator` starts from the
platform/API without requiring the first answer; `response` starts only when the
customer answers the first tool through a QR/shared link; `webhook` starts from an
external system. Only operator mode uses `enroll`. Later moments use waits or their
own webhooks. A webhook advances its moment and cancels the wait. An optional
secondary fallback evaluates the same webhook-primary moment once.

Each moment owns its CSAT, CES, NPS or woku tool. Choose `toolScope` as
`per_enrollment` or `shared` within that moment and configuration. Existing tools
cannot be assigned. Woku needs an uploaded `toolSpec.fileId`; other instruments
use question variables. This example uses one initial send and no reminders.
For a bilingual Woku, set `toolSpec.descriptionEn` to its English title.

```python
import httpx

DAY = 86_400_000
sequence = {"attemptOffsetsMs": [0], "deadlineMs": 3 * DAY, "cooldownAfterResponseMs": 0}
journey = woku.journeys.create({
    "name": "Purchase and delivery",
    "authoringVersion": 2,
    "startMode": "webhook",
    "recipients": {
        "ticketsEnabled": True,
        "plansEnabled": True,
        "ticketEmails": ["support@example.com"],
        "planMembers": [
            {"userId": "507f1f77bcf86cd799439011", "role": "admin"},
            {"userId": "507f1f77bcf86cd799439012", "role": "assignee"},
        ],
    },
    "moments": [
        {
            "key": "sale", "name": "Purchase", "tool": "csat", "enabled": True,
            "channel": "email", "trigger": {"type": "webhook"},
            "webhook": {"verification": {"mode": "url_token"}},
            "toolSpec": {"subject": {"es": "tu compra", "en": "your purchase"}},
            "sequence": sequence,
        },
        {
            "key": "delivery", "name": "Delivery", "tool": "ces", "enabled": True,
            "channel": "email", "trigger": {"type": "webhook"},
            "webhook": {"verification": {"mode": "url_token"}},
            "fallbackFromStage": "sale", "fallbackAfterMs": 5 * DAY,
            "toolSpec": {"subject": {"es": "recibir tu pedido", "en": "receiving your order"}},
            "sequence": sequence,
        },
    ],
})

# Generate once and securely store each URL in its sending system.
# Generating again replaces the previous moment credential.
sale = woku.journeys.mint_moment_url(journey["id"], "sale")
delivery = woku.journeys.mint_moment_url(journey["id"], "delivery")
woku.journeys.update(journey["id"], {"enabled": True})

# Different systems share the same purchase reference.
httpx.post(sale["url"], headers={"X-Woku-Event-Id": "crm-order-123"}, json={
    "subjectKey": "order-123", "contact": {"email": "customer@example.com"},
}).raise_for_status()
httpx.post(delivery["url"], headers={"X-Woku-Event-Id": "delivery-order-123"}, json={
    "subjectKey": "order-123",
}).raise_for_status()

page = woku.journeys.list_enrollments(journey["id"], {"limit": 20})
case = next((
    item for item in page["items"]
    if item["subjectKey"] == "order-123"
    and item.get("lifecycle") in ("pending", "running")
), None)
if case:
    woku.journeys.stop_enrollment(journey["id"], case["id"], {
        "reason": "Customer requested no further evaluations",
    }, {"idempotency_key": f"stop-{case['id']}"})
```

`get_enrollment` reads a specific case. Enrollment lists return `{items, nextCursor}`;
pass `nextCursor` as the next request's `cursor`. `connections` reports credential
readiness, `set_sender_secret` configures an external signing secret, and
`preview_moment` tests saved payload mapping without starting or sending.
All methods have matching `AsyncWoku` variants.

Stop preserves answers, tickets, plans, shared tools and other cases. Messages
already accepted by their provider may arrive. `stopping` means cleanup is still
in progress; `dispatchOutcomeUncertain` marks an interrupted in-flight send.

An enrollment reports `pendingMoments` for tools not yet sent and `completed`
when the customer answers the final tool or 30 days pass after its first send.
The same `subjectKey` may enter a new cycle after completion or stopping; each
cycle has a distinct enrollment `id`. Only one cycle for that key may be in
progress in the same journey.

Ticket and plan recipients are independent; adding a plan email grants no role.
Set `recipients.ticketsEnabled` or `recipients.plansEnabled` to `False` to stop
that action independently. Both default to enabled when omitted. Disabled
actions do not require completed recipients, and saved settings remain for
later reactivation.
Existing journeys keep their execution contract. Create a new v2 journey to adopt
these rules, and review/activate it after its recipients and connections are ready.

## Async

```python
import asyncio
from woku import AsyncWoku


async def main() -> None:
    async with AsyncWoku(api_key="sk_...") as woku:
        async for ticket in await woku.tickets.list({"severity": "high"}):
            print(ticket["title"])


asyncio.run(main())
```

## Pagination

List methods return a page you can iterate item by item across pages, or walk
page by page:

```python
for ticket in woku.tickets.list({"severity": "high"}):
    print(ticket["title"])

first = woku.dispatches.list({"channel": "whatsapp"})
if first.has_next_page():
    second = first.get_next_page()
```

## Errors

Every failure is a `WokuError`. HTTP errors are typed subclasses carrying the
status, parsed body and `request_id`:

```python
from woku import NotFoundError, RateLimitError

try:
    woku.tickets.get("nonexistent")
except NotFoundError as err:
    print(err.status, err.request_id)  # 404, "req_..."
except RateLimitError as err:
    print("retry after", err.retry_after_seconds)
```

Transport failures (DNS/TLS/timeout) are `WokuConnectionError` /
`WokuTimeoutError`.

## Configuration

```python
Woku(
    api_key="sk_...",
    base_url="https://clientapi.woku.app",  # default
    timeout=60.0,  # seconds, default
    max_retries=2,  # default
)
```

Per-call overrides go in the `options` argument of any method:

```python
woku.tickets.list({"severity": "high"}, options={"timeout": 10.0, "max_retries": 0})
woku.nps_tools.create(body, options={"idempotency_key": "my-key"})
```

## Resources

`trackers`, `nps_tools` / `csat_tools` / `ces_tools`, `nps` / `csat` / `ces`,
`wokus`, `forms`, `flows`, `action_plans`, `action_plan_groups`, `tickets`,
`ticket_destinations`, `dispatches`, `reports`, `company`, `quarantines`,
`journeys`.

## License

MIT
