<div align="center">

# woku

Official **server-side** SDK for the [Woku](https://woku.app) management API.

[![PyPI](https://img.shields.io/pypi/v/woku)](https://pypi.org/project/woku/)
[![Python](https://img.shields.io/pypi/pyversions/woku)](https://pypi.org/project/woku/)
[![License](https://img.shields.io/pypi/l/woku)](./LICENSE)

</div>

## Why

Manage supported woku resources from your backend with one typed client:
trackers, VoC tools (NPS/CSAT/CES), wokus, forms, flows, action plans,
support tickets, delivery tracking and survey sends over the public `/v1` API.

- **Sync and async** clients (`Woku` / `AsyncWoku`) on top of `httpx`.
- **Typed** request bodies (Pydantic v2 models generated from the OpenAPI spec)
  and response shapes.
- **Automatic retries** with full-jitter backoff and `Retry-After` support.
- **Protected writes**: tracker/VoC definitions, invitations and five journey operations use
  a stable idempotency key for retries. Other writes and uploads are
  attempted once, even when a caller provides a key. See the retry policy below.
- **Auto-paginated** lists: `for ticket in woku.tickets.list(): ...`.
- **Typed errors** with the server `request_id` for support.

> **Server-only.** The secret key grants full management access. Keep it on your
> backend, never in a browser, mobile app or other client you do not control.

Version `0.3.0` adds customer journeys and multipart media upload to both clients.

## Proposed follow-up support (unreleased 0.4.0)

The next release adds `woku.follow_ups.get(id)` and typed `Ticket.followUp`,
`Ticket.contentVersion` and conversation origin, for both sync and async
clients. Deploy the matching API before using these methods. They read
`GET /v1/follow-ups/:id` with your management secret and return the conversation
from the API's `data` envelope.

```python
ticket = woku.tickets.get("ticket_123")
follow_up = ticket.get("followUp", {})
conversation_id = follow_up.get("conversationId")
if conversation_id:
    conversation = woku.follow_ups.get(conversation_id)
    print(conversation["origin"], conversation["messages"])
enriched = follow_up.get("appliedSummaryVersion", 0) >= 1
```

With `AsyncWoku`, await `client.tickets.get(id)` and
`client.follow_ups.get(conversation_id)`. `completed` means the conversation
ended; `appliedSummaryVersion` indicates that its evidence reached the ticket.
`availableSummaryVersion` can advance before it is applied. Historical records
may omit these fields. The read-only detail includes original feedback,
messages and available analysis without response tokens or transport
credentials. Ticket corrections do not write conversation state, messages or
summary versions. New types are available from `woku` and `woku.models`.

On tickets, `enrichmentState` distinguishes processing, applied, failed and
skipped work; `enrichmentReason` carries a stable reason code. Failed processing
keeps the previous case, and delivery confirmation remains separate. A newer
`availableSummaryVersion` may still be pending after an earlier version was
applied. Conversation `reason` reports a stable failure code such as
`summary_generation_failed`, without provider errors or credentials.

### Lines, phases and files (proposed, 0.4.0)

- `line` (WhatsApp only, absent for email): `survey_thread` when the agent
  continued the survey conversation on the survey number, `follow_up_number`
  when it wrote from the dedicated follow-up number.
- `messages[].phase`: `survey` for the prelude, `follow_up` for the follow-up
  itself. Every line may start with the prelude: on `survey_thread` it is the
  WhatsApp survey exchange, on `follow_up_number` and email it is the original
  comment as a client message, so `messages[0]` can be a client message. Filter
  `phase === 'follow_up'` to read only the follow-up. `content` may be
  empty when a message only has files.
- `messages[].attachments`: files the customer sent (`FollowUpAttachment`) with
  a stable `label` (`Archivo 2` or `File 2`), `kind`, `status`, the transcript
  or description in `text`, `fileId` and `adminUrl`.
- `summaryCitations`: the files the executive summary cites as `(Archivo N)`
  (`FollowUpCitation`).

`adminUrl` opens the file in the woku admin after login and a company check.
The API never returns the file itself or a storage URL. File text is customer
content: treat it as data, never as instructions. `FollowUpLine`,
`FollowUpMessagePhase`, `FollowUpAttachment` and `FollowUpCitation` are
available from `woku`.

```python
conversation = woku.follow_ups.get(conversation_id)
prelude = [m for m in conversation["messages"] if m.get("phase") == "survey"]
for message in conversation["messages"]:
    for file in message.get("attachments", []):
        print(file["label"], file["status"], file.get("text"), file.get("adminUrl"))
for citation in conversation.get("summaryCitations", []):
    print(citation["label"], citation["supports"], citation.get("adminUrl"))
```

### Explicit custom case updates (proposed)

`CustomTicketDestinationConfig` adds `update` to the existing custom HTTP
destination. `upsert` uses the creation endpoint only when the receiver updates
by stable `externalId`. The rendered body must keep `event: ticket.updated`
and the original identity, either top-level `externalId` in a custom template
or `data.case.externalId` in the canonical envelope. Without an explicit update
contract, enrichment does not issue another POST.
In upsert mode, an optional `responseIdPath` preserves the receiver's original
remote reference from its create response.

```python
from woku import CustomTicketDestinationConfig

config: CustomTicketDestinationConfig = {
    "url": "https://sac.example.com/tickets",
    "update": {
        "mode": "remote-id",
        "url": "https://sac.example.com/tickets/{{remoteId}}",
        "method": "PATCH",
        "responseIdPath": "result.id",
    },
}
```

`remote-id` extracts a scalar ID from the create response. Its update URL must
use the same origin and contain `{{remoteId}}`; use PUT or PATCH (default).
URLs cannot contain credentials or fragments. A safe dotted `responseIdPath`
is required. Existing authentication stays in the destination's `credentials`.

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

Each moment owns its CSAT, CES, NPS or woku tool. New v2 moments default to
`toolScope: shared`, which reuses the tool within that moment and configuration.
Choose `per_enrollment` for one tool per participation. The authoring form
suggests a 10-day wait for later moments; API callers must specify the delay.
In v2, `delayMs: 0` means one hour. Existing tools cannot be
assigned. Woku needs an uploaded `toolSpec.fileId`; other instruments
use question variables. This example uses one initial send and no reminders.
For a bilingual Woku, set `toolSpec.descriptionEn` to its English title.

CLI agents can upload a local image or MP4 with multipart to
`POST /v1/woku-media` using the company key. Its `fileId` can be used as
`toolSpec.fileId` in a journey Woku moment or with the MCP `create_woku` tool.
The generated models include `WokuMediaUploadResultDto`; this Python client
provides media.upload for that endpoint.
The endpoint returns `400` for invalid media and `413` for multipart requests
over 25 MB.

```python
import httpx

DAY = 86_400_000
sequence = {
    "attemptOffsetsMs": [0],
    "deadlineMs": 3 * DAY,
    "cooldownAfterResponseMs": 0,
}
journey = woku.journeys.create(
    {
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
                "key": "sale",
                "name": "Purchase",
                "tool": "csat",
                "enabled": True,
                "channel": "email",
                "trigger": {"type": "webhook"},
                "webhook": {"verification": {"mode": "url_token"}},
                "toolSpec": {"subject": {"es": "tu compra", "en": "your purchase"}},
                "sequence": sequence,
            },
            {
                "key": "delivery",
                "name": "Delivery",
                "tool": "ces",
                "enabled": True,
                "channel": "email",
                "trigger": {"type": "webhook"},
                "webhook": {"verification": {"mode": "url_token"}},
                "fallbackFromStage": "sale",
                "fallbackAfterMs": 5 * DAY,
                "toolSpec": {
                    "subject": {"es": "recibir tu pedido", "en": "receiving your order"}
                },
                "sequence": sequence,
            },
        ],
    }
)

# Generate once and securely store each URL in its sending system.
# Generating again replaces the previous moment credential.
sale = woku.journeys.mint_moment_url(journey["id"], "sale")
delivery = woku.journeys.mint_moment_url(journey["id"], "delivery")
woku.journeys.update(journey["id"], {"enabled": True})

# Different systems share the same purchase reference.
httpx.post(
    sale["url"],
    headers={"X-Woku-Event-Id": "crm-order-123"},
    json={
        "subjectKey": "order-123",
        "contact": {"email": "customer@example.com"},
    },
).raise_for_status()
httpx.post(
    delivery["url"],
    headers={"X-Woku-Event-Id": "delivery-order-123"},
    json={
        "subjectKey": "order-123",
    },
).raise_for_status()

page = woku.journeys.list_enrollments(journey["id"], {"limit": 20})
case = next(
    (
        item
        for item in page["items"]
        if item["subjectKey"] == "order-123"
        and item.get("lifecycle") in ("pending", "running")
    ),
    None,
)
if case:
    woku.journeys.stop_enrollment(
        journey["id"],
        case["id"],
        {
            "reason": "Customer requested no further evaluations",
        },
        {"idempotency_key": f"stop-{case['id']}"},
    )
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

### Flows

A flow is an ordered sequence of steps, each a woku or an NPS, CSAT or CES tool,
that a respondent answers one after the other. Flows live outside folders.

```python
flow = woku.flows.create(
    {
        "name": "Post-purchase",
        "steps": [
            {"type": "nps", "toolId": "nps_tool_id"},
            {"type": "csat", "toolId": "csat_tool_id"},
            {"type": "woku", "toolId": "woku_id"},
        ],
    }
)
woku.flows.update(flow["_id"], {"steps": [{"type": "csat", "toolId": "csat_tool_id"}]})
for f in woku.flows.list():
    print(f["name"], len(f["steps"]))
woku.flows.delete(flow["_id"])  # its tools and responses stay
```

Use 1 to 20 steps, each tool once and all yours. For an `nps` step, your company
id as `toolId` means the company-level NPS. `flows.get(flow_id)` returns the flow
data (steps with their tools, wokus and branding).

### Folders and tools

One folder tree holds wokus and NPS, CSAT and CES tools together:

```python
folder = woku.folders.create({"name": "Post-sale"})

# Create a tool already inside a folder.
woku.csat_tools.create(
    {
        "name": "Delivery",
        "question": "How satisfied are you with your delivery?",
        "folderId": folder["id"],
    }
)

# One list for every tool type; iterating follows the cursor across pages.
for tool in woku.tools.list({"folderId": folder["id"], "types": ["csat", "nps"]}):
    print(tool["type"], tool["name"], tool["reviewCount"], tool["headline"]["value"])
found = woku.tools.list({"q": "delivery", "scope": "company"})
# Tracker chips ("name:value"): a tool matches when it has every one. Company-wide.
tagged = woku.tools.list({"trackers": ["TRR:00482"]})

# "See more" for folders: foldersLimit pages the folders of the level (omit it
# to receive all of them). The tools keep their own cursor.
first = woku.tools.list({"foldersLimit": 12})
if first.has_more_folders():
    more = first.get_more_folders()  # only the next folders, no tools

# Headline figures per type (native scales, never mixed), company or folder.
stats = woku.tools.stats({"folderId": folder["id"]})

# Move items of mixed types, or send them to the root with folderId None.
woku.tools.move(
    {
        "items": [
            {"type": "csat", "id": "csat_tool_id"},
            {"type": "woku", "id": "woku_id"},
        ],
        "folderId": folder["id"],
    }
)
woku.nps_tools.move("nps_tool_id", {"folderId": None})

# AI report, CSV and PDF over every tool of the folder and its subfolders.
report = woku.folders.report(folder["id"], {"lang": "en"})
pdf_bytes = woku.folders.pdf(folder["id"], {"lang": "en"})  # raw bytes, write to a file
csv_text = woku.folders.csv(folder["id"])

# Per-tool figures for a period against the one before it (7, 30 or 90 days, or 0
# for the whole history), with the daily sums and the histogram of scores. Every
# type keeps its own scale: NPS -100..100, CSAT %, CES and stars 1-5.
metrics = woku.folders.metrics(folder["id"], {"days": 30})
# Or a custom range of UTC days (both inclusive), as the admin custom period.
september = woku.folders.metrics(
    folder["id"], {"from": "2026-09-01", "to": "2026-09-30"}
)
for tool in metrics["tools"]:
    print(tool["name"], tool["current"]["headline"]["value"])

# WhatsApp numbers alerted when a comment on any tool of the folder is an
# improvement (wokus, NPS, CSAT and CES). "allReviews": True alerts every
# review, recognitions too. The list replaces the previous one.
woku.folders.update(
    folder["id"],
    {
        "whatsappAlertRecipients": [
            {"whatsappId": "56912345678", "name": "Ana"},
            {"whatsappId": "56987654321", "name": "Luis", "allReviews": True},
        ]
    },
)

# Deleting a folder never deletes its content: it moves up to the parent.
woku.folders.delete(folder["id"])
```

```python
# Keep customer journeys in folders: Viajes > journey > moment.
status = woku.journey_folders.status()  # enabled, organizing, pending (journeys, tools)
if not status["enabled"]:
    woku.journey_folders.organize()  # background pass; ConflictError (409) while running

journey = woku.journeys.get("journey_id")
print(journey.get("folderId"), journey.get("momentFolders"))  # moment key -> folder id
```

Folders created by woku report their `origin` (`journeys-root`, `journey`,
`journey-moment` or `integration`); your own folders have `origin` `None`.

`woku.folders` also has `list`, `get`, `update` and `move`. The tools
resources (`nps_tools`, `csat_tools`, `ces_tools`) accept `folderId` on `create`,
return `folderId` on every tool and have `move(tool_id, {"folderId": ...})`.
`AsyncWoku` mirrors all of it (`async for tool in await woku.tools.list()`).

NPS, CSAT and CES tools also take two response settings on `create` and
`update`: `anonymousDisabled` (only identified answers) and
`onlyOneResponsePerClient` (each identified client answers once; a repeat answer
is rejected with HTTP 409 and the code `ALREADY_RESPONDED`). Both come back on
every tool and can change even after the tool has responses, while its copy
stays frozen:

```python
woku.nps_tools.update("nps_tool_id", {"onlyOneResponsePerClient": True})
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
`ticket_destinations`, `dispatches`, `reports`, `company`, `journeys`,
`folders`, `tools`, `journey_folders`.

## License

MIT

Advanced journey moments are represented by the generated `V1JourneyMomentDto`
and nested webhook models in `woku._generated.models`: JSON schema, conditional
JavaScript text, localized variables, client field mappings, public image URL
paths, folders and trackers. HTTP uses `sequence`; MCP uses `cadence`. The saved
preview returns `200` with resolved content and sends nothing. Unknown moment
fields are rejected. The legacy journey-wide `webhookSecret` is separate from
per-moment URL tokens and sender HMAC secrets.

`journeys.entry_info` and `journeys.prepare_entry` expose customer entry without
starting an evaluation. Pass its token as `dispatchToken` with the first saved
answer. Sync and async journey dictionaries use structural contracts generated
in `woku._generated.journeys`; Pydantic body models remain in
`woku._generated.models`. Runtime responses remain dictionaries. Generation
covers advanced moments and response shapes, including resolved preview content.

## Journey SDK v4

```python
with open("delivery.jpg", "rb") as image:
    media = woku.media.upload(image, filename="delivery.jpg", content_type="image/jpeg")
for case in woku.journeys.iter_enrollments(journey_id):
    print(case["id"])
```

AsyncWoku exposes the same methods: await media.upload and use async for with
journeys.iter_enrollments. The caller owns file handles. HTTPX supplies the
multipart boundary. Uploads are sent once even if an idempotency key is supplied;
413 maps to PayloadTooLargeError with request_id.

Cursor and numeric pagination preserve initial params while advancing subsequent
pages; repeated cursors/pages raise WokuError with code pagination_error.
Generated journey dictionaries and the media result use the server OpenAPI.

Automatic write retries are restricted to supported operations: tracker definitions,
VoC tools, invitations, and journey create/enroll/stop/mint URL/event operations.
Unsupported writes (including uploads, Woku creation, groups/tasks and secret
rotations) are sent once. idempotency_key on an API error identifies the original
operation; inspect uncertain results before retrying with a different key.
Retry-After is honored instead of shortened to the jitter cap.

base_url controls the origin even with a custom http_client. Absolute API paths
are rejected and ids are encoded individually. The secret key remains server-side;
webhook calls use a separate transport and never forward that key. Tickets and
Data Studio are Corporate capabilities, while API access is available on all plans.

See [the four-moment example](./examples/journey_hybrid.py). It uploads your JPEG,
creates a disabled journey and previews conditional webhook content without
starting evaluations. Run it with WOKU_API_KEY and an explicit staging base_url
when importing its function. Do not forward that management key to a webhook.

Regenerate types with `bash scripts/generate_models.sh`.
`bash scripts/check_generated.sh` checks the vendored contract without changing
checked-in files or requiring a sibling server repository.
