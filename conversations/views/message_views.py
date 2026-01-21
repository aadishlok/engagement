# views/message_views.py
from rest_framework.decorators import api_view, authentication_classes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from ..services import message_service
from ..authentication import APIKeyAuthentication
from ..serializers import MessageCreateSerializer


@extend_schema(
    methods=["GET"],
    summary="List messages in a conversation",
    description="Retrieve all messages in a conversation with optional filtering by text content and role. Results are paginated. This endpoint does not require authentication.",
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="Unique identifier of the conversation",
            required=True,
        ),
        OpenApiParameter(
            name="q",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Optional search query to filter messages by text content (case-insensitive)",
            required=False,
        ),
        OpenApiParameter(
            name="role",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Optional filter by role: 'user' or 'assistant'",
            required=False,
            enum=["user", "assistant"],
        ),
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for pagination (default: 1)",
            required=False,
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of items per page (default: 10)",
            required=False,
        ),
    ],
    responses={
        200: {
            "description": "Messages retrieved successfully",
        },
        404: {"description": "Conversation not found"},
    },
    examples=[
        OpenApiExample(
            "Success Response",
            value={
                "success": True,
                "data": {
                    "count": 25,
                    "next": "http://localhost:8000/conversations/{id}/messages?page=2",
                    "previous": None,
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
                },
                "message": "Messages retrieved successfully"
            },
            response_only=True,
        ),
    ],
    tags=["Messages"],
    auth=[],
)
@api_view(['GET'])
def get_messages_view(request, id):
    return message_service.get_messages_by_conversation_id(id, request)


@extend_schema(
    methods=["POST"],
    summary="Create a message",
    description="Add a new message to a conversation. If the message role is 'user', an assistant response will be automatically generated. Requires authentication.",
    request=MessageCreateSerializer,
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="Unique identifier of the conversation",
            required=True,
        ),
    ],
    responses={
        201: {
            "description": "Message created successfully",
        },
        400: {"description": "Validation error"},
        401: {"description": "Authentication failed"},
        404: {"description": "Conversation not found"},
    },
    examples=[
        OpenApiExample(
            "Create User Message",
            value={
                "text": "Hello, how are you?",
                "role": "user"
            },
            request_only=True,
        ),
        OpenApiExample(
            "Create Assistant Message",
            value={
                "text": "I'm doing well, thank you!",
                "role": "assistant"
            },
            request_only=True,
        ),
        OpenApiExample(
            "Success Response",
            value={
                "success": True,
                "data": {
                    "message_id": "660e8400-e29b-41d4-a716-446655440001",
                    "conversation": "550e8400-e29b-41d4-a716-446655440000",
                    "role": "user",
                    "text": "Hello!",
                    "date_created": "2024-01-19T12:00:00Z",
                    "date_updated": "2024-01-19T12:00:00Z"
                },
                "message": "Message created successfully"
            },
            response_only=True,
        ),
    ],
    tags=["Messages"],
)
@api_view(['POST'])
@authentication_classes([APIKeyAuthentication])
def create_message_view(request, id):
    return message_service.create_message(id, request)


@extend_schema(
    methods=["DELETE"],
    summary="Delete a message",
    description="Delete a specific message from a conversation. This action cannot be undone.",
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="Unique identifier of the conversation",
            required=True,
        ),
        OpenApiParameter(
            name="message_id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="Unique identifier of the message",
            required=True,
        ),
    ],
    responses={
        200: {
            "description": "Message deleted successfully",
        },
        404: {"description": "Message not found"},
        401: {"description": "Authentication failed"},
    },
    examples=[
        OpenApiExample(
            "Success Response",
            value={
                "success": True,
                "data": None,
                "message": "Message deleted successfully"
            },
            response_only=True,
        ),
    ],
    tags=["Messages"],
)
@api_view(['DELETE'])
@authentication_classes([APIKeyAuthentication])
def delete_message_view(request, id, message_id):
    return message_service.delete_message(id, message_id)
