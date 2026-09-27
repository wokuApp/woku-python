from __future__ import annotations

import httpx
import respx

from woku import AsyncWoku, Woku

BASE = "http://api.test"


def client() -> Woku:
    return Woku(api_key="sk_test", base_url=BASE)


def async_client() -> AsyncWoku:
    return AsyncWoku(api_key="sk_test", base_url=BASE)


@respx.mock
def test_auto_iterates_items_across_pages_lazily() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params.get("page") or 1)
        if page == 1:
            return httpx.Response(
                200,
                json={
                    "data": [{"id": "a"}, {"id": "b"}],
                    "total": 3,
                    "page": 1,
                    "limit": 2,
                },
            )
        return httpx.Response(
            200, json={"data": [{"id": "c"}], "total": 3, "page": 2, "limit": 2}
        )

    respx.get(f"{BASE}/v1/items").mock(side_effect=handler)
    first = client().get_page("/v1/items")
    assert first.has_next_page() is True
    ids = [item["id"] for item in first]
    assert ids == ["a", "b", "c"]


@respx.mock
def test_walks_page_by_page_with_iter_pages() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params.get("page") or 1)
        return httpx.Response(
            200, json={"data": [{"n": page}], "total": 2, "page": page, "limit": 1}
        )

    respx.get(f"{BASE}/v1/items").mock(side_effect=handler)
    first = client().get_page("/v1/items")
    assert [p.page for p in first.iter_pages()] == [1, 2]


@respx.mock
def test_bare_array_response_is_a_single_page() -> None:
    respx.get(f"{BASE}/v1/events").mock(
        return_value=httpx.Response(200, json=[{"id": "e1"}, {"id": "e2"}])
    )
    page = client().get_page("/v1/events")
    assert page.has_next_page() is False
    assert [item["id"] for item in page] == ["e1", "e2"]


@respx.mock
async def test_async_auto_iterates_items_across_pages() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params.get("page") or 1)
        if page == 1:
            return httpx.Response(
                200, json={"data": [{"id": "a"}], "total": 2, "page": 1, "limit": 1}
            )
        return httpx.Response(
            200, json={"data": [{"id": "b"}], "total": 2, "page": 2, "limit": 1}
        )

    respx.get(f"{BASE}/v1/items").mock(side_effect=handler)
    async with async_client() as woku:
        first = await woku.get_page("/v1/items")
        ids = [item["id"] async for item in first]
    assert ids == ["a", "b"]


@respx.mock
def test_query_page_override_does_not_repeat_the_same_page() -> None:
    requested: list[int] = []

    def respond(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params["page"])
        requested.append(page)
        return httpx.Response(
            200, json={"data": [page], "total": 3, "page": page, "limit": 1}
        )

    respx.get(f"{BASE}/v1/items").mock(side_effect=respond)
    with Woku(api_key="sk_test", base_url=BASE) as sdk:
        page = sdk.get_page(
            "/v1/items", {"page": 1, "limit": 1}, {"params": {"page": 2}}
        )
        values = []
        for value in page:
            values.append(value)
            if len(values) == 3:
                break
    assert values == [2, 3]
    assert requested == [2, 3]
