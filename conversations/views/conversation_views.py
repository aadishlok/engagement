from rest_framework.decorators import api_view, authentication_classes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from ..services.conversation_service import get_conversation_by_id, create_conversation, delete_conversation
from rest_framework.exceptions import AuthenticationFailed
from ..authentication import APIKeyAuthentication
from ..serializers import ConversationCreateSerializer
from ..utils import validate_uuid


@extend_schema(
    methods=["GET"],
    summary="Get a conversation",
    description="Retrieve a conversation by its unique identifier. Optionally filter by text search in title or description. This endpoint does not require authentication.",
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
        200: {"description": "Conversation retrieved successfully"},
        404: {"description": "Conversation not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
    examples=[
        OpenApiExample(
            "Success Response",
            value={
                "success": True,
                "data": {
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "My First Conversation",
                    "description": "A conversation about AI assistants",
                    "date_created": "2024-01-19T12:00:00Z",
                    "date_updated": "2024-01-19T12:00:00Z"
                },
                "message": "Conversation retrieved successfully"
            },
            response_only=True,
        ),
    ],
    tags=["Conversations"],
    auth=[],
)
@extend_schema(
    methods=["DELETE"],
    summary="Delete a conversation",
    description="Delete a conversation and all its associated messages. This action cannot be undone. Requires authentication.",
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
        200: {"description": "Conversation deleted successfully"},
        404: {"description": "Conversation not found"},
        401: {"description": "Authentication failed"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
    examples=[
        OpenApiExample(
            "Success Response",
            value={
                "success": True,
                "data": None,
                "message": "Conversation deleted successfully"
            },
            response_only=True,
        ),
    ],
    tags=["Conversations"],
)
@api_view(["GET", "DELETE"])
def get_or_delete_conversation_view(request, id):
    # Validate UUID format
    validated_id = validate_uuid(id, "id")
    
    if request.method == "GET":
        return get_conversation_by_id(conversation_id=validated_id)
    elif request.method == "DELETE":
        # Check authentication for DELETE requests
        authenticator = APIKeyAuthentication()
        try:
            authenticator.authenticate(request)
        except Exception:
            raise AuthenticationFailed('Invalid API Key')
        
        return delete_conversation(conversation_id=validated_id)


@extend_schema(
    methods=["POST"],
    summary="Create a new conversation",
    description="Create a new conversation with an optional title and required description.",
    request=ConversationCreateSerializer,
    responses={
        201: {"description": "Conversation created successfully"},
        400: {"description": "Validation error"},
        401: {"description": "Authentication failed"},
        500: {"description": "Internal server error"},
    },
    examples=[
        OpenApiExample(
            "Create Conversation Request",
            value={
                "title": "My First Conversation",
                "description": "A conversation about AI assistants"
            },
            request_only=True,
        ),
        OpenApiExample(
            "Success Response",
            value={
                "success": True,
                "data": {
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "My First Conversation",
                    "description": "A conversation about AI assistants",
                    "date_created": "2024-01-19T12:00:00Z",
                    "date_updated": "2024-01-19T12:00:00Z"
                },
                "message": "Conversation created successfully"
            },
            response_only=True,
        ),
    ],
    tags=["Conversations"],
)
@api_view(["POST"])
@authentication_classes([APIKeyAuthentication])
def create_conversation_view(request):
    return create_conversation(request.data)

