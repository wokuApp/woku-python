"""Request-body types.

Each alias is the Pydantic v2 model generated from the OpenAPI spec (the source
of truth for validation bounds) unioned with a plain mapping, so call sites can
pass either a typed model instance or a dict literal.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Union

from ._generated import models as _g

#: A plain JSON object accepted anywhere a typed model is.
JsonMapping = Mapping[str, Any]

CreateTrackerParams = Union[_g.CreateExternalTrackerDefinitionDTO, JsonMapping]
UpdateTrackerParams = Union[_g.UpdateExternalTrackerDefinitionDTO, JsonMapping]
SearchEntitiesByTrackersParams = Union[_g.SearchEntitiesByTrackersDTO, JsonMapping]
AssignTrackerByNameParams = Union[_g.AssignExternalTrackerByNameDTO, JsonMapping]

CreateNpsToolParams = Union[_g.CreateNpsToolBodyDTO, JsonMapping]
UpdateNpsToolParams = Union[_g.UpdateNpsToolBodyDTO, JsonMapping]
CreateCsatToolParams = Union[_g.CreateCsatToolBodyDTO, JsonMapping]
UpdateCsatToolParams = Union[_g.UpdateCsatToolBodyDTO, JsonMapping]
CreateCesToolParams = Union[_g.CreateCesToolBodyDTO, JsonMapping]
UpdateCesToolParams = Union[_g.UpdateCesToolBodyDTO, JsonMapping]

SendInvitationsParams = Union[_g.V1CreateInvitationsBodyDto, JsonMapping]
SendNpsInvitationsParams = Union[_g.V1CreateNpsInvitationsBodyDto, JsonMapping]
SendCsatInvitationsParams = Union[_g.V1CreateCsatInvitationsBodyDto, JsonMapping]
SendCesInvitationsParams = Union[_g.V1CreateCesInvitationsBodyDto, JsonMapping]

# CreateWokuApiDto is a multipart form (no JSON schema body), so it is loosely typed.
CreateWokuParams = JsonMapping
UpdateWokuParams = Union[_g.UpdateWokuBodyDTO, JsonMapping]
UpdateWokuSettingsParams = Union[_g.UpdateWokuSettingsBodyDTO, JsonMapping]
MoveWokuParams = Union[_g.MoveWokuBodyDTO, JsonMapping]
ShareWokuParams = Union[_g.V1ShareWokuBodyDto, JsonMapping]

UpdateTicketParams = Union[_g.UpdateTicketBodyDTO, JsonMapping]
CreateTicketDestinationParams = Union[_g.V1CreateTicketDestinationDto, JsonMapping]
UpdateTicketDestinationParams = Union[_g.V1UpdateTicketDestinationDto, JsonMapping]

CreateActionPlanGroupParams = Union[_g.CreateActionPlanGroupDto, JsonMapping]
UpdateActionPlanGroupParams = Union[_g.UpdateActionPlanGroupDto, JsonMapping]
CreateActionPlanTaskParams = Union[_g.CreateActionPlanTaskDto, JsonMapping]
UpdateActionPlanTaskParams = Union[_g.UpdateActionPlanTaskDto, JsonMapping]
ReorderActionPlanTasksParams = Union[_g.ReorderActionPlanTasksDto, JsonMapping]
PostPlanReplyParams = Union[_g.PostPlanReplyBodyDTO, JsonMapping]
