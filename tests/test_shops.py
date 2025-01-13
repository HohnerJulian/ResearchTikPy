import unittest

from researchtikpy.shops import get_shop_info
from tests.helpers import access_token


class TestShops(unittest.TestCase):
    def test_get_shop_info(self):
        response = get_shop_info(shop_name="Free Soul", access_token=access_token())
        self.assertEqual(response.status_code, 200)
