from pathlib import Path
import unittest

import pandas as pd
import requests

from researchtikpy.get_followers import Username
from researchtikpy.get_following import (
    dump_users_following,
    extract_following,
    get_user_following,
    iter_following_responses,
)
from tests.helpers import access_token


class TestGetFollowing(unittest.TestCase):
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
        tgt_csv = Path("following.csv")
        dump_users_following(usernames, tgt_csv)
        assert tgt_csv.exists()
        tgt_csv.unlink()
