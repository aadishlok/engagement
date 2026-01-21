from django.shortcuts import get_object_or_404
from rest_framework import status
from ..models import Conversation
from ..serializers import ConversationSerializer, ConversationCreateSerializer
from ..utils import prepare_success_response
from ..logging_utils import log_info, log_warning


def get_conversation_by_id(conversation_id: str):
    log_info(
        f"Retrieving conversation: {conversation_id}",
        {"conversation_id": str(conversation_id)}
    )
    conversation = get_object_or_404(
        Conversation, conversation_id=conversation_id
    )
    serializer = ConversationSerializer(conversation)
    log_info(
        f"Successfully retrieved conversation: {conversation_id}",
        {"conversation_id": str(conversation_id), "title": conversation.title}
    )
    return prepare_success_response(
        data=serializer.data,
        message="Conversation retrieved successfully",
        status_code=status.HTTP_200_OK
    )


def create_conversation(data):
    
    serializer = ConversationCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    
    # Warning if description is very short (potential data quality issue)
    if len(data.get("description", "")) < 10:
        log_warning(
            f"Conversation created with short description (length: {len(data.get('description', ''))})",
            {"description_length": len(data.get("description", ""))}
        )
    
    conversation = serializer.save()
    serialized_data = ConversationSerializer(conversation)

    return prepare_success_response(
        data=serialized_data.data,
        message="Conversation created successfully",
        status_code=status.HTTP_201_CREATED
    )


def delete_conversation(conversation_id: str):
    conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
    
    # Warning if conversation has many messages (cascade delete will remove them)
    message_count = conversation.messages.count()
    if message_count > 100:
        log_warning(
            f"Deleting conversation with {message_count} messages (cascade delete)",
            {"conversation_id": str(conversation_id), "message_count": message_count}
        )
    
    conversation.delete()

    return prepare_success_response(
        data=None,
        message="Conversation deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT
    )