# Changelog

## Unreleased

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
