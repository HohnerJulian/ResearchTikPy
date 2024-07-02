import unittest

import pandas as pd
from researchtikpy import get_videos_query
from .helpers import access_token


class TestGetVideosQuery(unittest.TestCase):
    def test_get_videos_query(self):
        df = get_videos_query(
            query={"and": [{"operation": "IN", "field_name": "hashtag_name", "field_values": ["germany"]}]},
            access_token=access_token(),
            start_date="20240101",
            end_date="20240102",
            total_max_count=10,
            max_count=10
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
    
    def test_invalid_query(self):
        # 'operation' EQ must have one field value
        invalid_query = {"and": [{"operation": "EQ", "field_name": "keyword", "field_values": ["one", "two"]}]}
        with self.assertRaises(ValueError):
            get_videos_query(
                query=invalid_query,
                access_token=access_token(),
                start_date="20240101",
                end_date="20240102",
                total_max_count=10,
                max_count=10
            )
