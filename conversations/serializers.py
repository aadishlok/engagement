from rest_framework import serializers
from .models import Conversation, Message


class ConversationCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Optional title for the conversation"
    )
    description = serializers.CharField(
        max_length=500,
        required=True,
        help_text="Description of the conversation (required, max 500 characters)"
    )
    
    class Meta:
        model = Conversation
        fields = ["title", "description"]


class ConversationSerializer(serializers.ModelSerializer):
    conversation_id = serializers.UUIDField(read_only=True, help_text="Unique identifier for the conversation")
    title = serializers.CharField(required=False, allow_null=True, help_text="Title of the conversation")
    description = serializers.CharField(help_text="Description of the conversation")
    date_created = serializers.DateTimeField(read_only=True, help_text="Timestamp when conversation was created")
    date_updated = serializers.DateTimeField(read_only=True, help_text="Timestamp when conversation was last updated")
    
    class Meta:
        model = Conversation
        fields = "__all__"


class MessageCreateSerializer(serializers.ModelSerializer):
    text = serializers.CharField(
        required=True,
        help_text="Content of the message (required)"
    )
    conversation = serializers.PrimaryKeyRelatedField(
        queryset=Conversation.objects.all(),
        required=False,
        help_text="UUID of the conversation (automatically set from URL)"
    )
    role = serializers.ChoiceField(
        choices=[('user', 'User'), ('assistant', 'Assistant')],
        default='user',
        help_text="Role of the message sender: 'user' or 'assistant'"
    )
    
    class Meta:
        model = Message
        fields = ["text", "conversation", "role"]


class MessageSerializer(serializers.ModelSerializer):
    message_id = serializers.UUIDField(read_only=True, help_text="Unique identifier for the message")
    conversation = serializers.UUIDField(read_only=True, help_text="UUID of the conversation this message belongs to")
    role = serializers.CharField(help_text="Role of the message sender: 'user' or 'assistant'")
    text = serializers.CharField(help_text="Content of the message")
    date_created = serializers.DateTimeField(read_only=True, help_text="Timestamp when message was created")
    date_updated = serializers.DateTimeField(read_only=True, help_text="Timestamp when message was last updated")
    
    class Meta:
        model = Message
        fields = "__all__"

