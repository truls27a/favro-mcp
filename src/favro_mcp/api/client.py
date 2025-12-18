"""Favro API client."""

from typing import Any, TypeVar

import httpx

from favro_mcp.api.models import (
    Card,
    Collection,
    Column,
    Organization,
    Tag,
    User,
    Widget,
)

T = TypeVar("T")

BASE_URL = "https://favro.com/api/v1"


class FavroAPIError(Exception):
    """Base exception for Favro API errors."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


class FavroAuthError(FavroAPIError):
    """Authentication error."""

    pass


class FavroNotFoundError(FavroAPIError):
    """Resource not found error."""

    pass


class FavroRateLimitError(FavroAPIError):
    """Rate limit exceeded error."""

    def __init__(self, message: str, reset_time: str | None = None) -> None:
        super().__init__(429, message)
        self.reset_time = reset_time


class FavroClient:
    """Client for the Favro API."""

    def __init__(
        self,
        email: str,
        token: str,
        organization_id: str | None = None,
    ) -> None:
        self.email = email
        self.token = token
        self.organization_id = organization_id
        self._backend_identifier: str | None = None
        self._client = httpx.Client(
            base_url=BASE_URL,
            auth=(email, token),
            timeout=30.0,
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "FavroClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        self.close()

    def _get_headers(self, include_org: bool = True) -> dict[str, str]:
        """Get request headers."""
        headers: dict[str, str] = {}
        if include_org and self.organization_id:
            headers["organizationId"] = self.organization_id
        if self._backend_identifier:
            headers["X-Favro-Backend-Identifier"] = self._backend_identifier
        return headers

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and extract data."""
        # Store backend identifier for routing
        backend_id = response.headers.get("X-Favro-Backend-Identifier")
        if backend_id:
            self._backend_identifier = backend_id

        if response.status_code == 401:
            raise FavroAuthError(401, "Invalid credentials")
        if response.status_code == 403:
            raise FavroAuthError(403, "Access denied")
        if response.status_code == 404:
            raise FavroNotFoundError(404, "Resource not found")
        if response.status_code == 429:
            reset_time = response.headers.get("X-RateLimit-Reset")
            raise FavroRateLimitError("Rate limit exceeded", reset_time)
        if response.status_code >= 400:
            raise FavroAPIError(response.status_code, response.text)

        if response.status_code == 204:
            return {}

        data: dict[str, Any] = response.json()
        # Check for error responses that come with 200 status
        if "message" in data and len(data) == 1:
            raise FavroAPIError(200, str(data["message"]))
        return data

    def _get(
        self,
        path: str,
        params: dict[str, str] | None = None,
        include_org: bool = True,
    ) -> dict[str, Any]:
        """Make a GET request."""
        response = self._client.get(
            path,
            params=params,
            headers=self._get_headers(include_org),
        )
        return self._handle_response(response)

    def _post(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        include_org: bool = True,
    ) -> dict[str, Any]:
        """Make a POST request."""
        response = self._client.post(
            path,
            json=data,
            headers=self._get_headers(include_org),
        )
        return self._handle_response(response)

    def _put(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        include_org: bool = True,
    ) -> dict[str, Any]:
        """Make a PUT request."""
        response = self._client.put(
            path,
            json=data,
            headers=self._get_headers(include_org),
        )
        return self._handle_response(response)

    def _delete(
        self,
        path: str,
        params: dict[str, str] | None = None,
        include_org: bool = True,
    ) -> dict[str, Any]:
        """Make a DELETE request."""
        response = self._client.delete(
            path,
            params=params,
            headers=self._get_headers(include_org),
        )
        return self._handle_response(response)

    def _paginate_all(
        self,
        path: str,
        params: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch all pages of a paginated endpoint."""
        all_entities: list[dict[str, Any]] = []
        params = params or {}

        # First request
        data = self._get(path, params)
        all_entities.extend(data.get("entities", []))

        # Get subsequent pages
        request_id: str | None = data.get("requestId")
        total_pages = data.get("pages", 1)
        if not isinstance(total_pages, int):
            total_pages = 1

        if request_id:
            for page in range(1, total_pages):
                page_params = {**params, "requestId": request_id, "page": str(page)}
                data = self._get(path, page_params)
                all_entities.extend(data.get("entities", []))

        return all_entities

    # User endpoints
    def get_user(self, user_id: str) -> User:
        """Get a specific user."""
        data = self._get(f"/users/{user_id}", include_org=False)
        return User.model_validate(data)

    def get_users(self) -> list[User]:
        """Get all users in the organization."""
        entities = self._paginate_all("/users")
        return [User.model_validate(e) for e in entities]

    # Organization endpoints
    def get_organizations(self) -> list[Organization]:
        """Get all organizations accessible to the user."""
        entities = self._paginate_all("/organizations", params={})
        # Note: This endpoint doesn't require org header, but we need to
        # temporarily disable it
        return [Organization.model_validate(e) for e in entities]

    def get_organization(self, organization_id: str) -> Organization:
        """Get a specific organization."""
        data = self._get(f"/organizations/{organization_id}")
        return Organization.model_validate(data)

    # Collection endpoints
    def get_collections(self, archived: bool = False) -> list[Collection]:
        """Get all collections in the organization."""
        params = {"archived": "true" if archived else "false"}
        entities = self._paginate_all("/collections", params)
        return [Collection.model_validate(e) for e in entities]

    def get_collection(self, collection_id: str) -> Collection:
        """Get a specific collection."""
        data = self._get(f"/collections/{collection_id}")
        return Collection.model_validate(data)

    # Widget (board) endpoints
    def get_widgets(
        self,
        collection_id: str | None = None,
        archived: bool = False,
    ) -> list[Widget]:
        """Get all widgets (boards) in the organization."""
        params: dict[str, str] = {"archived": "true" if archived else "false"}
        if collection_id:
            params["collectionId"] = collection_id
        entities = self._paginate_all("/widgets", params)
        return [Widget.model_validate(e) for e in entities]

    def get_widget(self, widget_common_id: str) -> Widget:
        """Get a specific widget (board)."""
        data = self._get(f"/widgets/{widget_common_id}")
        return Widget.model_validate(data)

    # Column endpoints
    def get_columns(self, widget_common_id: str) -> list[Column]:
        """Get all columns for a widget."""
        params = {"widgetCommonId": widget_common_id}
        entities = self._paginate_all("/columns", params)
        return [Column.model_validate(e) for e in entities]

    def get_column(self, column_id: str) -> Column:
        """Get a specific column."""
        data = self._get(f"/columns/{column_id}")
        return Column.model_validate(data)

    def create_column(
        self,
        widget_common_id: str,
        name: str,
        position: int | None = None,
    ) -> Column:
        """Create a new column on a widget."""
        data: dict[str, Any] = {
            "widgetCommonId": widget_common_id,
            "name": name,
        }
        if position is not None:
            data["position"] = position
        result = self._post("/columns", data)
        return Column.model_validate(result)

    def update_column(
        self,
        column_id: str,
        name: str | None = None,
        position: int | None = None,
    ) -> Column:
        """Update a column."""
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if position is not None:
            data["position"] = position
        result = self._put(f"/columns/{column_id}", data)
        return Column.model_validate(result)

    def delete_column(self, column_id: str) -> None:
        """Delete a column."""
        self._delete(f"/columns/{column_id}")

    # Card endpoints
    def get_cards(
        self,
        widget_common_id: str | None = None,
        collection_id: str | None = None,
        column_id: str | None = None,
        todo_list: bool = False,
        unique: bool = True,
    ) -> list[Card]:
        """Get cards from the organization."""
        params: dict[str, str] = {"unique": "true" if unique else "false"}
        if widget_common_id:
            params["widgetCommonId"] = widget_common_id
        if collection_id:
            params["collectionId"] = collection_id
        if column_id:
            params["columnId"] = column_id
        if todo_list:
            params["todoList"] = "true"
        entities = self._paginate_all("/cards", params)
        return [Card.model_validate(e) for e in entities]

    def get_card(self, card_id: str) -> Card:
        """Get a specific card."""
        data = self._get(f"/cards/{card_id}")
        return Card.model_validate(data)

    def create_card(
        self,
        name: str,
        widget_common_id: str | None = None,
        column_id: str | None = None,
        lane_id: str | None = None,
        detailed_description: str | None = None,
        tags: list[str] | None = None,
        start_date: str | None = None,
        due_date: str | None = None,
        assignments: list[str] | None = None,
    ) -> Card:
        """Create a new card."""
        data: dict[str, Any] = {"name": name}
        if widget_common_id:
            data["widgetCommonId"] = widget_common_id
        if column_id:
            data["columnId"] = column_id
        if lane_id:
            data["laneId"] = lane_id
        if detailed_description:
            data["detailedDescription"] = detailed_description
        if tags:
            data["addTags"] = tags
        if start_date:
            data["startDate"] = start_date
        if due_date:
            data["dueDate"] = due_date
        if assignments:
            data["addAssignmentIds"] = assignments
        result = self._post("/cards", data)
        return Card.model_validate(result)

    def update_card(
        self,
        card_id: str,
        name: str | None = None,
        detailed_description: str | None = None,
        widget_common_id: str | None = None,
        column_id: str | None = None,
        lane_id: str | None = None,
        add_tags: list[str] | None = None,
        remove_tags: list[str] | None = None,
        start_date: str | None = None,
        due_date: str | None = None,
        add_assignments: list[str] | None = None,
        remove_assignments: list[str] | None = None,
        archived: bool | None = None,
        list_position: float | None = None,
        custom_fields: list[dict[str, Any]] | None = None,
    ) -> Card:
        """Update a card.

        Args:
            custom_fields: List of custom field updates. Each dict should contain
                'customFieldId' and the appropriate value field for the field type:
                - Text: {'customFieldId': '...', 'value': 'text'}
                - Number/Rating: {'customFieldId': '...', 'total': 5}
                - Link: {'customFieldId': '...', 'link': {'url': '...', 'text': '...'}}
                - Checkbox: {'customFieldId': '...', 'value': True}
                - Date: {'customFieldId': '...', 'value': '2024-01-15'}
                - Status: {'customFieldId': '...', 'value': ['itemId1', 'itemId2']}
                - Members: {'customFieldId': '...', 'members': {'addUserIds': [...], 'removeUserIds': [...]}}
                - Color: {'customFieldId': '...', 'color': 'blue'}
        """
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if detailed_description is not None:
            data["detailedDescription"] = detailed_description
        if widget_common_id is not None:
            data["widgetCommonId"] = widget_common_id
        if column_id is not None:
            data["columnId"] = column_id
        if lane_id is not None:
            data["laneId"] = lane_id
        if add_tags:
            data["addTagIds"] = add_tags
        if remove_tags:
            data["removeTagIds"] = remove_tags
        if start_date is not None:
            data["startDate"] = start_date
        if due_date is not None:
            data["dueDate"] = due_date
        if add_assignments:
            data["addAssignmentIds"] = add_assignments
        if remove_assignments:
            data["removeAssignmentIds"] = remove_assignments
        if archived is not None:
            data["archive"] = archived
        if list_position is not None:
            data["listPosition"] = list_position
        if custom_fields:
            data["customFields"] = custom_fields
        result = self._put(f"/cards/{card_id}", data)
        return Card.model_validate(result)

    def delete_card(self, card_id: str, everywhere: bool = False) -> None:
        """Delete a card."""
        params = {"everywhere": "true"} if everywhere else None
        self._delete(f"/cards/{card_id}", params)

    # Tag endpoints
    def get_tags(self) -> list[Tag]:
        """Get all tags in the organization."""
        entities = self._paginate_all("/tags")
        return [Tag.model_validate(e) for e in entities]

    def get_tag(self, tag_id: str) -> Tag:
        """Get a specific tag."""
        data = self._get(f"/tags/{tag_id}")
        return Tag.model_validate(data)

    # Custom field endpoints
    def get_custom_fields(self) -> list[dict[str, Any]]:
        """Get all custom fields in the organization."""
        return self._paginate_all("/customfields")
