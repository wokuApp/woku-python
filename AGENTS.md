# woku (Python SDK) — agent conventions

Official server-side Python SDK for the Woku management API (`/v1`), sync
(`Woku`) and async (`AsyncWoku`) over httpx. Floor Python 3.9. Tooling: uv +
hatchling + ruff + pyright + pytest.

## Keep the README current (hard rule)

Any change to the SDK's public surface or behavior (methods added or removed,
examples, options, versions) MUST update `README.md` **in the same change**. The
PyPI page freezes the README at publish time, so a README fix needs a new patch
version to reach the package page; the GitHub README updates on merge. Never ship
a change that leaves an example or a listed method stale.

## Workflow

- Gate before any PR: `uv run ruff check .`, `uv run ruff format --check .`,
  `uv run pyright`, `uv run pytest -q`. Verify on **real 3.9**
  (`uv run --python 3.9 pytest -q`): a generic TypedDict is invalid before 3.11
  and `X | Y` is a runtime error in value positions on 3.9.
- Version lives in `src/woku/_version.py`; the GitHub Release tag must match it.
  Code, comments and commits in English.
- Never present integrations that are not in production (only Shopify and Zendesk
  are). No `action_plans.send` to external tools.
