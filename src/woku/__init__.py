"""woku - official server-side SDK for the Woku management API.

Authenticate with your company secret key and manage trackers, VoC tools
(NPS/CSAT/CES), wokus, forms, flows, action plans, tickets, delivery and
captures over the public ``/v1`` API.

::

    from woku import Woku

    woku = Woku(api_key="sk_...")
    tracker = woku.trackers.create({"name": "Store", "system": "retail"})
"""

from __future__ import annotations

from ._client import AsyncWoku, Woku
from ._exceptions import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PayloadTooLargeError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
    WokuAPIError,
    WokuConnectionError,
    WokuError,
    WokuTimeoutError,
)
from ._options import RequestOptions
from ._pagination import AsyncPage, PageResponse, SyncPage
from ._version import __version__
from .models import (
    FollowUp,
    FollowUpAttachment,
    FollowUpCitation,
    FollowUpConversation,
    FollowUpLine,
    FollowUpMessage,
    FollowUpMessagePhase,
    FollowUpOrigin,
    FollowUpState,
    TicketOrigin,
    TicketOriginTracker,
)
from .resources.folder_participants import AsyncFolderParticipants, FolderParticipants
from .resources.folders import AsyncFolders, Folders
from .resources.follow_ups import AsyncFollowUps, FollowUps
from .resources.journey_folders import AsyncJourneyFolders, JourneyFolders
from .resources.report_subscriptions import (
    AsyncReportSubscriptions,
    ReportSubscriptions,
)
from .resources.tools import AsyncTools, AsyncToolsPage, Tools, ToolsPage
from .types import CustomTicketDestinationConfig, CustomTicketUpdateConfig

__all__ = [
    "AsyncFolderParticipants",
    "FolderParticipants",
    "AsyncReportSubscriptions",
    "ReportSubscriptions",
    "AsyncJourneyFolders",
    "JourneyFolders",
    "AsyncFolders",
    "AsyncTools",
    "AsyncToolsPage",
    "Folders",
    "Tools",
    "ToolsPage",
    "AsyncPage",
    "CustomTicketDestinationConfig",
    "CustomTicketUpdateConfig",
    "AsyncFollowUps",
    "FollowUps",
    "FollowUp",
    "FollowUpAttachment",
    "FollowUpCitation",
    "FollowUpConversation",
    "FollowUpLine",
    "FollowUpMessage",
    "FollowUpMessagePhase",
    "FollowUpOrigin",
    "FollowUpState",
    "TicketOrigin",
    "TicketOriginTracker",
    "AsyncWoku",
    "AuthenticationError",
    "BadRequestError",
    "ConflictError",
    "InternalServerError",
    "NotFoundError",
    "PageResponse",
    "PermissionDeniedError",
    "PayloadTooLargeError",
    "RateLimitError",
    "RequestOptions",
    "SyncPage",
    "UnprocessableEntityError",
    "Woku",
    "WokuAPIError",
    "WokuConnectionError",
    "WokuError",
    "WokuTimeoutError",
    "__version__",
]
