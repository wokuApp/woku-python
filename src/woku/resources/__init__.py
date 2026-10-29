"""Resource namespaces (sync and async), one module per API area."""

from __future__ import annotations

from .action_plans import (
    ActionPlanGroups,
    ActionPlans,
    AsyncActionPlanGroups,
    AsyncActionPlans,
)
from .company import AsyncCompany, Company
from .data_apps import AsyncDataApps, DataApps
from .dispatches import AsyncDispatches, Dispatches
from .flows import AsyncFlows, Flows
from .follow_ups import AsyncFollowUps, FollowUps
from .forms import AsyncForms, Forms
from .journeys import AsyncJourneys, Journeys
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
    "AsyncDataApps",
    "AsyncFollowUps",
    "AsyncForms",
    "AsyncNps",
    "AsyncNpsTools",
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
    "DataApps",
    "FollowUps",
    "Forms",
    "Nps",
    "NpsTools",
    "Journeys",
    "AsyncJourneys",
    "Reports",
    "TicketDestinations",
    "Tickets",
    "Trackers",
    "Wokus",
]
