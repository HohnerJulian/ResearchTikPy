import unittest

from researchtikpy.shops import get_product_info, get_product_reviews, get_shop_info
from tests.helpers import access_token


class TestShops(unittest.TestCase):
    def test_get_shop_info(self):
        # https://www.tiktok.com/@sosucosmetics
        shop = "SOSU Cosmetics"
        response = get_shop_info(shop_name=shop, access_token=access_token())
        self.assertEqual(response.status_code, 200)

    def test_get_product_info(self):
        # This is a product of https://www.tiktok.com/@sosucosmetics (test above)
        shop_id = "7495831119779957057"
        response = get_product_info(shop_id=shop_id, access_token=access_token())
        self.assertEqual(response.status_code, 200)

    @unittest.skip("Skipping this test until the API is updated")
    def test_get_product_reviews(self):
        product_id = "1729441062054432065"
        response = get_product_reviews(
            product_id=product_id, access_token=access_token()
        )
        self.assertEqual(response.status_code, 200)
