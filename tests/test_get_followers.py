# test_get_followers.py
import unittest
from unittest.mock import patch, Mock
import pandas as pd
from researchtikpy import get_followers

class TestGetFollowers(unittest.TestCase):

    @patch('researchtikpy.requests.Session')
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
        access_token = 'test_access_token'

        # Act
        result_df = get_followers(usernames_list, access_token, verbose=False)

        # Assert
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(len(result_df), 2)
        self.assertEqual(result_df.iloc[0]['username'], 'follower1')

    @patch('researchtikpy.requests.Session')
    def test_get_followers_rate_limit(self, mock_session):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 429  # Simulate a rate limit error from the API
        mock_session().post.return_value = mock_response

        usernames_list = ['testuser']
        access_token = 'test_access_token'

        # Act & Assert
        # Checking if the DataFrame is empty since the API is rate-limited
        # Alternatively, could check for a specific exception or log message
        result_df = get_followers(usernames_list, access_token, verbose=False)
        self.assertTrue(result_df.empty)

    # Add more tests to cover different scenarios like different error codes or partial data fetching

if __name__ == '__main__':
    unittest.main()
