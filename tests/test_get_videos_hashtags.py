import unittest
import pandas as pd
from researchtikpy import get_videos_hashtag
from .helpers import access_token


class TestGetVideoHashtag(unittest.TestCase):
    def test_get_videos_hashtag(self):
        token: str = access_token()
        df = get_videos_hashtag(
            hashtags=["germany"],
            access_token=token,
            start_date="20240101",
            end_date="20240102",
            total_max_count=5,
            max_count=30
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
