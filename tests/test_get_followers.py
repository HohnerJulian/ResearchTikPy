import unittest
from unittest.mock import patch, Mock
import pandas as pd
import requests
from researchtikpy import get_followers
from researchtikpy.social_graph import (
    Username,
    extract_followers,
    get_user_followers,
    iter_followers_responses,
)
from tests.helpers import access_token


class TestGetFollowers(unittest.TestCase):
    @patch("researchtikpy.social_graph.requests.Session")
    def test_get_followers_success(self, mock_session):
        # Arrange
        followers_data = {
            "data": {
                "user_followers": [
                    {"id": "1", "username": "follower1"},
                    {"id": "2", "username": "follower2"},
                ],
                "has_more": False,
                "cursor": 0,
            }
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = followers_data
        mock_session().post.return_value = mock_response

        usernames_list = ["testuser"]
        access_token = "test_access_token"

        # Act
        result_df = get_followers(usernames_list, access_token, verbose=False)

        # Assert
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(len(result_df), 2)
        self.assertEqual(result_df.iloc[0]["username"], "follower1")

    @patch("researchtikpy.social_graph.requests.Session")
    def test_get_followers_rate_limit(self, mock_session):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 429  # Simulate a rate limit error from the API
        mock_session().post.return_value = mock_response

        usernames_list = ["testuser"]
        access_token = "test_access_token"

        # Act & Assert
        # Checking if the DataFrame is empty since the API is rate-limited
        # Alternatively, could check for a specific exception or log message
        result_df = get_followers(usernames_list, access_token, verbose=False)
        self.assertTrue(result_df.empty)

    def test_get_user_followers(self):
        response: requests.Response = get_user_followers(
            access_token=access_token(),
            session=requests.Session(),
            username="realdonaldtrump",
        )
        assert response.status_code == 200
        n_followers = len(extract_followers(response))
        assert n_followers > 70, n_followers

    def test_get_many_followers(self):
        resps: list[requests.Response] = []
        for resp in iter_followers_responses(
            access_token=access_token(), username="realdonaldtrump"
        ):
            assert resp.status_code == 200
            resps.append(resp)
            if len(resps) > 5:
                break
        followers: list[Username] = [
            follower for resp in resps for follower in extract_followers(resp)
        ]
        assert len(followers) > 400

    # Add more tests to cover different scenarios like different error codes or partial data fetching


if __name__ == "__main__":
    unittest.main()
