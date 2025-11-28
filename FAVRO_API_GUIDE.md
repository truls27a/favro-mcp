# Favro API Guide

A comprehensive guide to using the Favro REST API for building integrations and automations with the Favro project management platform.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [API Basics](#api-basics)
- [Core Concepts](#core-concepts)
- [Endpoints](#endpoints)
- [Examples](#examples)
- [SDKs and Libraries](#sdks-and-libraries)
- [Limitations and Best Practices](#limitations-and-best-practices)

---

## Overview

The Favro API is a RESTful API that allows you to programmatically interact with Favro's project management features. You can manage organizations, collections, widgets (boards), cards, custom fields, tags, comments, and more.

**Base URL:** `https://favro.com/api/v1/`

**Official Documentation:** [https://favro.com/developer/](https://favro.com/developer/)

---

## Authentication

### Methods

Favro supports **HTTP Basic Authentication** using:
- Your email address as the username
- Either your password or an API token as the password

### Generating an API Token

1. Log into Favro
2. Click your account dropdown in the upper-left corner
3. Select **My profile**
4. Navigate to the **API Tokens** tab
5. Create a new token

**Benefits of API tokens:**
- Can be restricted to read-only endpoints
- Can be revoked at any time
- More secure than using your password

### Authentication Header

```
Authorization: Basic [base64(email:password_or_token)]
```

### Example Request

```bash
curl -u "user@example.com:your_api_token" \
  https://favro.com/api/v1/organizations
```

---

## API Basics

### Required Headers

| Header | Description | Required |
|--------|-------------|----------|
| `Authorization` | Basic auth credentials | Yes |
| `organizationId` | The organization ID for the request | Yes (for org routes) |
| `Content-Type` | `application/json` for POST/PUT | Yes (for write operations) |
| `X-Favro-Backend-Identifier` | Backend routing identifier | Recommended |

### Organization ID

Nearly all API requests require the `organizationId` header. The API will reject calls to organization routes that don't include this header.

You can obtain your organization ID by calling `GET /organizations` first.

### Backend Routing

Every response includes an `X-Favro-Backend-Identifier` header. Include this header in subsequent requests to ensure routing to the same server instance, which is important for data consistency.

### Rate Limiting

Rate limits are applied at two levels:

| Route Type | Rate Limit |
|------------|------------|
| User-level routes | 50 calls/hour |
| Organization routes (Trial) | 100 calls/hour |
| Organization routes (Standard) | 1,000 calls/hour |
| Organization routes (Enterprise) | 10,000 calls/hour |

**Rate limit headers in responses:**
- `X-RateLimit-Limit` - Maximum requests allowed
- `X-RateLimit-Remaining` - Requests remaining
- `X-RateLimit-Reset` - Unix timestamp when limit resets
- `X-RateLimit-Delay` - Suggested delay between requests

### Pagination

Paginated endpoints return up to 100 items per page with this structure:

```json
{
  "limit": 100,
  "page": 0,
  "pages": 5,
  "requestId": "abc123",
  "entities": [...]
}
```

To fetch subsequent pages, include the `requestId` and `page` parameters:

```bash
GET /api/v1/cards?requestId=abc123&page=1
```

### Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request |
| 401 | Authentication failed |
| 403 | Authorization failed |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Server error |

---

## Core Concepts

### Terminology Mapping

| Favro UI Term | API Term |
|---------------|----------|
| Board/Backlog | Widget |
| Dashboard | Collection |
| Card | Card |
| Column/Status | Column |

### Data Hierarchy

```
Organization
└── Collection (Dashboard)
    └── Widget (Board/Backlog)
        └── Column
            └── Card
                ├── Tasks/Tasklists
                ├── Comments
                ├── Attachments
                └── Custom Fields
```

### Identifiers

Favro uses several types of IDs:
- **`organizationId`** - Organization-scoped identifier
- **`widgetCommonId`** - Global widget identifier
- **`cardCommonId`** - Global card identifier
- **`cardId`** - Widget-scoped card identifier
- **`columnId`** - Column identifier within a widget

---

## Endpoints

### Organizations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/organizations` | Get all organizations |
| GET | `/organizations/:organizationId` | Get specific organization |
| POST | `/organizations` | Create organization |
| PUT | `/organizations/:organizationId` | Update organization |

### Collections

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/collections` | Get all collections |
| GET | `/collections/:collectionId` | Get specific collection |
| POST | `/collections` | Create collection |
| PUT | `/collections/:collectionId` | Update collection |
| DELETE | `/collections/:collectionId` | Delete collection |

### Widgets (Boards)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/widgets` | Get all widgets |
| GET | `/widgets/:widgetCommonId` | Get specific widget |
| POST | `/widgets` | Create widget |
| PUT | `/widgets/:widgetCommonId` | Update widget |
| DELETE | `/widgets/:widgetCommonId` | Delete widget |

**Note:** Deleting a widget also deletes all columns, cards, and comments within it.

### Columns

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/columns` | Get all columns (requires `widgetCommonId`) |
| GET | `/columns/:columnId` | Get specific column |
| POST | `/columns` | Create column |
| PUT | `/columns/:columnId` | Update column |
| DELETE | `/columns/:columnId` | Delete column |

**Column object properties:**
- `columnId`
- `organizationId`
- `widgetCommonId`
- `name`
- `position`
- `cardCount`
- `timeSum`
- `estimationSum`

### Cards

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cards` | Get cards (requires filter) |
| GET | `/cards/:cardId` | Get specific card |
| POST | `/cards` | Create card |
| PUT | `/cards/:cardId` | Update card |
| DELETE | `/cards/:cardId` | Delete card |

**Required filters for GET /cards:**
- `cardCommonId`
- `cardSequentialId`
- `widgetCommonId`
- `collectionId`
- `todoList=true`

**Card properties include:**
- `cardId`, `cardCommonId`
- `name`, `detailedDescription`
- `widgetCommonId`, `columnId`
- `assignments` (user assignments)
- `tags` (tag IDs)
- `customFields`
- `dependencies`
- `attachments`
- `archived`

### Custom Fields

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customfields` | Get all custom fields |
| GET | `/customfields/:customFieldId` | Get specific custom field |
| POST | `/customfields` | Create custom field |
| PUT | `/customfields/:customFieldId` | Update custom field |
| DELETE | `/customfields/:customFieldId` | Delete custom field |

**Custom field types:**
- Text, Number, Rating
- Members, Date, Timeline
- Status, Multiple select
- Checkbox, Link
- Time (time tracking)

### Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tags` | Get all tags |
| GET | `/tags/:tagId` | Get specific tag |
| POST | `/tags` | Create tag |
| PUT | `/tags/:tagId` | Update tag |
| DELETE | `/tags/:tagId` | Delete tag |

**Tag properties:**
- `tagId`
- `organizationId`
- `name`
- `color`

### Tasks/Tasklists

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | Get tasks for a card |
| POST | `/tasks` | Create task |
| PUT | `/tasks/:taskId` | Update task |
| DELETE | `/tasks/:taskId` | Delete task |

### Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/comments` | Get comments for a card |
| POST | `/comments` | Create comment |
| PUT | `/comments/:commentId` | Update comment |
| DELETE | `/comments/:commentId` | Delete comment |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | Get all users in organization |
| GET | `/users/:userId` | Get specific user |

### Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/webhooks` | Get all webhooks |
| POST | `/webhooks` | Create webhook |
| DELETE | `/webhooks/:webhookId` | Delete webhook |

**Webhook events:**
- Card created, updated, deleted
- Card moved (column change)
- Card committed
- Comment added

---

## Examples

### Get All Organizations

```bash
curl -u "user@example.com:api_token" \
  https://favro.com/api/v1/organizations
```

### Get Cards from a Widget

```bash
curl -u "user@example.com:api_token" \
  -H "organizationId: your_org_id" \
  "https://favro.com/api/v1/cards?widgetCommonId=ff440e8f358c08513a86c8d6"
```

### Create a Card

```bash
curl -X POST "https://favro.com/api/v1/cards" \
  -u "user@example.com:api_token" \
  -H "organizationId: zk4CJpg5uozhL4R2W" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Task",
    "widgetCommonId": "ff440e8f358c08513a86c8d6",
    "columnId": "b4d8c6283d9d58f9a39108e7",
    "detailedDescription": "Task description here"
  }'
```

### Create a Card with Custom Fields

```bash
curl -X POST "https://favro.com/api/v1/cards" \
  -u "user@example.com:api_token" \
  -H "organizationId: zk4CJpg5uozhL4R2W" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Task with Custom Fields",
    "widgetCommonId": "ff440e8f358c08513a86c8d6",
    "columnId": "b4d8c6283d9d58f9a39108e7",
    "customFields": [{
      "customFieldId": "kj4qQzhLMJ73dybBR",
      "value": "Custom value"
    }]
  }'
```

### Update a Card

```bash
curl -X PUT "https://favro.com/api/v1/cards/card_id_here" \
  -u "user@example.com:api_token" \
  -H "organizationId: zk4CJpg5uozhL4R2W" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Task Name",
    "columnId": "new_column_id"
  }'
```

### Get Columns for a Widget

```bash
curl -u "user@example.com:api_token" \
  -H "organizationId: your_org_id" \
  "https://favro.com/api/v1/columns?widgetCommonId=ff440e8f358c08513a86c8d6"
```

### Create a Webhook

```bash
curl -X POST "https://favro.com/api/v1/webhooks" \
  -u "user@example.com:api_token" \
  -H "organizationId: zk4CJpg5uozhL4R2W" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Webhook",
    "widgetCommonId": "ff440e8f358c08513a86c8d6",
    "postToUrl": "https://your-server.com/webhook"
  }'
```

---

## SDKs and Libraries

### Node.js / TypeScript

**Bravo SDK** - Unofficial SDK with full TypeScript support

```bash
npm install @bscotch/bravo
```

```typescript
import { BravoClient } from '@bscotch/bravo';

const client = new BravoClient({
  token: 'your_api_token',
  email: 'user@example.com',
  organizationId: 'your_org_id'
});

// Get all cards from a widget
const cards = await client.findCardsByWidgetId('widget_id');
```

**Repository:** [github.com/bscotch/favro-sdk](https://github.com/bscotch/favro-sdk)

### PHP

```bash
composer require seregazhuk/favro-api
```

```php
use Favro\Favro;

$favro = new Favro('user@example.com', 'api_token', 'organization_id');

// Get cards
$cards = $favro->cards->getAll(['widgetCommonId' => 'widget_id']);

// Create a card
$card = $favro->cards->create([
    'name' => 'New Card',
    'widgetCommonId' => 'widget_id'
]);
```

**Repository:** [github.com/seregazhuk/php-favro-api](https://github.com/seregazhuk/php-favro-api)

### Elixir

**Favro Hex Package**

```elixir
# In mix.exs
{:favro, "~> 0.2.1"}
```

```elixir
Favro.list_cards(widget: "widget_id")
Favro.create_card(%{name: "New Card", widgetCommonId: "widget_id"})
```

**Documentation:** [hexdocs.pm/favro](https://hexdocs.pm/favro)

### Python

**Unofficial Python wrapper**

**Repository:** [github.com/ALERTua/favro](https://github.com/ALERTua/favro)

---

## Limitations and Best Practices

### Known Limitations

1. **Limited Search/Filtering**
   - No text search on card names or descriptions
   - Cannot filter by assigned user or tags directly
   - Must fetch all cards and filter locally

2. **Rate Limits**
   - API rate limits are relatively low
   - Consider caching to reduce API calls
   - Use the `X-RateLimit-Remaining` header to monitor usage

3. **Webhook Constraints**
   - Webhooks created via API differ from UI-created webhooks
   - Webhook payloads may have incomplete information
   - Custom fields scope information not available in webhooks

4. **Custom Fields**
   - All custom fields appear global in API responses
   - No mechanism to determine collection/widget scope

5. **Identifier Complexity**
   - Cards have both global (`cardCommonId`) and widget-scoped (`cardId`) identifiers
   - Most endpoints use widget-scoped `cardId`

### Best Practices

1. **Always include the backend identifier**
   ```bash
   -H "X-Favro-Backend-Identifier: value_from_previous_response"
   ```

2. **Handle pagination properly**
   - Always check if there are more pages
   - Use the same `requestId` for subsequent page requests

3. **Cache organization data**
   - Fetch organization, collection, and widget data once
   - Reuse IDs rather than fetching repeatedly

4. **Implement retry logic**
   - Handle 429 (rate limit) responses with exponential backoff
   - Use the `X-RateLimit-Reset` header to determine wait time

5. **Use appropriate HTTP methods**
   - GET for reading
   - POST for creating
   - PUT for updating
   - DELETE for removing

6. **Validate before writing**
   - Fetch current state before updates when needed
   - Check required fields are present

---

## Additional Resources

- [Official API Reference](https://favro.com/developer/)
- [Favro Help Center - API](https://help.favro.com/en/collections/2170744-api)
- [Bravo SDK Documentation](https://github.com/bscotch/favro-sdk)
- [Microsoft Learn - Generating API Token](https://learn.microsoft.com/en-us/viva/goals/favro-generating-an-api-token)

---

*This guide was compiled from the official Favro API documentation and community resources.*
