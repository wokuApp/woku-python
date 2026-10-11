"""Response models.

The ``/v1`` controllers return curated, projected documents; these ``TypedDict``
shapes mirror them for editor help. They are permissive (``total=False``) and
are not validated at runtime, matching the structural typing of the JS SDK.
Where the server returns an opaque document the type is :data:`WokuRecord`.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

#: A JSON object the SDK does not exhaustively type.
WokuRecord = dict[str, Any]

FeedbackType = Literal["recognition", "improvement"]
Severity = Literal["high", "medium", "low"]
Locale = Literal["es", "en"]
Channel = Literal["email", "whatsapp"]
DispatchStatus = Literal["invited", "partially_responded", "responded", "failed"]


class Tracker(TypedDict, total=False):
    """External tracker definition (curated)."""

    _id: str
    name: str
    system: str
    description: str | None
    active: bool
    createdAt: str
    updatedAt: str


class EntitiesByTrackers(TypedDict, total=False):
    """Result of a VoC-entity search by tracker filters."""

    entityType: str
    total: int
    matches: list[WokuRecord]


class ToolLocalizedContent(TypedDict, total=False):
    locale: str


class NpsTool(TypedDict, total=False):
    """NPS tool definition (curated, no internal fields)."""

    _id: str
    folderId: str | None
    name: str
    npsMessage: str
    audienceType: str
    availableLocales: list[str]
    defaultLocale: str
    localizedContent: list[ToolLocalizedContent]
    createdAt: str


class CsatTool(TypedDict, total=False):
    """CSAT tool definition (curated)."""

    _id: str
    folderId: str | None
    name: str
    question: str
    subject: str
    availableLocales: list[str]
    defaultLocale: str
    localizedContent: list[ToolLocalizedContent]
    createdAt: str


class CesTool(TypedDict, total=False):
    """CES tool definition (curated)."""

    _id: str
    folderId: str | None
    name: str
    question: str
    action: str
    availableLocales: list[str]
    defaultLocale: str
    localizedContent: list[ToolLocalizedContent]
    createdAt: str


class DeletedResult(TypedDict, total=False):
    """Acknowledgement returned by tool deletes."""

    deleted: bool
    id: str


class RejectedRecipient(TypedDict, total=False):
    recipient: str
    reason: str


class InvitationsResult(TypedDict, total=False):
    """Per-recipient outcome of a survey send."""

    accepted: int
    rejected: int
    rejectedRecipients: list[RejectedRecipient]


FollowUpState = Literal[
    "pending",
    "initial_sent",
    "awaiting_detail",
    "closing",
    "completed",
    "timed_out",
    "cancelled",
]


class FollowUpOrigin(TypedDict, total=False):
    tool: Literal["woku", "nps", "csat", "ces"]
    refId: str
    instrumentId: str


class FollowUp(TypedDict, total=False):
    """Lightweight follow-up state, separate from ticket evidence application."""

    conversationId: str
    state: Literal[
        "not_applicable",
        "pending",
        "initial_sent",
        "awaiting_detail",
        "closing",
        "completed",
        "timed_out",
        "cancelled",
    ]
    reason: str
    availableSummaryVersion: int
    appliedSummaryVersion: int
    enrichedAt: str
    enrichmentState: Literal["processing", "applied", "failed", "skipped"]
    enrichmentReason: str


#: WhatsApp line: ``survey_thread`` (the agent continued the survey chat on the
#: survey number) or ``follow_up_number`` (dedicated number). Absent for email.
FollowUpLine = Literal["survey_thread", "follow_up_number"]

#: ``survey``: the survey exchange before the follow-up (prelude).
#: ``follow_up``: the follow-up itself.
FollowUpMessagePhase = Literal["survey", "follow_up"]


class FollowUpAttachment(TypedDict, total=False):
    """A file the customer sent.

    ``adminUrl`` opens it in the woku admin after login and a company check;
    the file itself and storage URLs are never returned. ``text`` (transcript
    or description) is untrusted customer content.
    """

    index: int
    label: str
    kind: Literal["image", "audio", "document", "unsupported"]
    fileId: str
    readableFileId: str
    filename: str
    mimeType: str
    status: Literal["pending", "ready", "failed", "unsupported"]
    text: str
    failureReason: str
    adminUrl: str


class FollowUpCitation(TypedDict, total=False):
    """A file the executive summary cites as "(Archivo N)"."""

    index: int
    label: str
    fileId: str
    supports: str
    adminUrl: str


class FollowUpMessage(TypedDict, total=False):
    role: Literal["agent", "client"]
    #: May be empty when the message only has files.
    content: str
    timestamp: str
    phase: FollowUpMessagePhase
    responseType: str
    selectedOption: str
    attachments: list[FollowUpAttachment]


class FollowUpConversation(TypedDict, total=False):
    """Authorized conversation without response tokens or transport credentials."""

    _id: str
    companyId: str
    origin: FollowUpOrigin
    wokuId: str
    reviewId: str
    reviewType: Literal["textnote", "voicemail"]
    originalReview: str
    originalQualification: int
    state: FollowUpState
    channel: Channel
    line: FollowUpLine
    reason: str
    messages: list[FollowUpMessage]
    executiveSummary: str
    actionItems: list[str]
    sentiment: str
    topics: list[str]
    summaryCitations: list[FollowUpCitation]
    summaryVersion: int
    createdAt: str
    updatedAt: str


class TicketOriginTracker(TypedDict, total=False):
    trackerId: str
    name: str
    value: str


class TicketOrigin(TypedDict, total=False):
    tool: Literal["woku", "nps", "csat", "ces", "form"]
    refId: str
    instrumentId: str
    instrumentName: str
    trackers: list[TicketOriginTracker]


class Ticket(TypedDict, total=False):
    """Support ticket (curated allow-list)."""

    _id: str
    code: str
    title: str
    severity: Severity
    destinationId: str
    origin: TicketOrigin
    followUp: FollowUp
    contentVersion: int
    score: WokuRecord
    aiSummary: str
    aiCategory: str
    sentiment: str
    client: WokuRecord
    customerComment: WokuRecord
    timeline: list[WokuRecord]
    createdAt: str
    updatedAt: str


class SeverityBreakdown(TypedDict, total=False):
    high: int
    medium: int
    low: int


class TicketStatsByDestination(TypedDict, total=False):
    destinationId: str
    countInPeriod: int
    countTotal: int
    severity: SeverityBreakdown


class TicketStats(TypedDict, total=False):
    """Ticket aggregate counts."""

    byTool: dict[str, int]
    byDestination: list[TicketStatsByDestination]


class DispatchTarget(TypedDict, total=False):
    responseType: str
    targetId: str
    respondedAt: str | None


class DispatchAttempt(TypedDict, total=False):
    channel: Channel
    attemptIndex: int
    sentAt: str
    status: Literal["sent", "delivered", "bounced", "failed"]


class Dispatch(TypedDict, total=False):
    """One outbound invitation dispatch (delivery view, no recipient PII)."""

    _id: str
    channel: Channel
    source: str | None
    status: DispatchStatus
    targets: list[DispatchTarget]
    attempts: list[DispatchAttempt]
    createdAt: str
    updatedAt: str


class DispatchByStatus(TypedDict, total=False):
    invited: int
    partially_responded: int
    responded: int
    failed: int


class DispatchStats(TypedDict, total=False):
    """Response-rate metrics over the dispatches."""

    total: int
    delivered: int
    byStatus: DispatchByStatus
    responseRate: float | None


class Woku(TypedDict, total=False):
    """A woku (feedback collection tool), curated."""

    _id: str
    description: str
    folderId: str | None
    closed: bool
    reviewsDisabled: bool
    anonymousDisabled: bool
    onlyOneReviewPerClient: bool
    availableLocales: list[str]
    defaultLocale: str
    createdAt: str


class TestConnectionResult(TypedDict, total=False):
    """Sanitized ticket-destination connectivity test result."""

    ok: bool
    status: int
    message: str


class ApiKeyResult(TypedDict, total=False):
    """Rotated secret key."""

    secretKey: str


ToolType = Literal["woku", "nps", "csat", "ces"]


class ToolHeadline(TypedDict, total=False):
    """Headline figure of a tool, always in its native scale (never mixed)."""

    kind: Literal["stars", "nps", "csat", "ces"]
    #: Stars 1-5, NPS -100..100, CSAT satisfied %, CES mean 1-5; None without responses.
    value: float | None
    scale: str


class ToolItem(TypedDict, total=False):
    """A woku, NPS, CSAT or CES tool as listed by ``tools.list``."""

    type: ToolType
    id: str
    name: str
    folderId: str | None
    createdAt: str | None
    reviewCount: int
    lastResponseAt: str | None
    headline: ToolHeadline


class FolderStats(TypedDict, total=False):
    """Subtree figures of a folder."""

    toolCounts: dict[str, int]
    subfolderCount: int
    reviewCount: int


class Folder(TypedDict, total=False):
    """A folder with its breadcrumb path and subtree stats."""

    id: str
    name: str
    color: str | None
    parentFolderId: str | None
    #: Breadcrumb from the root, for example ``Journeys > Post-sale``.
    path: str
    #: System folder kind (``journeys-root``, ``journey``, ``journey-moment`` or
    #: ``integration``); None for a folder you created.
    origin: str | None
    #: WhatsApp numbers alerted when a comment of any tool in the folder is an
    #: improvement: ``whatsappId`` (no leading +), ``name`` and ``sources`` (which
    #: of ``woku``, ``nps``, ``csat`` and ``ces`` alert that number).
    whatsappAlertRecipients: list[dict[str, Any]]
    createdAt: str | None
    stats: FolderStats


class ToolTypeStats(TypedDict, total=False):
    """Headline figures of one tool type for the company or a folder."""

    toolCount: int
    reviewCount: int
    headline: ToolHeadline
    lastResponseAt: str | None
    #: NPS only: promoters, passives and detractors.
    distribution: dict[str, int]
    #: Set (to True) instead of the figures when this type failed to compute.
    error: bool


#: Figures per type; a type that fails reports ``{"error": True}``.
ToolsStats = dict[str, ToolTypeStats]


class MoveResult(TypedDict, total=False):
    """Result of ``tools.move``."""

    moved: int
    folderId: str | None
    items: list[dict[str, str]]


class JourneyFoldersStatus(TypedDict, total=False):
    """Whether journeys are kept in folders (``Viajes > journey > moment``)."""

    enabled: bool
    enabledAt: str | None
    organizedAt: str | None
    #: True while the one-off organization runs in the background.
    organizing: bool
    #: Journeys and tools still without a folder.
    pending: dict[str, int]


class FlowStep(TypedDict, total=False):
    """One step of a flow: the tool the respondent answers at that point."""

    type: ToolType
    #: Tool id. For an ``nps`` step, your company id means the company-level NPS.
    toolId: str


class Flow(TypedDict, total=False):
    """A survey flow: an ordered sequence of woku, NPS, CSAT and CES steps."""

    _id: str
    name: str
    #: Ordered steps. Flows live outside folders.
    steps: list[FlowStep]
    #: Woku ids of the ``woku`` steps, in order (kept for compatibility).
    wokusIds: list[str]
    npsToolId: str | None
    companyIdNps: str | None
    createdAt: str
    updatedAt: str
