"""Action plans and action-plan groups.

Covers ``/v1/action-plans`` and ``/v1/action-plan-groups``.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, TypedDict
from urllib.parse import quote

from .._options import RequestOptions
from .._pagination import AsyncPage, SyncPage
from ..models import WokuRecord
from ..types import (
    CreateActionPlanGroupParams,
    CreateActionPlanTaskParams,
    ReorderActionPlanTasksParams,
    UpdateActionPlanGroupParams,
    UpdateActionPlanTaskParams,
)

if TYPE_CHECKING:
    from .._client import AsyncWoku, Woku

# `from` is a reserved word, so the functional TypedDict syntax is used to keep
# the wire key exactly `from` (the value is passed straight through as a query).
ListActionPlansParams = TypedDict(
    "ListActionPlansParams",
    {
        "groupId": str,
        "status": str,
        "source": str,
        "priority": str,
        "search": str,
        "from": str,
        "to": str,
        "page": int,
        "limit": int,
    },
    total=False,
)


class ActionPlans:
    """Read and drive action plans, incl. the managed kanban."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: ListActionPlansParams | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPage[WokuRecord]:
        return self._client.get_page("/v1/action-plans", params, options)

    def get(self, plan_id: str, options: RequestOptions | None = None) -> WokuRecord:
        return self._client.request(
            "get", f"/v1/action-plans/{quote(plan_id, safe='')}", options=options
        )

    def events(
        self, plan_id: str, options: RequestOptions | None = None
    ) -> builtins.list[WokuRecord]:
        """The plan timeline (events, oldest first)."""
        return self._client.request(
            "get", f"/v1/action-plans/{quote(plan_id, safe='')}/events", options=options
        )

    def get_conversation(
        self, plan_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """The plan AI conversation (read-only)."""
        return self._client.request(
            "get",
            f"/v1/action-plans/{quote(plan_id, safe='')}/conversation",
            options=options,
        )

    def reply(
        self, plan_id: str, text: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Reply to the plan AI agent.

        Each reply is a paid AI turn (``confirm: true`` is sent automatically);
        the reply is composed asynchronously, so poll :meth:`get_conversation`
        until ``busy`` is false.
        """
        return self._client.request(
            "post",
            f"/v1/action-plans/{quote(plan_id, safe='')}/conversation",
            body={"text": text, "confirm": True},
            options=options,
        )

    def create_task(
        self,
        plan_id: str,
        body: CreateActionPlanTaskParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return self._client.request(
            "post",
            f"/v1/action-plans/{quote(plan_id, safe='')}/tasks",
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    def update_task(
        self,
        plan_id: str,
        task_id: str,
        body: UpdateActionPlanTaskParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return self._client.request(
            "patch",
            (
                f"/v1/action-plans/{quote(plan_id, safe='')}"
                f"/tasks/{quote(task_id, safe='')}"
            ),
            body=body,
            options=options,
        )

    def reorder_tasks(
        self,
        plan_id: str,
        body: ReorderActionPlanTasksParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return self._client.request(
            "patch",
            f"/v1/action-plans/{quote(plan_id, safe='')}/tasks/reorder",
            body=body,
            options=options,
        )

    def delete_task(
        self,
        plan_id: str,
        task_id: str,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return self._client.request(
            "delete",
            (
                f"/v1/action-plans/{quote(plan_id, safe='')}"
                f"/tasks/{quote(task_id, safe='')}"
            ),
            options=options,
        )

    def approve(
        self, plan_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return self._status(plan_id, "approve", options)

    def reopen(self, plan_id: str, options: RequestOptions | None = None) -> WokuRecord:
        return self._status(plan_id, "reopen", options)

    def cancel(self, plan_id: str, options: RequestOptions | None = None) -> WokuRecord:
        return self._status(plan_id, "cancel", options)

    def complete(
        self, plan_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return self._status(plan_id, "complete", options)

    def resume(self, plan_id: str, options: RequestOptions | None = None) -> WokuRecord:
        return self._status(plan_id, "resume", options)

    def _status(
        self, plan_id: str, action: str, options: RequestOptions | None
    ) -> WokuRecord:
        return self._client.request(
            "post",
            f"/v1/action-plans/{quote(plan_id, safe='')}/{action}",
            options=options,
        )


class ActionPlanGroups:
    """Manage action-plan groups."""

    def __init__(self, client: Woku) -> None:
        self._client = client

    def list(
        self,
        params: dict | None = None,
        options: RequestOptions | None = None,
    ) -> builtins.list[WokuRecord]:
        return self._client.request(
            "get", "/v1/action-plan-groups", query=params, options=options
        )

    def get(self, group_id: str, options: RequestOptions | None = None) -> WokuRecord:
        """Get one group with its embedded stats."""
        return self._client.request(
            "get", f"/v1/action-plan-groups/{quote(group_id, safe='')}", options=options
        )

    def create(
        self,
        body: CreateActionPlanGroupParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return self._client.request(
            "post",
            "/v1/action-plan-groups",
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    def update(
        self,
        group_id: str,
        body: UpdateActionPlanGroupParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return self._client.request(
            "patch",
            f"/v1/action-plan-groups/{quote(group_id, safe='')}",
            body=body,
            options=options,
        )

    def set_enabled(
        self,
        group_id: str,
        enabled: bool,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return self._client.request(
            "patch",
            f"/v1/action-plan-groups/{quote(group_id, safe='')}/enabled",
            body={"enabled": enabled},
            options=options,
        )

    def delete(
        self, group_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return self._client.request(
            "delete",
            f"/v1/action-plan-groups/{quote(group_id, safe='')}",
            options=options,
        )


class AsyncActionPlans:
    """Async twin of :class:`ActionPlans`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: ListActionPlansParams | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPage[WokuRecord]:
        return await self._client.get_page("/v1/action-plans", params, options)

    async def get(
        self, plan_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._client.request(
            "get", f"/v1/action-plans/{quote(plan_id, safe='')}", options=options
        )

    async def events(
        self, plan_id: str, options: RequestOptions | None = None
    ) -> builtins.list[WokuRecord]:
        """The plan timeline (events, oldest first)."""
        return await self._client.request(
            "get", f"/v1/action-plans/{quote(plan_id, safe='')}/events", options=options
        )

    async def get_conversation(
        self, plan_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """The plan AI conversation (read-only)."""
        return await self._client.request(
            "get",
            f"/v1/action-plans/{quote(plan_id, safe='')}/conversation",
            options=options,
        )

    async def reply(
        self, plan_id: str, text: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Reply to the plan AI agent (paid turn; ``confirm`` sent automatically)."""
        return await self._client.request(
            "post",
            f"/v1/action-plans/{quote(plan_id, safe='')}/conversation",
            body={"text": text, "confirm": True},
            options=options,
        )

    async def create_task(
        self,
        plan_id: str,
        body: CreateActionPlanTaskParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return await self._client.request(
            "post",
            f"/v1/action-plans/{quote(plan_id, safe='')}/tasks",
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    async def update_task(
        self,
        plan_id: str,
        task_id: str,
        body: UpdateActionPlanTaskParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return await self._client.request(
            "patch",
            (
                f"/v1/action-plans/{quote(plan_id, safe='')}"
                f"/tasks/{quote(task_id, safe='')}"
            ),
            body=body,
            options=options,
        )

    async def reorder_tasks(
        self,
        plan_id: str,
        body: ReorderActionPlanTasksParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return await self._client.request(
            "patch",
            f"/v1/action-plans/{quote(plan_id, safe='')}/tasks/reorder",
            body=body,
            options=options,
        )

    async def delete_task(
        self,
        plan_id: str,
        task_id: str,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return await self._client.request(
            "delete",
            (
                f"/v1/action-plans/{quote(plan_id, safe='')}"
                f"/tasks/{quote(task_id, safe='')}"
            ),
            options=options,
        )

    async def approve(
        self, plan_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._status(plan_id, "approve", options)

    async def reopen(
        self, plan_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._status(plan_id, "reopen", options)

    async def cancel(
        self, plan_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._status(plan_id, "cancel", options)

    async def complete(
        self, plan_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._status(plan_id, "complete", options)

    async def resume(
        self, plan_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._status(plan_id, "resume", options)

    async def _status(
        self, plan_id: str, action: str, options: RequestOptions | None
    ) -> WokuRecord:
        return await self._client.request(
            "post",
            f"/v1/action-plans/{quote(plan_id, safe='')}/{action}",
            options=options,
        )


class AsyncActionPlanGroups:
    """Async twin of :class:`ActionPlanGroups`."""

    def __init__(self, client: AsyncWoku) -> None:
        self._client = client

    async def list(
        self,
        params: dict | None = None,
        options: RequestOptions | None = None,
    ) -> builtins.list[WokuRecord]:
        return await self._client.request(
            "get", "/v1/action-plan-groups", query=params, options=options
        )

    async def get(
        self, group_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        """Get one group with its embedded stats."""
        return await self._client.request(
            "get", f"/v1/action-plan-groups/{quote(group_id, safe='')}", options=options
        )

    async def create(
        self,
        body: CreateActionPlanGroupParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return await self._client.request(
            "post",
            "/v1/action-plan-groups",
            body=body,
            options={**(options or {}), "max_retries": 0},
        )

    async def update(
        self,
        group_id: str,
        body: UpdateActionPlanGroupParams,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return await self._client.request(
            "patch",
            f"/v1/action-plan-groups/{quote(group_id, safe='')}",
            body=body,
            options=options,
        )

    async def set_enabled(
        self,
        group_id: str,
        enabled: bool,
        options: RequestOptions | None = None,
    ) -> WokuRecord:
        return await self._client.request(
            "patch",
            f"/v1/action-plan-groups/{quote(group_id, safe='')}/enabled",
            body={"enabled": enabled},
            options=options,
        )

    async def delete(
        self, group_id: str, options: RequestOptions | None = None
    ) -> WokuRecord:
        return await self._client.request(
            "delete",
            f"/v1/action-plan-groups/{quote(group_id, safe='')}",
            options=options,
        )
