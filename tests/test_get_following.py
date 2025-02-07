from pathlib import Path
import unittest

import pandas as pd
import requests

from researchtikpy.social_graph import (
    Username,
    dump_users_following,
    extract_following,
    get_user_following,
    iter_following_responses,
)
from tests.helpers import access_token


from unittest.mock import patch, MagicMock
from researchtikpy import get_following


class TestGetFollowing(unittest.TestCase):
    @patch("researchtikpy.get_following.requests.Session")
    def test_get_following_success(self, mock_session):
        # Arrange
        expected_following_data = {
            "data": {
                "user_following": [
                    {"id": "1", "username": "following1"},
                    {"id": "2", "username": "following2"},
                ],
                "has_more": False,
                "cursor": 0,
            }
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_following_data
        mock_session.return_value.post.return_value = mock_response
        usernames_list = ["testuser"]
        access_token = "test_access_token"

        # Act
        result_df = get_following(
            usernames_list, access_token, max_count=2, verbose=False
        )

        # Assert
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(len(result_df), 2)
        self.assertEqual(list(result_df["username"]), ["following1", "following2"])

    @unittest.skip("Skipping test_get_followings_rate_limit")
    @patch("researchtikpy.social_graph.requests.Session")
    def test_get_following_rate_limit(self, mock_session):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 429  # Simulate rate limit error from the API
        mock_session.return_value.post.return_value = mock_response
        usernames_list = ["testuser"]
        access_token = "test_access_token"

        # Act
        result_df = get_following(usernames_list, access_token, verbose=False)

        # Assert
        self.assertTrue(result_df.empty)

    def test_get_user_following(self):
        response: requests.Response = get_user_following(
            access_token=access_token(),
            session=requests.Session(),
            username="nba",
        )
        assert response.status_code == 200
        n_following = len(extract_following(response))
        assert n_following > 90, n_following

    def test_get_many_following(self):
        resps: list[requests.Response] = []
        for resp in iter_following_responses(
            access_token=access_token(), username="nba"
        ):
            assert resp.status_code == 200
            resps.append(resp)
            if len(resps) > 5:
                break
        following: list[Username] = [
            following for resp in resps for following in extract_following(resp)
        ]
        assert len(following) > 200

    def test_dump_users_following(self):
        usernames = pd.Series(["nba"])
        tgt_file = Path("following.jsonl")
        dump_users_following(usernames, tgt_file)
        assert tgt_file.exists()
        tgt_file.unlink()

    # Additional test cases can be added here to cover more scenarios.


if __name__ == "__main__":
    unittest.main()
