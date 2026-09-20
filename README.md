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

Custom moments create CSAT, CES, NPS, or woku tools. `toolScope` defaults to
`"per_enrollment"`; `"shared"` reuses a tool only for that same moment and tool
configuration. Existing tools cannot be assigned. Woku moments require
`toolSpec.fileId` from an upload and use the moment name as their title.

Define the moments where you listen, create a tool for each customer or share
one within the same moment, and set them off by hand or from your own events.

```python
journey = woku.journeys.create(
    {
        "name": "Sales journey",
        "moments": [
            {
                "key": "sale",
                "name": "Sale",
                "tool": "csat",
                "toolScope": "shared",
                "toolSpec": {"subject": {"es": "tu compra", "en": "your purchase"}},
                "enabled": True,
                "channel": "whatsapp_first",
                "trigger": {"type": "webhook"},
                "sequence": {
                    "attemptOffsetsMs": [0, 28_800_000],
                    "deadlineMs": 259_200_000,
                    "cooldownAfterResponseMs": 3_600_000,
                },
            }
        ],
    }
)

# Store this now: it signs the journey inbound calls and is shown once.
print(journey["webhookSecret"])

woku.journeys.update(journey["id"], {"enabled": True})
woku.journeys.enroll(
    journey["id"],
    {"subjectKey": "customer-123", "contact": {"email": "customer@example.com"}},
)
```

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
