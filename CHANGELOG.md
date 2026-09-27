# Changelog

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
