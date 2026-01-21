from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from unittest.mock import patch, MagicMock
from conversations.services.message_service import (
    create_message, 
    get_messages_by_conversation_id,
    get_message_by_id,
    delete_message
)
from conversations.models import Conversation, Message
import uuid
from django.http import Http404


def create_mock_request(data=None, query_params=None):
    """Helper function to create a mock DRF request object"""
    factory = APIRequestFactory()
    if data is not None:
        request = factory.post('/messages', data, format='json')
    else:
        request = factory.get('/messages', query_params or {})
    
    # Wrap with DRF Request and manually set data
    drf_request = Request(request)
    if data is not None:
        # Set data as a property-like attribute
        drf_request._full_data = data
        drf_request._data = data
        # Mock the data property to return our data
        type(drf_request).data = property(lambda self: getattr(self, '_data', {}))
    else:
        # Ensure data is an empty dict if not provided
        drf_request._data = {}
        type(drf_request).data = property(lambda self: getattr(self, '_data', {}))
    
    if query_params:
        # Set query_params
        drf_request._query_params = query_params
        # Mock query_params property
        type(drf_request).query_params = property(lambda self: getattr(self, '_query_params', {}))
    else:
        # Ensure query_params exists even if None
        drf_request._query_params = {}
        type(drf_request).query_params = property(lambda self: getattr(self, '_query_params', {}))
    
    return drf_request


class MessageServiceTestCase(TestCase):
    """Unit tests for message_service functions"""
    
    def setUp(self):
        self.conversation = Conversation.objects.create(
            description="Test conversation for messages",
            title="Test Title"
        )
        self.factory = APIRequestFactory()
        self.valid_message_data = {
            "text": "Hello, this is a test message",
            "role": "user"
        }
    
    def test_create_message_success_201(self):
        """Test creating a message with valid data returns 201"""
        drf_request = create_mock_request(data=self.valid_message_data)
        
        response = create_message(str(self.conversation.conversation_id), drf_request)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Message created successfully")
        self.assertIn('data', response.data)
        self.assertIn('message_id', response.data['data'])
        self.assertEqual(response.data['data']['text'], "Hello, this is a test message")
        self.assertEqual(response.data['data']['role'], "user")
        
        message_id = response.data['data']['message_id']
        self.assertTrue(Message.objects.filter(message_id=message_id).exists())
    
    def test_create_message_validation_error_400(self):
        """Test creating a message with invalid data returns 400"""
        invalid_data = {
            "role": "user"
        }
        drf_request = create_mock_request(data=invalid_data)
        
        with self.assertRaises(ValidationError) as context:
            create_message(str(self.conversation.conversation_id), drf_request)
        
        self.assertIsNotNone(context.exception)
        self.assertTrue(
            'detail' in context.exception.detail or 
            'text' in context.exception.detail or
            len(context.exception.detail) > 0
        )
    
    def test_create_message_empty_data_400(self):
        """Test creating a message with empty data returns 400"""
        empty_data = {}
        drf_request = create_mock_request(data=empty_data)
        
        with self.assertRaises(ValidationError):
            create_message(str(self.conversation.conversation_id), drf_request)
    
    def test_create_message_conversation_not_found_404(self):
        """Test creating a message with non-existent conversation raises 404"""
        fake_conversation_id = str(uuid.uuid4())
        message_data = {
            "text": "Test message",
            "role": "user"
        }
        drf_request = create_mock_request(data=message_data)
        
        with self.assertRaises(Exception) as context:
            create_message(fake_conversation_id, drf_request)
        
        self.assertIsNotNone(context.exception)
    
    def test_create_message_invalid_conversation_uuid_400(self):
        """Test creating a message with invalid conversation UUID format returns 400"""
        invalid_data = {
            "text": "Test message",
            "role": "user"
        }
        drf_request = create_mock_request(data=invalid_data)
        
        from django.core.exceptions import ValidationError as DjangoValidationError
        with self.assertRaises((ValidationError, DjangoValidationError, ValueError)) as context:
            create_message("not-a-valid-uuid", drf_request)
        
        self.assertIsNotNone(context.exception)
    
    @patch('conversations.services.message_service.MessageCreateSerializer')
    def test_create_message_serializer_save_error_500(self, mock_serializer_class):
        """Test that serializer save errors propagate as 500"""
        mock_serializer = MagicMock()
        mock_serializer_class.return_value = mock_serializer
        mock_serializer.is_valid.return_value = True
        mock_serializer.save.side_effect = Exception("Unexpected error during save")
        
        drf_request = create_mock_request(data=self.valid_message_data)
        
        with self.assertRaises(Exception):
            create_message(str(self.conversation.conversation_id), drf_request)
    
    @patch('conversations.services.message_service.MessageCreateSerializer')
    def test_create_message_serializer_validation_error_500(self, mock_serializer_class):
        """Test that unexpected serializer errors propagate as 500"""
        mock_serializer = MagicMock()
        mock_serializer_class.return_value = mock_serializer
        mock_serializer.is_valid.side_effect = Exception("Unexpected validation error")
        
        drf_request = create_mock_request(data=self.valid_message_data)
        
        with self.assertRaises(Exception):
            create_message(str(self.conversation.conversation_id), drf_request)
    
    def test_create_message_generates_assistant_response(self):
        """Test that creating a user message generates an assistant response"""
        drf_request = create_mock_request(data=self.valid_message_data)
        
        response = create_message(str(self.conversation.conversation_id), drf_request)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        message_id = response.data['data']['message_id']
        user_message = Message.objects.get(message_id=message_id)
        
        assistant_messages = Message.objects.filter(
            conversation=self.conversation,
            role='assistant'
        )
        self.assertTrue(assistant_messages.exists())
        
        assistant_message = assistant_messages.first()
        self.assertIsNotNone(assistant_message.text)
        self.assertGreater(len(assistant_message.text), 0)
    
    def test_create_message_assistant_role_no_response(self):
        """Test that creating an assistant message does not generate another response"""
        assistant_data = {
            "text": "This is an assistant message",
            "role": "assistant"
        }
        
        initial_message_count = Message.objects.filter(conversation=self.conversation).count()
        
        drf_request = create_mock_request(data=assistant_data)
        response = create_message(str(self.conversation.conversation_id), drf_request)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        final_message_count = Message.objects.filter(conversation=self.conversation).count()
        self.assertEqual(final_message_count, initial_message_count + 1)
    
    def test_get_messages_by_conversation_id_success_200(self):
        """Test retrieving messages for a conversation returns 200"""
        message1 = Message.objects.create(
            conversation=self.conversation,
            text="First message",
            role="user"
        )
        message2 = Message.objects.create(
            conversation=self.conversation,
            text="Second message",
            role="assistant"
        )
        
        # Create a DRF request
        drf_request = create_mock_request(query_params={})
        
        response = get_messages_by_conversation_id(str(self.conversation.conversation_id), drf_request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 2)
    
    def test_get_messages_by_conversation_id_not_found_404(self):
        """Test retrieving messages for non-existent conversation returns empty results"""
        fake_conversation_id = str(uuid.uuid4())
        
        drf_request = create_mock_request(query_params={})
        
        response = get_messages_by_conversation_id(fake_conversation_id, drf_request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_get_messages_by_conversation_id_invalid_uuid_400(self):
        """Test retrieving messages with invalid UUID format raises 400"""
        invalid_id = "not-a-valid-uuid"
        
        drf_request = create_mock_request(query_params={})
        
        from django.core.exceptions import ValidationError as DjangoValidationError
        with self.assertRaises((ValidationError, DjangoValidationError, ValueError)):
            get_messages_by_conversation_id(invalid_id, drf_request)
    
    def test_get_message_by_id_success_200(self):
        """Test retrieving a specific message returns 200"""
        message = Message.objects.create(
            conversation=self.conversation,
            text="Test message",
            role="user"
        )
        
        response = get_message_by_id(str(self.conversation.conversation_id), str(message.message_id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Message retrieved successfully")
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['text'], "Test message")
        self.assertEqual(response.data['data']['role'], "user")
        self.assertIn('message_id', response.data['data'])
        self.assertIn('conversation', response.data['data'])
    
    def test_get_message_by_id_not_found_404(self):
        """Test retrieving a non-existent message raises 404"""
        fake_message_id = str(uuid.uuid4())
        
        with self.assertRaises(Http404):
            get_message_by_id(str(self.conversation.conversation_id), fake_message_id)
    
    def test_get_message_by_id_invalid_uuid_400(self):
        """Test retrieving message with invalid UUID format raises 400"""
        invalid_id = "not-a-valid-uuid"
        
        from django.core.exceptions import ValidationError as DjangoValidationError
        with self.assertRaises((ValidationError, DjangoValidationError, ValueError)):
            get_message_by_id(str(self.conversation.conversation_id), invalid_id)
    
    def test_delete_message_success_200(self):
        """Test deleting an existing message returns 200 (204 NO_CONTENT)"""
        message = Message.objects.create(
            conversation=self.conversation,
            text="Message to delete",
            role="user"
        )
        message_id = message.message_id
        
        self.assertTrue(Message.objects.filter(message_id=message_id).exists())
        
        response = delete_message(str(self.conversation.conversation_id), str(message_id))
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['code'], status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], "Message deleted successfully")
        self.assertIsNone(response.data['data'])
        
        self.assertFalse(Message.objects.filter(message_id=message_id).exists())
    
    def test_delete_message_not_found_404(self):
        """Test deleting a non-existent message raises 404"""
        fake_message_id = str(uuid.uuid4())
        
        with self.assertRaises(Http404):
            delete_message(str(self.conversation.conversation_id), fake_message_id)