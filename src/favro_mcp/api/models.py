"""Pydantic models for Favro API responses."""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    limit: int
    page: int
    pages: int
    request_id: str = Field(alias="requestId")
    entities: list[T]


class User(BaseModel):
    """User model."""

    user_id: str = Field(alias="userId")
    name: str
    email: str
    organization_role: str | None = Field(default=None, alias="organizationRole")


class OrganizationMember(BaseModel):
    """Organization member model."""

    user_id: str = Field(alias="userId")
    role: str
    join_date: datetime | None = Field(default=None, alias="joinDate")


class Organization(BaseModel):
    """Organization model."""

    organization_id: str = Field(alias="organizationId")
    name: str
    thumbnail: str | None = None
    shared_to_users: list[OrganizationMember] = Field(default=[], alias="sharedToUsers")


class Collection(BaseModel):
    """Collection model."""

    collection_id: str = Field(alias="collectionId")
    organization_id: str = Field(alias="organizationId")
    name: str
    archived: bool = False
    background: str | None = None
    public_sharing: str | None = Field(default=None, alias="publicSharing")


class Widget(BaseModel):
    """Widget (board) model."""

    widget_common_id: str = Field(alias="widgetCommonId")
    organization_id: str = Field(alias="organizationId")
    collection_ids: list[str] = Field(default_factory=list, alias="collectionIds")
    name: str
    type: str  # "board" or "backlog"
    color: str | None = None
    owner_role: str | None = Field(default=None, alias="ownerRole")
    edit_role: str | None = Field(default=None, alias="editRole")
    archived: bool = False
    breakdown_card_common_id: str | None = Field(
        default=None, alias="breakdownCardCommonId"
    )


class Column(BaseModel):
    """Column model."""

    column_id: str = Field(alias="columnId")
    organization_id: str = Field(alias="organizationId")
    widget_common_id: str = Field(alias="widgetCommonId")
    name: str
    position: float
    card_count: int = Field(default=0, alias="cardCount")
    time_sum: int | None = Field(default=None, alias="timeSum")
    estimation_sum: float | None = Field(default=None, alias="estimationSum")


class CardAssignment(BaseModel):
    """Card assignment model."""

    user_id: str = Field(alias="userId")
    completed: bool = False


class CardCustomField(BaseModel):
    """Card custom field value."""

    custom_field_id: str = Field(alias="customFieldId")
    value: str | int | float | list[str] | dict[str, Any] | None = None
    total: float | None = None
    link: dict[str, str] | None = None
    members: list[str] | None = None
    status: str | None = None
    color: str | None = None


class CardTimeOnBoard(BaseModel):
    """Time card has spent on board."""

    time: int  # milliseconds
    is_stopped: bool = Field(default=False, alias="isStopped")


class Card(BaseModel):
    """Card model."""

    card_id: str = Field(alias="cardId")
    organization_id: str = Field(alias="organizationId")
    card_common_id: str = Field(alias="cardCommonId")
    name: str
    sequential_id: int = Field(alias="sequentialId")
    widget_common_id: str | None = Field(default=None, alias="widgetCommonId")
    column_id: str | None = Field(default=None, alias="columnId")
    lane_id: str | None = Field(default=None, alias="laneId")
    parent_card_id: str | None = Field(default=None, alias="parentCardId")
    is_lane: bool = Field(default=False, alias="isLane")
    archived: bool = False
    detailed_description: str | None = Field(default=None, alias="detailedDescription")
    tags: list[str] = Field(default_factory=list)
    start_date: datetime | None = Field(default=None, alias="startDate")
    due_date: datetime | None = Field(default=None, alias="dueDate")
    assignments: list[CardAssignment] = Field(default=[])
    num_comments: int = Field(default=0, alias="numComments")
    tasks_total: int = Field(default=0, alias="tasksTotal")
    tasks_done: int = Field(default=0, alias="tasksDone")
    custom_fields: list[CardCustomField] = Field(default=[], alias="customFields")
    time_on_board: CardTimeOnBoard | None = Field(default=None, alias="timeOnBoard")
    todo_list_user_id: str | None = Field(default=None, alias="todoListUserId")
    todo_list_completed: bool | None = Field(default=None, alias="todoListCompleted")
    list_position: float | None = Field(default=None, alias="listPosition")
    sheet_position: float | None = Field(default=None, alias="sheetPosition")


class Tag(BaseModel):
    """Tag model."""

    tag_id: str = Field(alias="tagId")
    organization_id: str = Field(alias="organizationId")
    name: str
    color: str | None = None


class Comment(BaseModel):
    """Comment model."""

    comment_id: str = Field(alias="commentId")
    card_common_id: str = Field(alias="cardCommonId")
    organization_id: str = Field(alias="organizationId")
    user_id: str = Field(alias="userId")
    comment: str
    created: datetime
    last_updated: datetime | None = Field(default=None, alias="lastUpdated")


class TaskList(BaseModel):
    """Task list (checklist) model."""

    tasklist_id: str = Field(alias="taskListId")
    organization_id: str = Field(alias="organizationId")
    card_common_id: str = Field(alias="cardCommonId")
    name: str
    position: int


class Task(BaseModel):
    """Task (checklist item) model."""

    task_id: str = Field(alias="taskId")
    tasklist_id: str = Field(alias="taskListId")
    organization_id: str = Field(alias="organizationId")
    card_common_id: str = Field(alias="cardCommonId")
    name: str
    completed: bool
    position: int
