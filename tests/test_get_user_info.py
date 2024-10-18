import unittest
from researchtikpy import get_users_info
from .helpers import access_token


class TestGetAccessToken(unittest.TestCase):
    def test_get_users_info(self):
        df = get_users_info(
            usernames=["ciedygrace", "pcos.pains"],
            access_token=access_token(),
        )
        assert len(df) == 2
