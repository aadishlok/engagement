from django.urls import path
from .views.conversation_views import get_or_delete_conversation_view, create_conversation_view
from .views.message_views import get_messages_view, create_message_view, delete_message_view

urlpatterns = [
    path("", create_conversation_view, name="create-conversation"),
    path("<uuid:id>", get_or_delete_conversation_view, name="get-or-delete-conversation"),
    path("<uuid:id>/messages", get_messages_view, name="get-messages-for-conversation"),
    path("<uuid:id>/messages/create", create_message_view, name="create-message-for-conversation"),
    path("<uuid:id>/messages/<uuid:message_id>", delete_message_view, name="delete-message-from-conversation"),
]