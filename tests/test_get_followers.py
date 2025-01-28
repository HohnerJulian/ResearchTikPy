import unittest

import requests

from researchtikpy.get_followers import extract_followers, get_user_followers
from tests.helpers import access_token


class TestGetFollowers(unittest.TestCase):
    def test_get_users_info(self):
        response: requests.Response = get_user_followers(
            access_token=access_token(),
            session=requests.Session(),
            username="realdonaldtrump",
        )
        assert response.status_code == 200
        n_followers = len(extract_followers(response))
        assert n_followers > 80, n_followers
