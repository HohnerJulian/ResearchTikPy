import unittest

import requests

from researchtikpy.get_followers import (
    Username,
    extract_followers,
    get_user_followers,
    iter_followers_responses,
)
from tests.helpers import access_token


class TestGetFollowers(unittest.TestCase):
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
