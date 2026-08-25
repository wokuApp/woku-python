"""Resource namespaces (sync and async), one module per API area."""

from __future__ import annotations

from .action_plans import (
    ActionPlanGroups,
    ActionPlans,
    AsyncActionPlanGroups,
    AsyncActionPlans,
)
from .company import AsyncCompany, Company
from .dispatches import AsyncDispatches, Dispatches
from .flows import AsyncFlows, Flows
from .forms import AsyncForms, Forms
from .quarantines import AsyncQuarantines, Quarantines
from .reports import AsyncReports, Reports
from .surveys import AsyncCes, AsyncCsat, AsyncNps, Ces, Csat, Nps
from .tickets import (
    AsyncTicketDestinations,
    AsyncTickets,
    TicketDestinations,
    Tickets,
)
from .trackers import AsyncTrackers, Trackers
from .voc_tools import (
    AsyncCesTools,
    AsyncCsatTools,
    AsyncNpsTools,
    CesTools,
    CsatTools,
    NpsTools,
)
from .wokus import AsyncWokus, Wokus

__all__ = [
    "ActionPlanGroups",
    "ActionPlans",
    "AsyncActionPlanGroups",
    "AsyncActionPlans",
    "AsyncCes",
    "AsyncCesTools",
    "AsyncCompany",
    "AsyncCsat",
    "AsyncCsatTools",
    "AsyncDispatches",
    "AsyncFlows",
    "AsyncForms",
    "AsyncNps",
    "AsyncNpsTools",
    "AsyncQuarantines",
    "AsyncReports",
    "AsyncTicketDestinations",
    "AsyncTickets",
    "AsyncTrackers",
    "AsyncWokus",
    "Ces",
    "CesTools",
    "Company",
    "Csat",
    "CsatTools",
    "Dispatches",
    "Flows",
    "Forms",
    "Nps",
    "NpsTools",
    "Quarantines",
    "Reports",
    "TicketDestinations",
    "Tickets",
    "Trackers",
    "Wokus",
]
