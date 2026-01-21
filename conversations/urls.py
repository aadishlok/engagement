from django.urls import path
from .views.conversation_views import get_or_delete_conversation_view, create_conversation_view
from .views.message_views import get_or_create_message_view, delete_message_view

urlpatterns = [
    path("", create_conversation_view, name="create-conversation"),
    path("<str:id>", get_or_delete_conversation_view, name="get-or-delete-conversation"),
    path("<str:id>/messages", get_or_create_message_view, name="get-or-create-message"),
    path("<str:id>/messages/<str:message_id>", delete_message_view, name="delete-message-from-conversation"),
]