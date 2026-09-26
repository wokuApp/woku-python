"""Lazy pagination over the ``page``/``limit`` envelope every list returns."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Iterator
from typing import (
    Any,
    Callable,
    Generic,
    TypedDict,
    TypeVar,
)

from ._exceptions import WokuError

T = TypeVar("T")


class PageResponse(TypedDict):
    """The paginated envelope every ``/v1`` list endpoint returns.

    Not generic: a generic ``TypedDict`` is only valid on Python 3.11+. Item
    typing lives on :class:`SyncPage` / :class:`AsyncPage` instead.
    """

    data: list[Any]
    total: int
    page: int
    limit: int


def is_page_response(value: Any) -> bool:
    """True when ``value`` has the shape of a :class:`PageResponse`."""
    total = value.get("total") if isinstance(value, dict) else None
    return (
        isinstance(value, dict)
        and isinstance(value.get("data"), list)
        # accept any JSON number for `total` (int or float), matching the
        # reference SDK's `typeof total === "number"` check.
        and isinstance(total, (int, float))
        and not isinstance(total, bool)
    )


class _BasePage(Generic[T]):
    """Shared page state (data + cursor arithmetic)."""

    def __init__(self, response: PageResponse) -> None:
        self.data: list[T] = list(response.get("data", []))
        self.total: int = int(response.get("total", 0))
        self.page: int = int(response.get("page", 1))
        self.limit: int = int(response.get("limit", 0))

    def has_next_page(self) -> bool:
        """Whether another page exists after this one."""
        if self.limit <= 0:
            return False
        return self.page * self.limit < self.total


class SyncPage(_BasePage[T]):
    """A single page plus a lazy cursor to walk the rest.

    Iterate items across every page with ``for item in page`` or walk page by
    page with ``for p in page.iter_pages()``.
    """

    def __init__(
        self,
        response: PageResponse,
        fetch_page: Callable[[int], SyncPage[T]],
    ) -> None:
        super().__init__(response)
        self._fetch_page = fetch_page

    def get_next_page(self) -> SyncPage[T]:
        """Fetch the next page (raise if there is none; guard with has_next_page)."""
        if not self.has_next_page():
            raise IndexError("No next page")
        next_page = self._fetch_page(self.page + 1)
        if next_page.page <= self.page:
            raise WokuError("Pagination did not advance.", code="pagination_error")
        return next_page

    def __iter__(self) -> Iterator[T]:
        page: SyncPage[T] = self
        while True:
            yield from page.data
            if not page.has_next_page():
                return
            page = page.get_next_page()

    def iter_pages(self) -> Iterator[SyncPage[T]]:
        """Yield each page, fetching lazily as needed."""
        page: SyncPage[T] = self
        while True:
            yield page
            if not page.has_next_page():
                return
            page = page.get_next_page()


class AsyncPage(_BasePage[T]):
    """The async twin of :class:`SyncPage`.

    Iterate items across every page with ``async for item in page`` or walk page
    by page with ``async for p in page.iter_pages()``.
    """

    def __init__(
        self,
        response: PageResponse,
        fetch_page: Callable[[int], Awaitable[AsyncPage[T]]],
    ) -> None:
        super().__init__(response)
        self._fetch_page = fetch_page

    async def get_next_page(self) -> AsyncPage[T]:
        """Fetch the next page (raise if there is none; guard with has_next_page)."""
        if not self.has_next_page():
            raise IndexError("No next page")
        next_page = await self._fetch_page(self.page + 1)
        if next_page.page <= self.page:
            raise WokuError("Pagination did not advance.", code="pagination_error")
        return next_page

    async def __aiter__(self) -> AsyncIterator[T]:
        page: AsyncPage[T] = self
        while True:
            for item in page.data:
                yield item
            if not page.has_next_page():
                return
            page = await page.get_next_page()

    async def iter_pages(self) -> AsyncIterator[AsyncPage[T]]:
        """Yield each page, fetching lazily as needed."""
        page: AsyncPage[T] = self
        while True:
            yield page
            if not page.has_next_page():
                return
            page = await page.get_next_page()
