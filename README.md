# AI Chat Assistant Backend API

A Django REST Framework backend API for managing conversations and messages for an AI chat assistant. This project demonstrates skills in API design, data modeling, authentication, and deployment readiness.

## Features

- RESTful API for managing conversations and messages
- API key-based authentication (required for POST/DELETE operations)
- Automatic assistant response generation with async background processing
- Pagination and filtering support for message listings
- SQLite database with proper migrations and schema evolution
- Docker containerization support
- Comprehensive test suite
- Logging and observability

## Tech Stack

- **Framework**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: SQLite (can be easily switched to PostgreSQL)
- **Containerization**: Docker & Docker Compose

## Quick Start with Docker (Recommended)

### Prerequisites
- Docker
- Docker Compose

### Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd engagement
```

2. Start the service:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

3. Run migrations (if needed):
```bash
docker-compose exec web python manage.py migrate
```

## Local Development Setup

### Prerequisites
- Python 3.11+
- pip

### Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd engagement
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## Running Tests

To run the test suite:

```bash
# With Docker
docker-compose exec web python manage.py test

# Local development
python manage.py test
```

## API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication

**GET endpoints are public** and do not require authentication. **POST and DELETE endpoints require API key authentication.**

Include the API key in the request header for authenticated endpoints:

```
X-API-Key: neuRealities_assessment
```

**Note**: The default API key is `neuRealities_assessment`. In production, this should be changed and stored securely.

**Authentication Requirements:**
- `GET /conversations/{id}` - No authentication required
- `GET /conversations/{id}/messages` - No authentication required
- `POST /conversations/` - Authentication required
- `POST /conversations/{id}/messages/create` - Authentication required
- `DELETE /conversations/{id}/delete` - Authentication required
- `DELETE /conversations/{id}/messages/{message_id}` - Authentication required

### Endpoints

#### 1. Create a Conversation

**POST** `/conversations/`

Create a new conversation.

**Request Body:**
```json
{
  "title": "My First Conversation",  // Optional
  "description": "A conversation about AI assistants"  // Required
}
```

**Response:** `201 Created`
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My First Conversation",
  "description": "A conversation about AI assistants",
  "date_created": "2024-01-19T12:00:00Z",
  "date_updated": "2024-01-19T12:00:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/conversations/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: neuRealities_assessment" \
  -d '{"description": "Test conversation", "title": "Test"}'
```

---

#### 2. Get a Conversation

**GET** `/conversations/{id}`

Retrieve a conversation by its ID. **This endpoint does not require authentication.**

**Query Parameters:**
- `q` (optional): Search query to filter by title or description (case-insensitive)

**Response:** `200 OK`
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My First Conversation",
  "description": "A conversation about AI assistants",
  "date_created": "2024-01-19T12:00:00Z",
  "date_updated": "2024-01-19T12:00:00Z"
}
```

**Example:**
```bash
# No authentication required for GET
curl -X GET http://localhost:8000/conversations/550e8400-e29b-41d4-a716-446655440000

# With search filter
curl -X GET "http://localhost:8000/conversations/550e8400-e29b-41d4-a716-446655440000?q=AI"
```

---

#### 3. Delete a Conversation

**DELETE** `/conversations/{id}/delete`

Delete a conversation and all its associated messages. **Requires authentication.**

**Response:** `200 OK`

**Example:**
```bash
curl -X DELETE http://localhost:8000/conversations/550e8400-e29b-41d4-a716-446655440000/delete \
  -H "X-API-Key: neuRealities_assessment"
```

---

#### 4. Create a Message

**POST** `/conversations/{id}/messages/create`

Add a message to a conversation. **Requires authentication.** If the message role is "user", an assistant response will be automatically generated in the background using async processing.

**Request Body:**
```json
{
  "text": "Hello, how are you?",  // Required
  "role": "user"  // Required: "user" or "assistant"
}
```

**Response:** `201 Created`
```json
{
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "conversation": "550e8400-e29b-41d4-a716-446655440000",
  "role": "user",
  "text": "Hello, how are you?",
  "date_created": "2024-01-19T12:00:00Z",
  "date_updated": "2024-01-19T12:00:00Z"
}
```

**Note**: When creating a user message, an assistant response is automatically generated in a background thread. The API returns immediately with the user message, and the assistant response is created asynchronously.

**Example:**
```bash
curl -X POST http://localhost:8000/conversations/550e8400-e29b-41d4-a716-446655440000/messages/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: neuRealities_assessment" \
  -d '{"text": "Hello!", "role": "user"}'
```

---

#### 5. List Messages in a Conversation

**GET** `/conversations/{id}/messages`

Retrieve all messages in a conversation with pagination and filtering. **This endpoint does not require authentication.**

**Query Parameters:**
- `q` (optional): Search query to filter messages by text content (case-insensitive)
- `role` (optional): Filter by role - "user" or "assistant"
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 10)

**Response:** `200 OK`
```json
{
  "count": 25,
  "next": "http://localhost:8000/conversations/{id}/messages?page=2",
  "previous": null,
  "results": [
    {
      "message_id": "660e8400-e29b-41d4-a716-446655440001",
      "conversation": "550e8400-e29b-41d4-a716-446655440000",
      "role": "user",
      "text": "Hello!",
      "date_created": "2024-01-19T12:00:00Z",
      "date_updated": "2024-01-19T12:00:00Z"
    },
    {
      "message_id": "660e8400-e29b-41d4-a716-446655440002",
      "conversation": "550e8400-e29b-41d4-a716-446655440000",
      "role": "assistant",
      "text": "Hello! How can I assist you today?",
      "date_created": "2024-01-19T12:00:01Z",
      "date_updated": "2024-01-19T12:00:01Z"
    }
  ]
}
```

**Example:**
```bash
# No authentication required for GET
curl -X GET http://localhost:8000/conversations/550e8400-e29b-41d4-a716-446655440000/messages

# With filters
curl -X GET "http://localhost:8000/conversations/550e8400-e29b-41d4-a716-446655440000/messages?q=Hello&role=user"
```

---

#### 6. Delete a Message

**DELETE** `/conversations/{id}/messages/{message_id}`

Delete a specific message from a conversation.

**Response:** `204 No Content`

**Example:**
```bash
curl -X DELETE http://localhost:8000/conversations/550e8400-e29b-41d4-a716-446655440000/messages/660e8400-e29b-41d4-a716-446655440001 \
  -H "X-API-Key: neuRealities_assessment"
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "status": "error",
  "code": 400,
  "message": "Validation or Client Error",
  "details": {
    "field_name": ["Error message"]
  }
}
```

### Common Status Codes

- `200 OK`: Successful GET request
- `201 Created`: Successful POST request
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Invalid or missing API key
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Data Models

### Conversation
- `conversation_id` (UUID, Primary Key): Unique identifier
- `title` (String, Optional): Conversation title
- `description` (String, Required, Max 500 chars): Conversation description
- `date_created` (DateTime): Creation timestamp
- `date_updated` (DateTime): Last update timestamp

### Message
- `message_id` (UUID, Primary Key): Unique identifier
- `conversation` (ForeignKey): Reference to Conversation
- `role` (String, Required): "user" or "assistant"
- `text` (Text, Required): Message content
- `date_created` (DateTime): Creation timestamp
- `date_updated` (DateTime): Last update timestamp

## Assistant Response Generation

The API includes a simple rule-based assistant response generator with **async background processing**. When a user message is created:

1. The user message is saved immediately
2. The API returns the user message response right away
3. Assistant response generation runs in a background thread (non-blocking)
4. The assistant response is saved asynchronously

**Response Patterns:**
- Greetings ("hello", "hi", "hey") → "Hello! How can I assist you today?"
- Help requests → "I'm here to help! What do you need assistance with?"
- Questions (contains "?") → "That's an interesting question. Let me think about that..."
- Thanks → "You're welcome! Is there anything else I can help with?"
- Default → "I understand. Can you tell me more about that?"

This async approach ensures fast API response times while assistant responses are generated in the background.

## Database Migrations

The project uses Django migrations for database schema management:

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

The project includes:
- Initial migration: Creates Conversation and Message tables
- Second migration: Adds `role` field to Message and `title` field to Conversation, demonstrating schema evolution

## Project Structure

```
engagement/
├── conversations/          # Main app
│   ├── migrations/         # Database migrations
│   ├── services/           # Business logic layer
│   ├── views/              # API views
│   ├── models.py           # Data models
│   ├── serializers.py      # Request/response serializers
│   ├── authentication.py  # API key authentication
│   ├── tests.py            # Test suite
│   └── urls.py             # URL routing
├── engagement/             # Django project settings
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # This file
```

## Logging and Observability

The API includes comprehensive logging for:
- API requests and responses (method, path, status code, duration)
- Assistant response generation
- Errors and exceptions with full context
- Conversation and message operations

Logs are output to:
- Console (for development)
- File: `logs/engagement.log` (for production)

Log levels:
- **INFO**: Normal operations (requests, responses, successful operations)
- **WARNING**: Potential issues
- **ERROR**: Errors and exceptions

## Design Decisions & Trade-offs

1. **Authentication**: GET endpoints are public for better API usability, while POST/DELETE operations require authentication for security.

2. **Database**: SQLite is used for simplicity and ease of deployment. For production, PostgreSQL is recommended.

3. **Assistant Responses**: Simple rule-based responses are used instead of real AI integration, as per requirements. Responses are generated asynchronously in background threads to ensure fast API response times.

4. **Pagination**: Page-based pagination is implemented for message listings to handle large conversations efficiently.

5. **Cascade Deletion**: Deleting a conversation automatically deletes all associated messages (CASCADE).

6. **UUID Primary Keys**: UUIDs are used instead of auto-incrementing integers for better distributed system compatibility.

7. **Async Processing**: Background threading is used for assistant response generation to avoid blocking API responses. For production scale, consider using Celery with Redis/RabbitMQ.

8. **Logging**: Comprehensive logging is implemented for observability. In production, consider integrating with log aggregation services (e.g., ELK stack, CloudWatch).

## Future Enhancements

- More sophisticated assistant response generation (e.g., LLM integration)
- Rate limiting
- PostgreSQL support in docker-compose
- API versioning
- Metrics and monitoring (e.g., Prometheus)
- Celery integration for more robust async task handling

## License

This project is created for assessment purposes.
