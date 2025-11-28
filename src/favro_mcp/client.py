"""Async HTTP client for Favro API."""

from __future__ import annotations

import asyncio
import base64
import logging
from typing import Any, TypeVar

import httpx

from favro_mcp.models import (
    Card,
    Collection,
    Column,
    Comment,
    CustomField,
    Organization,
    Tag,
    User,
    Widget,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")

BASE_URL = "https://favro.com/api/v1"


class FavroAPIError(Exception):
    """Base exception for Favro API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(FavroAPIError):
    """Rate limit exceeded error."""

    def __init__(self, reset_time: int | None = None) -> None:
        super().__init__("Rate limit exceeded", status_code=429)
        self.reset_time = reset_time


class FavroClient:
    """Async client for Favro REST API."""

    def __init__(
        self,
        email: str,
        api_token: str,
        organization_id: str | None = None,
    ) -> None:
        """Initialize Favro client.

        Args:
            email: User email for authentication
            api_token: API token from Favro settings
            organization_id: Default organization ID (optional)
        """
        self._email = email
        self._api_token = api_token
        self._organization_id = organization_id
        self._backend_id: str | None = None
        self._client: httpx.AsyncClient | None = None

    @property
    def organization_id(self) -> str | None:
        """Get current organization ID."""
        return self._organization_id

    @organization_id.setter
    def organization_id(self, value: str | None) -> None:
        """Set organization ID for subsequent requests."""
        self._organization_id = value

    def _get_auth_header(self) -> str:
        """Generate Basic auth header value."""
        credentials = f"{self._email}:{self._api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _get_headers(self, include_org: bool = True) -> dict[str, str]:
        """Get headers for API request."""
        headers: dict[str, str] = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json",
        }
        if include_org and self._organization_id:
            headers["organizationId"] = self._organization_id
        if self._backend_id:
            headers["X-Favro-Backend-Identifier"] = self._backend_id
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=BASE_URL,
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        include_org: bool = True,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        retry_count: int = 3,
    ) -> dict[str, Any]:
        """Make API request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            include_org: Whether to include organizationId header
            params: Query parameters
            json_data: JSON body data
            retry_count: Number of retries for rate limit errors

        Returns:
            JSON response data

        Raises:
            FavroAPIError: On API errors
            RateLimitError: On rate limit exceeded (after retries)
        """
        client = await self._get_client()
        headers = self._get_headers(include_org=include_org)

        for attempt in range(retry_count):
            try:
                response = await client.request(
                    method,
                    endpoint,
                    headers=headers,
                    params=params,
                    json=json_data,
                )

                # Track backend identifier for consistency
                if "X-Favro-Backend-Identifier" in response.headers:
                    self._backend_id = response.headers["X-Favro-Backend-Identifier"]

                # Handle rate limiting
                if response.status_code == 429:
                    reset_time = response.headers.get("X-RateLimit-Reset")
                    if attempt < retry_count - 1:
                        wait_seconds = min(2 ** (attempt + 1), 60)
                        logger.warning(
                            f"Rate limited, waiting {wait_seconds}s before retry "
                            f"(attempt {attempt + 1}/{retry_count})"
                        )
                        await asyncio.sleep(wait_seconds)
                        continue
                    raise RateLimitError(reset_time=int(reset_time) if reset_time else None)

                # Handle other errors
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                        message = error_data.get("message", response.text)
                    except Exception:
                        message = response.text
                    raise FavroAPIError(message, status_code=response.status_code)

                # Return empty dict for 204 No Content
                if response.status_code == 204:
                    return {}

                data: dict[str, Any] = response.json()

                # Handle API errors returned with 200 OK status
                # Favro sometimes returns {"message": "..."} for errors
                if "message" in data and len(data) == 1:
                    raise FavroAPIError(str(data["message"]), status_code=response.status_code)

                return data

            except httpx.RequestError as e:
                if attempt < retry_count - 1:
                    wait_seconds = 2 ** (attempt + 1)
                    logger.warning(
                        f"Request error: {e}, retrying in {wait_seconds}s "
                        f"(attempt {attempt + 1}/{retry_count})"
                    )
                    await asyncio.sleep(wait_seconds)
                    continue
                raise FavroAPIError(f"Request failed: {e}") from e

        raise FavroAPIError("Max retries exceeded")

    async def _get_all_pages(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch all pages from a paginated endpoint.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            List of all entities from all pages
        """
        all_entities: list[dict[str, Any]] = []
        params = params or {}
        request_id: str | None = None
        page = 0

        while True:
            if request_id:
                params["requestId"] = request_id
                params["page"] = page

            data = await self._request("GET", endpoint, params=params)

            entities = data.get("entities", [])
            all_entities.extend(entities)

            # Check if there are more pages
            pages = data.get("pages", 1)
            if page >= pages - 1:
                break

            request_id = data.get("requestId")
            if not request_id:
                break
            page += 1

        return all_entities

    # Organization endpoints

    async def get_organizations(self) -> list[Organization]:
        """Get all organizations the user has access to."""
        data = await self._request("GET", "/organizations", include_org=False)
        entities = data.get("entities", [])
        return [Organization.model_validate(e) for e in entities]

    async def get_organization(self, organization_id: str) -> Organization:
        """Get a specific organization."""
        data = await self._request(
            "GET",
            f"/organizations/{organization_id}",
            include_org=False,
        )
        return Organization.model_validate(data)

    # Collection endpoints

    async def get_collections(self) -> list[Collection]:
        """Get all collections in the organization."""
        entities = await self._get_all_pages("/collections")
        return [Collection.model_validate(e) for e in entities]

    async def get_collection(self, collection_id: str) -> Collection:
        """Get a specific collection."""
        data = await self._request("GET", f"/collections/{collection_id}")
        return Collection.model_validate(data)

    # Widget endpoints

    async def get_widgets(self, collection_id: str | None = None) -> list[Widget]:
        """Get all widgets (boards/backlogs).

        Args:
            collection_id: Optional filter by collection
        """
        params: dict[str, Any] = {}
        if collection_id:
            params["collectionId"] = collection_id
        entities = await self._get_all_pages("/widgets", params=params)
        return [Widget.model_validate(e) for e in entities]

    async def get_widget(self, widget_common_id: str) -> Widget:
        """Get a specific widget."""
        data = await self._request("GET", f"/widgets/{widget_common_id}")
        return Widget.model_validate(data)

    # Column endpoints

    async def get_columns(self, widget_common_id: str) -> list[Column]:
        """Get all columns for a widget."""
        params = {"widgetCommonId": widget_common_id}
        entities = await self._get_all_pages("/columns", params=params)
        return [Column.model_validate(e) for e in entities]

    async def get_column(self, column_id: str) -> Column:
        """Get a specific column."""
        data = await self._request("GET", f"/columns/{column_id}")
        return Column.model_validate(data)

    # Card endpoints

    async def get_cards(
        self,
        *,
        widget_common_id: str | None = None,
        collection_id: str | None = None,
        card_common_id: str | None = None,
        card_sequential_id: int | None = None,
    ) -> list[Card]:
        """Get cards with filters.

        At least one filter is required:
        - widget_common_id
        - collection_id
        - card_common_id
        - card_sequential_id
        """
        params: dict[str, Any] = {}
        if widget_common_id:
            params["widgetCommonId"] = widget_common_id
        if collection_id:
            params["collectionId"] = collection_id
        if card_common_id:
            params["cardCommonId"] = card_common_id
        if card_sequential_id:
            params["cardSequentialId"] = card_sequential_id

        if not params:
            raise ValueError("At least one filter parameter is required for get_cards")

        entities = await self._get_all_pages("/cards", params=params)
        return [Card.model_validate(e) for e in entities]

    async def get_card(self, card_id: str) -> Card:
        """Get a specific card by ID."""
        data = await self._request("GET", f"/cards/{card_id}")
        return Card.model_validate(data)

    async def create_card(
        self,
        name: str,
        widget_common_id: str,
        *,
        column_id: str | None = None,
        detailed_description: str | None = None,
        position: int | None = None,
        tags: list[str] | None = None,
        start_date: str | None = None,
        due_date: str | None = None,
        assignments: list[str] | None = None,
    ) -> Card:
        """Create a new card.

        Args:
            name: Card name/title
            widget_common_id: Widget to create card in
            column_id: Optional column ID
            detailed_description: Card description (markdown)
            position: Position in column
            tags: List of tag IDs
            start_date: Start date (ISO format)
            due_date: Due date (ISO format)
            assignments: List of user IDs to assign
        """
        json_data: dict[str, Any] = {
            "name": name,
            "widgetCommonId": widget_common_id,
        }
        if column_id:
            json_data["columnId"] = column_id
        if detailed_description:
            json_data["detailedDescription"] = detailed_description
        if position is not None:
            json_data["position"] = position
        if tags:
            json_data["tags"] = tags
        if start_date:
            json_data["startDate"] = start_date
        if due_date:
            json_data["dueDate"] = due_date
        if assignments:
            json_data["assignments"] = assignments

        data = await self._request("POST", "/cards", json_data=json_data)
        return Card.model_validate(data)

    async def update_card(
        self,
        card_id: str,
        *,
        name: str | None = None,
        detailed_description: str | None = None,
        widget_common_id: str | None = None,
        column_id: str | None = None,
        position: int | None = None,
        archived: bool | None = None,
        add_tags: list[str] | None = None,
        remove_tags: list[str] | None = None,
        start_date: str | None = None,
        due_date: str | None = None,
        add_assignments: list[str] | None = None,
        remove_assignments: list[str] | None = None,
    ) -> Card:
        """Update an existing card.

        Args:
            card_id: Card ID to update
            name: New name
            detailed_description: New description
            widget_common_id: Move to different widget
            column_id: Move to different column
            position: New position
            archived: Archive/unarchive
            add_tags: Tags to add
            remove_tags: Tags to remove
            start_date: New start date
            due_date: New due date
            add_assignments: Users to assign
            remove_assignments: Users to unassign
        """
        json_data: dict[str, Any] = {}
        if name is not None:
            json_data["name"] = name
        if detailed_description is not None:
            json_data["detailedDescription"] = detailed_description
        if widget_common_id:
            json_data["widgetCommonId"] = widget_common_id
        if column_id:
            json_data["columnId"] = column_id
        if position is not None:
            json_data["position"] = position
        if archived is not None:
            json_data["archived"] = archived
        if add_tags:
            json_data["addTags"] = add_tags
        if remove_tags:
            json_data["removeTags"] = remove_tags
        if start_date:
            json_data["startDate"] = start_date
        if due_date:
            json_data["dueDate"] = due_date
        if add_assignments:
            json_data["addAssignments"] = add_assignments
        if remove_assignments:
            json_data["removeAssignments"] = remove_assignments

        data = await self._request("PUT", f"/cards/{card_id}", json_data=json_data)
        return Card.model_validate(data)

    async def delete_card(self, card_id: str, *, everywhere: bool = False) -> None:
        """Delete a card.

        Args:
            card_id: Card ID to delete
            everywhere: If True, delete from all widgets
        """
        params: dict[str, Any] = {}
        if everywhere:
            params["everywhere"] = "true"
        await self._request("DELETE", f"/cards/{card_id}", params=params)

    # Comment endpoints

    async def get_comments(self, card_common_id: str) -> list[Comment]:
        """Get comments for a card."""
        params = {"cardCommonId": card_common_id}
        entities = await self._get_all_pages("/comments", params=params)
        return [Comment.model_validate(e) for e in entities]

    async def create_comment(self, card_common_id: str, comment: str) -> Comment:
        """Create a comment on a card.

        Args:
            card_common_id: Card to comment on
            comment: Comment text
        """
        json_data = {
            "cardCommonId": card_common_id,
            "comment": comment,
        }
        data = await self._request("POST", "/comments", json_data=json_data)
        return Comment.model_validate(data)

    # Tag endpoints

    async def get_tags(self) -> list[Tag]:
        """Get all tags in the organization."""
        entities = await self._get_all_pages("/tags")
        return [Tag.model_validate(e) for e in entities]

    # User endpoints

    async def get_users(self) -> list[User]:
        """Get all users in the organization."""
        entities = await self._get_all_pages("/users")
        return [User.model_validate(e) for e in entities]

    # Custom field endpoints

    async def get_custom_fields(self) -> list[CustomField]:
        """Get all custom fields in the organization."""
        entities = await self._get_all_pages("/customfields")
        return [CustomField.model_validate(e) for e in entities]
