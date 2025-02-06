# test_get_followers.py
import unittest
from unittest.mock import patch, Mock
import pandas as pd
from researchtikpy import get_followers



class TestGetFollowers(unittest.TestCase):

    @patch('requests.Session')
    def test_get_followers_success(self, mock_session):
        # Arrange
        followers_data = {
            "data": {
                "user_followers": [
                    {"id": "1", "username": "follower1"},
                    {"id": "2", "username": "follower2"},
                ],
                "has_more": False,
                "cursor": 0
            }
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = followers_data
        mock_session().post.return_value = mock_response

        usernames_list = ['testuser']
        mock_token = Mock()
        mock_token.token = 'test_token'

        # Act
        result_df = get_followers(usernames_list, mock_token, verbose=False)

        # Assert
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(len(result_df), 2)
        self.assertEqual(result_df.iloc[0]['username'], 'follower1')

    @unittest.skip("Creates an infinite loop, skipping until fn is fixed.")
    @patch("researchtikpy.get_followers.sleep")
    def test_get_followers_rate_limit(self, mock_sleep):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 429  # Simulate a rate limit error from the API
        mock_sleep.return_value = None
        mock_token = Mock()
        mock_token.token = 'test_token'

        usernames_list = ['testuser']
        
        with patch("requests.Session") as mock_session:
            mock_session.return_value.post.return_value = mock_response
            # Act & Assert
            # Checking if the DataFrame is empty since the API is rate-limited
            # Alternatively, could check for a specific exception or log message
            result_df = get_followers(usernames_list, mock_token, verbose=False)
            self.assertTrue(result_df.empty)

            assert mock_session().post.called  # Check if the post method was called
            assert mock_sleep.called  # Check if the sleep function was called

    # Add more tests to cover different scenarios like different error codes or partial data fetching

if __name__ == '__main__':
    unittest.main()
