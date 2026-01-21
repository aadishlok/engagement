from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Conversation, Message
import uuid


class ConversationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.api_key = "neuRealities_assessment"
        self.client.credentials(HTTP_X_API_KEY=self.api_key)
        self.conversation_url = reverse("create-conversation")
        
    def test_create_conversation_success(self):
        """Test creating a conversation with valid data"""
        data = {
            "description": "Test conversation",
            "title": "Test Title"
        }
        response = self.client.post(self.conversation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('conversation_id', response.data['data'])
        self.assertEqual(response.data['data']['description'], "Test conversation")
        self.assertEqual(response.data['data']['title'], "Test Title")
        self.assertEqual(response.data['message'], "Conversation created successfully")
        
    def test_create_conversation_without_title(self):
        """Test creating a conversation without title (optional field)"""
        data = {
            "description": "Test conversation without title"
        }
        response = self.client.post(self.conversation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('conversation_id', response.data['data'])
        
    def test_create_conversation_missing_description(self):
        """Test creating a conversation without required description"""
        data = {}
        response = self.client.post(self.conversation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_conversation_without_auth(self):
        """Test creating a conversation without API key"""
        client = APIClient()
        data = {"description": "Test conversation"}
        response = client.post(self.conversation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_conversation_success(self):
        """Test retrieving a conversation by ID"""
        # Create a conversation first
        conversation = Conversation.objects.create(description="Test conversation")
        url = reverse("get-or-delete-conversation", kwargs={"id": conversation.conversation_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['conversation_id'], str(conversation.conversation_id))
        self.assertEqual(response.data['data']['description'], "Test conversation")
        self.assertEqual(response.data['message'], "Conversation retrieved successfully")
        
    def test_get_conversation_without_auth(self):
        """Test retrieving a conversation without authentication (GET should work)"""
        conversation = Conversation.objects.create(description="Test conversation")
        client = APIClient()  # No authentication
        url = reverse("get-or-delete-conversation", kwargs={"id": conversation.conversation_id})
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
    def test_get_conversation_with_q_filter(self):
        """Test retrieving a conversation with q filter"""
        conversation = Conversation.objects.create(
            title="AI Chat",
            description="A conversation about artificial intelligence"
        )
        url = reverse("get-or-delete-conversation", kwargs={"id": conversation.conversation_id})
        
        # Test with matching q parameter
        response = self.client.get(url, {"q": "AI"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Test with non-matching q parameter
        response = self.client.get(url, {"q": "nonexistent"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_get_conversation_not_found(self):
        """Test retrieving a non-existent conversation"""
        fake_id = uuid.uuid4()
        url = reverse("get-or-delete-conversation", kwargs={"id": fake_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_conversation_success(self):
        """Test deleting a conversation"""
        conversation = Conversation.objects.create(description="Test conversation")
        url = reverse("get-or-delete-conversation", kwargs={"id": conversation.conversation_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Conversation deleted successfully")
        self.assertFalse(Conversation.objects.filter(conversation_id=conversation.conversation_id).exists())
        
    def test_delete_conversation_without_auth(self):
        """Test deleting a conversation without authentication (should fail)"""
        conversation = Conversation.objects.create(description="Test conversation")
        client = APIClient()  # No authentication
        url = reverse("get-or-delete-conversation", kwargs={"id": conversation.conversation_id})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_conversation_cascades_messages(self):
        """Test that deleting a conversation also deletes its messages"""
        conversation = Conversation.objects.create(description="Test conversation")
        message = Message.objects.create(
            conversation=conversation,
            text="Test message",
            role="user"
        )
        url = reverse("get-or-delete-conversation", kwargs={"id": conversation.conversation_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(Message.objects.filter(message_id=message.message_id).exists())


class MessageAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.api_key = "neuRealities_assessment"
        self.client.credentials(HTTP_X_API_KEY=self.api_key)
        self.conversation = Conversation.objects.create(description="Test conversation")
        
    def test_create_user_message_success(self):
        """Test creating a user message"""
        url = reverse("create-message-for-conversation", kwargs={"id": self.conversation.conversation_id})
        data = {
            "text": "Hello, how are you?",
            "role": "user"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('message_id', response.data['data'])
        self.assertEqual(response.data['data']['text'], "Hello, how are you?")
        self.assertEqual(response.data['data']['role'], "user")
        self.assertEqual(response.data['message'], "Message created successfully")
        
    def test_create_user_message_generates_assistant_response(self):
        """Test that creating a user message automatically generates an assistant response synchronously"""
        url = reverse("create-message-for-conversation", kwargs={"id": self.conversation.conversation_id})
        data = {
            "text": "Hello",
            "role": "user"
        }
        response = self.auth_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Assistant response is generated synchronously, so it should be available immediately
        messages = Message.objects.filter(conversation=self.conversation).order_by('date_created')
        self.assertEqual(messages.count(), 2)  # User message + assistant response
        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[1].role, "assistant")
        self.assertIsNotNone(messages[1].text)
        
    def test_create_assistant_message_directly(self):
        """Test creating an assistant message directly (no auto-response)"""
        url = reverse("create-message-for-conversation", kwargs={"id": self.conversation.conversation_id})
        data = {
            "text": "I am an assistant",
            "role": "assistant"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that only one message was created (no auto-response for assistant messages)
        messages = Message.objects.filter(conversation=self.conversation)
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages[0].role, "assistant")
        
    def test_create_message_missing_text(self):
        """Test creating a message without required text field"""
        url = reverse("create-message-for-conversation", kwargs={"id": self.conversation.conversation_id})
        data = {"role": "user"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_get_messages_success(self):
        """Test retrieving messages for a conversation"""
        # Create some messages
        Message.objects.create(conversation=self.conversation, text="Message 1", role="user")
        Message.objects.create(conversation=self.conversation, text="Message 2", role="assistant")
        Message.objects.create(conversation=self.conversation, text="Message 3", role="user")
        
        url = reverse("get-messages-for-conversation", kwargs={"id": self.conversation.conversation_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('results', response.data['data'])  # Paginated response
        self.assertEqual(len(response.data['data']['results']), 3)
        self.assertEqual(response.data['message'], "Messages retrieved successfully")
        
    def test_get_messages_without_auth(self):
        """Test retrieving messages without authentication (GET should work)"""
        Message.objects.create(conversation=self.conversation, text="Message 1", role="user")
        client = APIClient()  # No authentication
        url = reverse("get-messages-for-conversation", kwargs={"id": self.conversation.conversation_id})
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
    def test_get_messages_with_q_filter(self):
        """Test filtering messages by text content using q parameter"""
        Message.objects.create(conversation=self.conversation, text="Hello world", role="user")
        Message.objects.create(conversation=self.conversation, text="Goodbye", role="assistant")
        Message.objects.create(conversation=self.conversation, text="Hello again", role="user")
        
        url = reverse("get-messages-for-conversation", kwargs={"id": self.conversation.conversation_id})
        
        # Filter by "Hello"
        response = self.client.get(url, {"q": "Hello"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']['results']), 2)
        
        # Filter by "Goodbye"
        response = self.client.get(url, {"q": "Goodbye"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['text'], "Goodbye")
        
    def test_get_messages_with_role_filter(self):
        """Test filtering messages by role"""
        Message.objects.create(conversation=self.conversation, text="User message 1", role="user")
        Message.objects.create(conversation=self.conversation, text="Assistant message 1", role="assistant")
        Message.objects.create(conversation=self.conversation, text="User message 2", role="user")
        
        url = reverse("get-messages-for-conversation", kwargs={"id": self.conversation.conversation_id})
        
        # Filter by user role
        response = self.client.get(url, {"role": "user"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']['results']), 2)
        for msg in response.data['data']['results']:
            self.assertEqual(msg['role'], "user")
        
        # Filter by assistant role
        response = self.client.get(url, {"role": "assistant"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['role'], "assistant")
        
    def test_get_messages_with_combined_filters(self):
        """Test filtering messages with both q and role parameters"""
        Message.objects.create(conversation=self.conversation, text="Hello user", role="user")
        Message.objects.create(conversation=self.conversation, text="Hello assistant", role="assistant")
        Message.objects.create(conversation=self.conversation, text="Goodbye user", role="user")
        
        url = reverse("get-messages-for-conversation", kwargs={"id": self.conversation.conversation_id})
        
        # Filter by "Hello" and role "user"
        response = self.client.get(url, {"q": "Hello", "role": "user"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['text'], "Hello user")
        self.assertEqual(response.data['data']['results'][0]['role'], "user")
        
    def test_get_messages_pagination(self):
        """Test that message listing is paginated"""
        # Create more than 10 messages (default page size)
        for i in range(15):
            Message.objects.create(
                conversation=self.conversation,
                text=f"Message {i}",
                role="user"
            )
        
        url = reverse("get-messages-for-conversation", kwargs={"id": self.conversation.conversation_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']['results']), 10)  # First page
        self.assertIn('next', response.data['data'])  # Has next page
        
    def test_get_messages_empty_conversation(self):
        """Test retrieving messages from a conversation with no messages"""
        url = reverse("get-messages-for-conversation", kwargs={"id": self.conversation.conversation_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']['results']), 0)
        
    def test_delete_message_success(self):
        """Test deleting a message"""
        message = Message.objects.create(
            conversation=self.conversation,
            text="Test message",
            role="user"
        )
        url = reverse("delete-message-from-conversation", kwargs={
            "id": self.conversation.conversation_id,
            "message_id": message.message_id
        })
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Message deleted successfully")
        self.assertFalse(Message.objects.filter(message_id=message.message_id).exists())
        
    def test_delete_message_not_found(self):
        """Test deleting a non-existent message"""
        fake_message_id = uuid.uuid4()
        url = reverse("delete-message-from-conversation", kwargs={
            "id": self.conversation.conversation_id,
            "message_id": fake_message_id
        })
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_create_message_without_auth(self):
        """Test creating a message without API key"""
        client = APIClient()
        url = reverse("create-message-for-conversation", kwargs={"id": self.conversation.conversation_id})
        data = {"text": "Test", "role": "user"}
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_message_without_auth(self):
        """Test deleting a message without authentication (should fail)"""
        message = Message.objects.create(
            conversation=self.conversation,
            text="Test message",
            role="user"
        )
        client = APIClient()  # No authentication
        url = reverse("delete-message-from-conversation", kwargs={
            "id": self.conversation.conversation_id,
            "message_id": message.message_id
        })
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.conversation_url = reverse("create-conversation")
        
    def test_valid_api_key(self):
        """Test that valid API key allows access"""
        self.client.credentials(HTTP_X_API_KEY="neuRealities_assessment")
        data = {"description": "Test"}
        response = self.client.post(self.conversation_url, data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_invalid_api_key(self):
        """Test that invalid API key is rejected"""
        self.client.credentials(HTTP_X_API_KEY="invalid_key")
        data = {"description": "Test"}
        response = self.client.post(self.conversation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_missing_api_key(self):
        """Test that missing API key is rejected"""
        client = APIClient()
        data = {"description": "Test"}
        response = client.post(self.conversation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
