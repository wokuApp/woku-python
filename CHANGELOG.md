# Changelog

## 0.10.0

### Added

- Support and plans by folder: ticket destinations and action plan groups
  accept `scopeKind: "folder"` with a `folderId` (every tool inside it, at any
  depth). `ticket_destinations.list(params={"folderId": ...})`,
  `action_plan_groups.list({"folderId": ...})`, `tickets.list` and
  `tickets.stats` filter by folder, and tickets expose `origin.folder`.
- `folders.delete(id, confirm_dependents=True)` confirms deleting the
  destinations and groups configured on the folder; without it the API answers
  409 `FOLDER_HAS_DEPENDENTS`.

## 0.9.0

### Added

- `data_apps` (sync and async) for Data Studio apps on `/v1/data-apps`: `list`,
  `get` (with `version`), `run_queries`, `edit` with operations, `build`,
  `restore`, `copy_from_version`, `duplicate`, `publish`, `unpublish`,
  `list_tables` and `upload_table`. Every change makes a
  new version; personal data never comes back.

## 0.8.1

### Fixed

- The bundled OpenAPI spec (`openapi/openapi-v1.json`, shipped in the sdist) no
  longer names private routes in the summaries of seven `/v1` endpoints (for
  example "v1 alias of POST /wokus/create-woku"). No API change.

## 0.8.0

### Added

- `report_subscriptions` (sync and async): schedule report emails of a folder
  or a tool (monthly, every two weeks, weekly or once) with `list`, `create`,
  `update`, `delete` and `send`.
- `folder_participants` (sync and async): a folder's participant list with
  `get` (who of it answered each tool), `replace`, `add`, `remove`, `clear` and
  `resend_to_missing`.
- `folders.csv` takes `params` with `from`/`to` to keep only a period. `params`
  goes before `options`, as in `folders.report`.
- `tools.list` documents `sort` by `lastResponse` (the latest response).

- NPS, CSAT and CES tools take `anonymousDisabled` and
  `onlyOneResponsePerClient` on `create` and `update`, and return both on every
  tool. Both can change even after the tool has responses. A repeat answer to a
  one-response-per-client survey is rejected with HTTP 409 `ALREADY_RESPONDED`.

## 0.7.0

### Added

- `whatsappAlertRecipients` numbers take `allReviews`: `True` alerts every
  review (recognitions too), `False` or absent keeps improvement alerts only.
  Folders return it on every recipient.

## 0.6.0

### Added

- `folders.metrics` documents the custom `from`/`to` range of UTC days (both
  inclusive, up to 731 days), as the admin custom period; the result then also
  carries `from` and `to`.

### Removed

- `quarantines.check()` (sync and async): the public API no longer exposes
  `GET /v1/quarantines/check`, since quarantines are not managed from the admin
  anymore. Existing quarantines are still enforced when a respondent answers.

## 0.5.0

### Folders and tools

- New `folders` resource: `list`, `get`, `create`, `update`, `move`, `delete`
  (content moves up to the parent), `report` and `csv` over every woku, NPS,
  CSAT and CES tool of the folder and its subfolders.
- New `tools` resource: cursor-paginated `list` across wokus and NPS, CSAT and CES
  with search and filters, `stats` per type in native scales and batch `move`.
- `folderId` on NPS, CSAT and CES tool creation and responses, plus
  `move(tool_id, {"folderId": ...})`.
- New `journey_folders` resource (`status`, `organize`), `folderId` and `momentFolders`
  on journeys, and `origin` on folders.
- Folders expose `whatsappAlertRecipients` (settable on `folders.update`): the WhatsApp
  numbers alerted when a comment on any woku, NPS, CSAT or CES tool of the folder
  is an improvement.
- `folders.pdf` returns the folder report as PDF bytes (per-type breakdown on each
  native scale), and `tools.list` pages the folders with `foldersLimit`
  (`has_more_folders()` and `get_more_folders()`, sync and async).
- `flows` is no longer read-only: `create`, `update`, `delete` and ordered `steps`
  (woku, NPS, CSAT, CES) on every flow.
- `folders.metrics` (per-tool figures for a period against the one before it, daily
  sums and the histogram of scores), `trackers` on `tools.list` and
  `integrationProvider` on folders, sync and async.
- Sync and async twins, regenerated models from the public OpenAPI, contract
  tests and an example. Requires the server release that ships these endpoints.

## 0.3.0

### Customer journeys v3 and SDK v4

- Generated request/response models for all 17 journey operations, including
  advanced webhook content, folder nesting, trackers and prepared customer entry.
- Sync/async multipart media uploads and lazy enrollment iterators.
- Standalone vendored OpenAPI and deterministic generated-model drift checks.
- Case-insensitive headers, configured origin for custom HTTP clients, encoded
  identifiers, advancing pagination, nested validation errors and safe retries.
- API and connection errors expose the original operation idempotency key.
- Four-moment example, actual Python 3.9, wheel/sdist and test API validation.

Requires the customer journey API release with atomic idempotency for protected writes.
