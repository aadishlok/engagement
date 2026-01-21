from django.shortcuts import get_object_or_404
from rest_framework import status
from ..models import Conversation
from ..serializers import ConversationSerializer, ConversationCreateSerializer
from ..utils import prepare_success_response


def get_conversation_by_id(conversation_id: str):
    conversation = get_object_or_404(
        Conversation, conversation_id=conversation_id
    )
    serializer = ConversationSerializer(conversation)
    return prepare_success_response(
        data=serializer.data,
        message="Conversation retrieved successfully",
        status_code=status.HTTP_200_OK
    )


def create_conversation(data):
    serializer = ConversationCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    conversation = serializer.save()
    serialized_data = ConversationSerializer(conversation)

    return prepare_success_response(
        data=serialized_data.data,
        message="Conversation created successfully",
        status_code=status.HTTP_201_CREATED
    )


def delete_conversation(conversation_id: str):
    conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
    conversation.delete()

    return prepare_success_response(
        data=None,
        message="Conversation deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT
    )