from __future__ import annotations

import json

import httpx
import respx

from woku import AsyncWoku, Woku

BASE = "http://api.test"


def sdk() -> Woku:
    return Woku(api_key="sk_test", base_url=BASE, max_retries=0)


@respx.mock
def test_lists_apps_and_reads_one_version() -> None:
    respx.get(f"{BASE}/v1/data-apps").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [{"id": "a1", "title": "Ranking", "kind": "studio"}],
                "total": 1,
                "page": 1,
                "limit": 20,
                "totalPages": 1,
            },
        )
    )
    route = respx.get(f"{BASE}/v1/data-apps/a1").mock(
        return_value=httpx.Response(
            200, json={"id": "a1", "version": {"version": 2, "stage": "built"}}
        )
    )
    with sdk() as client:
        page = client.data_apps.list()
        app = client.data_apps.get("a1", version=2)
    assert page.data[0]["kind"] == "studio"
    assert app["version"]["version"] == 2
    assert route.calls.last.request.url.params["version"] == "2"


@respx.mock
def test_runs_queries_edits_and_manages_versions() -> None:
    queries = respx.post(f"{BASE}/v1/data-apps/a1/queries").mock(
        return_value=httpx.Response(200, json={"monthly": {"ok": True, "rows": []}})
    )
    edit = respx.post(f"{BASE}/v1/data-apps/a1/operations").mock(
        return_value=httpx.Response(201, json={"version": 4})
    )
    respx.post(f"{BASE}/v1/data-apps/a1/build").mock(
        return_value=httpx.Response(201, json={"version": 5})
    )
    respx.post(f"{BASE}/v1/data-apps/a1/versions/1/restore").mock(
        return_value=httpx.Response(201, json={"version": 6})
    )
    publish = respx.post(f"{BASE}/v1/data-apps/a1/versions/6/publish").mock(
        return_value=httpx.Response(
            200, json={"slug": "ranking", "isPublished": True, "publishedVersion": 6}
        )
    )
    with sdk() as client:
        client.data_apps.run_queries(
            "a1",
            {"queries": [{"id": "monthly"}], "params": {"period": {"from": "-30d"}}},
        )
        assert (
            client.data_apps.edit(
                "a1",
                {"baseVersion": 3, "operations": [{"op": "setTitle", "title": "X"}]},
            )["version"]
            == 4
        )
        assert client.data_apps.build("a1")["version"] == 5
        assert client.data_apps.restore("a1", 1)["version"] == 6
        published = client.data_apps.publish("a1", 6, {"accessKey": "clave"})
    assert json.loads(queries.calls.last.request.content) == {
        "queries": [{"id": "monthly"}],
        "params": {"period": {"from": "-30d"}},
    }
    assert json.loads(edit.calls.last.request.content)["baseVersion"] == 3
    assert json.loads(publish.calls.last.request.content) == {"accessKey": "clave"}
    assert published["publishedVersion"] == 6


@respx.mock
async def test_async_tables_list_and_upload_once() -> None:
    respx.get(f"{BASE}/v1/data-apps/a1/tables").mock(
        return_value=httpx.Response(
            200, json={"data": [{"id": "t1", "source": "table:t1"}]}
        )
    )
    upload = respx.post(f"{BASE}/v1/data-apps/a1/tables").mock(
        return_value=httpx.Response(201, json={"id": "t1", "version": 2})
    )
    async with AsyncWoku(api_key="sk_test", base_url=BASE) as client:
        tables = await client.data_apps.list_tables("a1")
        table = await client.data_apps.upload_table(
            "a1", b"Meta\n10\n", filename="metas.csv", content_type="text/csv"
        )
    assert tables[0]["source"] == "table:t1"
    assert table["version"] == 2
    request = upload.calls.last.request
    assert request.headers["content-type"].startswith("multipart/form-data")
    assert b'filename="metas.csv"' in request.content
    assert upload.call_count == 1
