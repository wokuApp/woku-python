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


class Ticket(TypedDict, total=False):
    """Support ticket (curated allow-list)."""

    _id: str
    code: str
    title: str
    severity: Severity
    destinationId: str
    origin: WokuRecord
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
