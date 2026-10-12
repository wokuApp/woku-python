"""Organize the listening: a folder, a tool inside it, figures and a batch move."""

from __future__ import annotations

from woku import Woku


def organize(woku: Woku) -> None:
    folder = woku.folders.create({"name": "Post-sale"})
    csat = woku.csat_tools.create(
        {
            "name": "Delivery",
            "question": "How satisfied are you with your delivery?",
            "folderId": folder["id"],
        }
    )

    for tool in woku.tools.list({"folderId": folder["id"]}):
        print(tool["type"], tool["name"], tool["headline"]["value"])

    print(woku.tools.stats({"folderId": folder["id"]}))
    woku.tools.move({"items": [{"type": "csat", "id": csat["_id"]}], "folderId": None})
