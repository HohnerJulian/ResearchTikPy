import os
import unittest

import pandas as pd
from researchtikpy import get_videos_hashtag, get_access_token

class TestGetVideoHashtag(unittest.TestCase):
    def test_get_videos_hashtag(self):
        token: str = access_token()
        df = get_videos_hashtag(
            hashtags=["germany"],
            access_token=token,
            start_date="20240101",
            end_date="20240102",
            total_max_count=10
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


def access_token() -> str:
    data: dict = get_access_token(
        client_key=os.environ["TIKTOK_CLIENT_KEY"],
        client_secret=os.environ["TIKTOK_CLIENT_SECRET"],
    )
    return data["access_token"]
