from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from unittest.mock import patch, MagicMock
from conversations.services.conversation_service import create_conversation, delete_conversation
from conversations.models import Conversation
import uuid
from django.http import Http404


class ConversationServiceTestCase(TestCase):
    """Unit tests for conversation_service functions"""
    
    def setUp(self):
        self.valid_data = {
            "description": "Test conversation description",
            "title": "Test Title"
        }
    

    def test_create_conversation_success_201(self):
        """Test creating a conversation with valid data returns 201"""
        response = create_conversation(self.valid_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Conversation created successfully")
        self.assertIn('data', response.data)
        self.assertIn('conversation_id', response.data['data'])
        self.assertEqual(response.data['data']['description'], "Test conversation description")
        self.assertEqual(response.data['data']['title'], "Test Title")
        
        conversation_id = response.data['data']['conversation_id']
        self.assertTrue(Conversation.objects.filter(conversation_id=conversation_id).exists())
    

    def test_create_conversation_success_without_title(self):
        """Test creating a conversation without optional title returns 201"""
        data = {"description": "Test conversation without title"}
        response = create_conversation(data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], status.HTTP_201_CREATED)
        self.assertIn('conversation_id', response.data['data'])
        self.assertEqual(response.data['data']['description'], "Test conversation without title")
    

    def test_create_conversation_validation_error_400(self):
        """Test creating a conversation with invalid data returns 400"""
        invalid_data = {"title": "Test Title"}
        
        with self.assertRaises(ValidationError) as context:
            create_conversation(invalid_data)
        
        self.assertIsNotNone(context.exception)
        # ValidationError can have field-specific errors or a 'detail' key
        self.assertTrue(
            'detail' in context.exception.detail or 
            'description' in context.exception.detail or
            len(context.exception.detail) > 0
        )
    

    def test_create_conversation_validation_error_empty_data_400(self):
        """Test creating a conversation with empty data returns 400"""
        empty_data = {}
        
        with self.assertRaises(ValidationError):
            create_conversation(empty_data)
    

    @patch('conversations.services.conversation_service.ConversationCreateSerializer')
    def test_create_conversation_serializer_save_error_500(self, mock_serializer_class):
        """Test that serializer save errors propagate as 500"""
        mock_serializer = MagicMock()
        mock_serializer_class.return_value = mock_serializer
        mock_serializer.is_valid.return_value = True
        mock_serializer.save.side_effect = Exception("Unexpected error during save")
        
        with self.assertRaises(Exception):
            create_conversation(self.valid_data)
    
    def test_create_conversation_response_structure(self):
        """Test that success response has correct structure"""
        response = create_conversation(self.valid_data)

        self.assertIn('code', response.data)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        
        self.assertIn('conversation_id', response.data['data'])
        self.assertIn('description', response.data['data'])
        self.assertIn('date_created', response.data['data'])
        self.assertIn('date_updated', response.data['data'])
    
    def test_create_conversation_creates_unique_ids(self):
        """Test that each conversation gets a unique ID"""
        response1 = create_conversation({"description": "First conversation"})
        response2 = create_conversation({"description": "Second conversation"})
        
        id1 = response1.data['data']['conversation_id']
        id2 = response2.data['data']['conversation_id']
        
        self.assertNotEqual(id1, id2)
    
    def test_create_conversation_sets_timestamps(self):
        """Test that created conversation has proper timestamps"""
        response = create_conversation(self.valid_data)
        
        data = response.data['data']
        self.assertIn('date_created', data)
        self.assertIn('date_updated', data)
        self.assertIsNotNone(data['date_created'])
        self.assertIsNotNone(data['date_updated'])


    def test_delete_conversation_success_204(self):
        """Test deleting an existing conversation returns 204"""
        conversation = Conversation.objects.create(
            description="Test conversation to delete",
            title="Test Title"
        )
        conversation_id = conversation.conversation_id
        self.assertTrue(Conversation.objects.filter(conversation_id=conversation_id).exists())
        
        response = delete_conversation(str(conversation_id))
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['code'], status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], "Conversation deleted successfully")
        self.assertIsNone(response.data['data'])
        
        self.assertFalse(Conversation.objects.filter(conversation_id=conversation_id).exists())


    def test_delete_conversation_not_found_404(self):
        """Test deleting a non-existent conversation raises 404"""
        
        fake_id = uuid.uuid4()
        
        with self.assertRaises(Http404):
            delete_conversation(str(fake_id))


    def test_get_conversation_by_id_success_200(self):
        """Test retrieving an existing conversation returns 200"""
        from conversations.services.conversation_service import get_conversation_by_id
        
        conversation = Conversation.objects.create(
            description="Test conversation to retrieve",
            title="Test Title"
        )
        conversation_id = str(conversation.conversation_id)
        
        response = get_conversation_by_id(conversation_id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Conversation retrieved successfully")
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['conversation_id'], conversation_id)
        self.assertEqual(response.data['data']['description'], "Test conversation to retrieve")
        self.assertEqual(response.data['data']['title'], "Test Title")
        self.assertIn('date_created', response.data['data'])
        self.assertIn('date_updated', response.data['data'])


    def test_get_conversation_by_id_not_found_404(self):
        """Test retrieving a non-existent conversation raises 404"""
        from conversations.services.conversation_service import get_conversation_by_id
        
        fake_id = str(uuid.uuid4())
        
        with self.assertRaises(Http404):
            get_conversation_by_id(fake_id)


    def test_get_conversation_by_id_invalid_uuid_400(self):
        """Test that invalid UUID format raises ValidationError (400)"""
        from conversations.services.conversation_service import get_conversation_by_id
        from django.core.exceptions import ValidationError
        
        invalid_id = "not-a-valid-uuid"
        
        with self.assertRaises(ValidationError) as context:
            get_conversation_by_id(invalid_id)
        
        self.assertIsNotNone(context.exception)
        # Verify it's a UUID validation error
        self.assertIn('UUID', str(context.exception))

