"""Pydantic models for Favro API entities."""

from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


# Generic type for paginated responses
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated API response wrapper."""

    limit: int
    page: int
    pages: int
    request_id: str = Field(alias="requestId")
    entities: list[T]

    model_config = ConfigDict(populate_by_name=True)


class Organization(BaseModel):
    """Favro organization."""

    organization_id: str = Field(alias="organizationId")
    name: str
    shared_to_users: list[dict[str, str]] = Field(default=[], alias="sharedToUsers")

    model_config = ConfigDict(populate_by_name=True)


class Collection(BaseModel):
    """Favro collection (dashboard)."""

    collection_id: str = Field(alias="collectionId")
    organization_id: str = Field(alias="organizationId")
    name: str
    shared_to_users: list[dict[str, str]] = Field(default=[], alias="sharedToUsers")
    public_sharing: str | None = Field(default=None, alias="publicSharing")
    background: str | None = None
    archived: bool = False
    widget_common_ids: list[str] = Field(default=[], alias="widgetCommonIds")

    model_config = ConfigDict(populate_by_name=True)


class Widget(BaseModel):
    """Favro widget (board/backlog)."""

    widget_common_id: str = Field(alias="widgetCommonId")
    organization_id: str = Field(alias="organizationId")
    collection_ids: list[str] = Field(default=[], alias="collectionIds")
    name: str
    type: str  # "board" or "backlog"
    public_sharing: str | None = Field(default=None, alias="publicSharing")
    color: str | None = None
    owner_role: str | None = Field(default=None, alias="ownerRole")
    editing_role: str | None = Field(default=None, alias="editingRole")
    archived: bool = False

    model_config = ConfigDict(populate_by_name=True)


class Column(BaseModel):
    """Favro column in a widget."""

    column_id: str = Field(alias="columnId")
    organization_id: str = Field(alias="organizationId")
    widget_common_id: str = Field(alias="widgetCommonId")
    name: str
    position: float = 0
    card_count: int = Field(default=0, alias="cardCount")
    time_sum: int | None = Field(default=None, alias="timeSum")
    estimation_sum: float | None = Field(default=None, alias="estimationSum")

    model_config = ConfigDict(populate_by_name=True)


class CustomFieldValue(BaseModel):
    """Custom field value on a card."""

    custom_field_id: str = Field(alias="customFieldId")
    value: str | int | float | bool | list[str] | dict[str, int | float | str] | None = None
    total: float | None = None
    link: dict[str, str] | None = None
    members: list[str] | None = None

    model_config = ConfigDict(populate_by_name=True)


class CardAssignment(BaseModel):
    """User assignment on a card."""

    user_id: str = Field(alias="userId")
    completed: bool = False

    model_config = ConfigDict(populate_by_name=True)


class Attachment(BaseModel):
    """Card attachment."""

    name: str
    file_url: str = Field(alias="fileURL")
    thumbnail_url: str | None = Field(default=None, alias="thumbnailURL")

    model_config = ConfigDict(populate_by_name=True)


class Card(BaseModel):
    """Favro card."""

    card_id: str = Field(alias="cardId")
    card_common_id: str = Field(alias="cardCommonId")
    organization_id: str = Field(alias="organizationId")
    widget_common_id: str = Field(alias="widgetCommonId")
    column_id: str | None = Field(default=None, alias="columnId")
    lane_id: str | None = Field(default=None, alias="laneId")
    parent_card_id: str | None = Field(default=None, alias="parentCardId")
    is_lane: bool = Field(default=False, alias="isLane")
    archived: bool = False
    position: float = 0
    list_position: float = Field(default=0, alias="listPosition")
    name: str
    detailed_description: str | None = Field(default=None, alias="detailedDescription")
    tags: list[str] = Field(default=[])
    sequential_id: int = Field(alias="sequentialId")
    start_date: datetime | None = Field(default=None, alias="startDate")
    due_date: datetime | None = Field(default=None, alias="dueDate")
    assignments: list[CardAssignment] = Field(default=[])
    num_comments: int = Field(default=0, alias="numComments")
    tasks_done: int = Field(default=0, alias="tasksDone")
    tasks_total: int = Field(default=0, alias="tasksTotal")
    attachments: list[Attachment] = Field(default=[])
    custom_fields: list[CustomFieldValue] = Field(default=[], alias="customFields")
    time_on_board: dict[str, int | bool] | None = Field(default=None, alias="timeOnBoard")
    time_on_columns: dict[str, int] | None = Field(default=None, alias="timeOnColumns")
    favro_attachments: list[dict[str, str]] = Field(default=[], alias="favroAttachments")

    model_config = ConfigDict(populate_by_name=True)


class Tag(BaseModel):
    """Favro tag."""

    tag_id: str = Field(alias="tagId")
    organization_id: str = Field(alias="organizationId")
    name: str
    color: str

    model_config = ConfigDict(populate_by_name=True)


class Comment(BaseModel):
    """Favro comment on a card."""

    comment_id: str = Field(alias="commentId")
    card_common_id: str = Field(alias="cardCommonId")
    organization_id: str = Field(alias="organizationId")
    user_id: str = Field(alias="userId")
    comment: str
    created: datetime
    last_updated: datetime | None = Field(default=None, alias="lastUpdated")

    model_config = ConfigDict(populate_by_name=True)


class Task(BaseModel):
    """Favro task in a card's tasklist."""

    task_id: str = Field(alias="taskId")
    card_common_id: str = Field(alias="cardCommonId")
    organization_id: str = Field(alias="organizationId")
    name: str
    completed: bool = False
    position: int = 0

    model_config = ConfigDict(populate_by_name=True)


class User(BaseModel):
    """Favro user."""

    user_id: str = Field(alias="userId")
    name: str
    email: str
    organization_role: str = Field(alias="organizationRole")

    model_config = ConfigDict(populate_by_name=True)


class CustomField(BaseModel):
    """Favro custom field definition."""

    custom_field_id: str = Field(alias="customFieldId")
    organization_id: str = Field(alias="organizationId")
    name: str
    type: str
    enabled: bool = True
    custom_field_items: list[dict[str, str]] = Field(default=[], alias="customFieldItems")

    model_config = ConfigDict(populate_by_name=True)


# Request models for creating/updating entities


class CardCreateRequest(BaseModel):
    """Request body for creating a card."""

    name: str
    widget_common_id: str = Field(alias="widgetCommonId")
    column_id: str | None = Field(default=None, alias="columnId")
    lane_id: str | None = Field(default=None, alias="laneId")
    parent_card_id: str | None = Field(default=None, alias="parentCardId")
    detailed_description: str | None = Field(default=None, alias="detailedDescription")
    position: int | None = None
    list_position: int | None = Field(default=None, alias="listPosition")
    tags: list[str] | None = None
    tag_names: list[str] | None = Field(default=None, alias="tagNames")
    start_date: str | None = Field(default=None, alias="startDate")
    due_date: str | None = Field(default=None, alias="dueDate")
    assignments: list[str] | None = None
    custom_fields: list[dict[str, str | int | float | bool]] | None = Field(
        default=None, alias="customFields"
    )

    model_config = ConfigDict(populate_by_name=True)


class CardUpdateRequest(BaseModel):
    """Request body for updating a card."""

    name: str | None = None
    detailed_description: str | None = Field(default=None, alias="detailedDescription")
    widget_common_id: str | None = Field(default=None, alias="widgetCommonId")
    column_id: str | None = Field(default=None, alias="columnId")
    lane_id: str | None = Field(default=None, alias="laneId")
    parent_card_id: str | None = Field(default=None, alias="parentCardId")
    position: int | None = None
    list_position: int | None = Field(default=None, alias="listPosition")
    archived: bool | None = None
    add_tags: list[str] | None = Field(default=None, alias="addTags")
    add_tag_names: list[str] | None = Field(default=None, alias="addTagNames")
    remove_tags: list[str] | None = Field(default=None, alias="removeTags")
    start_date: str | None = Field(default=None, alias="startDate")
    due_date: str | None = Field(default=None, alias="dueDate")
    add_assignments: list[str] | None = Field(default=None, alias="addAssignments")
    remove_assignments: list[str] | None = Field(default=None, alias="removeAssignments")
    custom_fields: list[dict[str, str | int | float | bool]] | None = Field(
        default=None, alias="customFields"
    )

    model_config = ConfigDict(populate_by_name=True)


class CommentCreateRequest(BaseModel):
    """Request body for creating a comment."""

    card_common_id: str = Field(alias="cardCommonId")
    comment: str

    model_config = ConfigDict(populate_by_name=True)
