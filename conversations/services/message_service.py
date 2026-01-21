from django.shortcuts import get_object_or_404
from rest_framework import status
from ..models import Message
from ..serializers import MessageSerializer, MessageCreateSerializer
from ..logging_utils import log_error
from ..utils import prepare_success_response, prepare_paginated_response


def get_messages_by_conversation_id(conversation_id: str, request):
    q = request.query_params.get('q', None)
    role = request.query_params.get('role', None)
    page_size = request.query_params.get('page_size', 10)
    
    messages = Message.objects.filter(conversation_id=conversation_id)
    
    if q:
        messages = messages.filter(text__icontains=q)

    if role:
        messages = messages.filter(role=role)

    try:
        page_size = int(page_size) if page_size else 10
    except (ValueError, TypeError):
        page_size = 10
    
    return prepare_paginated_response(
        messages, 
        request, 
        MessageSerializer, 
        page_size=page_size, 
        message="Messages retrieved successfully"
    )


def get_message_by_id(conversation_id: str, message_id: str):
    message = get_object_or_404(Message, conversation_id=conversation_id, message_id=message_id)
    serializer = MessageSerializer(message)
    return prepare_success_response(
        data=serializer.data,
        message="Message retrieved successfully",
        status_code=status.HTTP_200_OK
    )


def get_assistant_response(user_message_text: str) -> str:
    user_text_lower = user_message_text.lower()
    
    if any(word in user_text_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! How can I assist you today?"
    elif any(word in user_text_lower for word in ['help', 'support']):
        return "I'm here to help! What do you need assistance with?"
    elif '?' in user_message_text:
        return "That's an interesting question. Let me think about that..."
    elif any(word in user_text_lower for word in ['thank', 'thanks']):
        return "You're welcome! Is there anything else I can help with?"
    else:
        return "I understand. Can you tell me more about that?"


def create_message(conversation_id: str, request):
    message_data = {
        "conversation": conversation_id,
        **request.data
    }
    serializer = MessageCreateSerializer(data=message_data)
    serializer.is_valid(raise_exception=True)
    message = serializer.save()
    serialized_message = MessageSerializer(message)
    
    if message.role == 'user':
        try:
            assistant_response_text = get_assistant_response(message.text)
            assistant_message_data = {
                "conversation": str(message.conversation.conversation_id),
                "text": assistant_response_text,
                "role": "assistant"
            }
            assistant_serializer = MessageCreateSerializer(data=assistant_message_data)
            assistant_serializer.is_valid(raise_exception=True)
            assistant_serializer.save()
        except Exception as e:
            log_error(
                f"Failed to generate assistant response: {e}",
                {"conversation_id": str(message.conversation.conversation_id), "error": str(e)}
            )
    
    return prepare_success_response(
        data=serialized_message.data,
        message="Message created successfully",
        status_code=status.HTTP_201_CREATED
    )


def delete_message(conversation_id: str, message_id: str):
    message = get_object_or_404(
        Message, conversation_id=conversation_id, message_id=message_id
    )
    message.delete()
    return prepare_success_response(
        data=None,
        message="Message deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT
    )