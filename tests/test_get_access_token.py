# test_get_access_token.py
import unittest
from unittest.mock import patch
from researchtikpy.get_access_token import get_access_token

class TestGetAccessToken(unittest.TestCase):

    @patch('researchtikpy.get_access_token.requests.post')
    def test_token_retrieval_success(self, mock_post):
        # Arrange
        expected_response = {
            "access_token": "test_access_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_response
        client_key = 'test_client_key'
        client_secret = 'test_client_secret'

        # Act
        response = get_access_token(client_key, client_secret)

        # Assert
        self.assertEqual(response, expected_response)

    @patch('researchtikpy.get_access_token.requests.post')
    def test_token_retrieval_failure(self, mock_post):
        # Arrange
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = 'Bad Request'
        client_key = 'test_client_key'
        client_secret = 'test_client_secret'

        # Act & Assert
        with self.assertRaises(Exception) as context:
            get_access_token(client_key, client_secret)
        
        self.assertIn('Failed to obtain access token', str(context.exception))

if __name__ == '__main__':
    unittest.main()
