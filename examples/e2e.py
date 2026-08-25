"""End-to-end smoke against a LIVE Woku stack. Run with a real secret key::

    WOKU_API_KEY=sk_... WOKU_BASE_URL=https://clientapi.woku.app \
        uv run python examples/e2e.py

By default it only READS (create tracker + tool, then read delivery back). It
sends real invitations ONLY when WOKU_E2E_ALLOW_SEND=true and WOKU_E2E_RECIPIENT
is set - sends reach real inboxes, so keep it off unless WOKU_BASE_URL points at
a safe (non-production) environment.
"""

from __future__ import annotations

import os
import time

from woku import Woku


def main() -> None:
    woku = Woku(
        api_key=os.environ.get("WOKU_API_KEY"),
        base_url=os.environ.get("WOKU_BASE_URL"),
    )

    # 1. Company handshake (no side effects).
    company = woku.company.me()
    print("company:", company)

    # 2. Create a tracker definition (idempotent).
    stamp = int(time.time())
    tracker = woku.trackers.create({"name": f"sdk-e2e-{stamp}", "system": "sdk-e2e"})
    print("tracker:", tracker.get("_id"))

    # 3. Create an NPS tool.
    tool = woku.nps_tools.create(
        {
            "name": f"sdk-e2e-{stamp}",
            "npsMessage": "How likely are you to recommend us?",
        }
    )
    tool_id = tool["_id"]
    print("npsTool:", tool_id)

    # 4. Optionally send (real invitation - off by default).
    recipient = os.environ.get("WOKU_E2E_RECIPIENT")
    if os.environ.get("WOKU_E2E_ALLOW_SEND") == "true" and recipient:
        result = woku.nps.send_invitations(
            {"channel": "email", "npsToolId": tool_id, "recipients": [recipient]}
        )
        print("sent:", result)
    else:
        print("send skipped (set WOKU_E2E_ALLOW_SEND=true + WOKU_E2E_RECIPIENT)")

    # 5. Read back delivery + response rate.
    stats = woku.dispatches.stats()
    print("dispatch stats:", stats)

    # 6. Cleanup the tool (delete cascades its responses).
    woku.nps_tools.delete(tool_id)
    woku.trackers.deactivate(tracker["_id"])
    print("done")


if __name__ == "__main__":
    main()
