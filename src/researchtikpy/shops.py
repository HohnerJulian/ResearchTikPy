# Example from Docs
# curl --location 'https://open.tiktokapis.com/v2/research/tts/shop/' \
# --header 'Content-Type: application/json' \
# --header 'Authorization: Bearer <token>' \
# --data '{
#     "shop_name": "Free Soul",
#     "fields":"shop_name,shop_rating,shop_review_count,item_sold_count,shop_id,shop_performance_value",
#     "limit": 10
# }'

import requests

from researchtikpy.utils import AccessToken


def get_shop_info(shop_name: str, access_token: AccessToken) -> requests.Response:
    fields = "shop_name,shop_rating,shop_review_count,item_sold_count,shop_id,shop_performance_value"
    response = requests.post(
        "https://open.tiktokapis.com/v2/research/tts/shop/",
        headers={"Authorization": access_token.token},
        json={"shop_name": shop_name, "fields": fields, "limit": 10},
    )
    return response


# curl --location 'https://open.tiktokapis.com/v2/research/tts/product/' \
# --header 'Content-Type: application/json' \
# --header 'Authorization: Bearer <token>' \
# --data '{
#     "shop_id": 7495177166735509999,
#     "fields": "product_id,product_sold_count,product_description,product_price,product_review_count,product_name,product_rating_1_count,product_rating_2_count,product_rating_3_count,product_rating_4_count,product_rating_5_count",
#     "page_start": 1,
#     "page_size": 2
# }'


def get_product_info(shop_id: str, access_token: AccessToken) -> requests.Response:
    fields = "product_id,product_sold_count,product_description,product_price,product_review_count,product_name,product_rating_1_count,product_rating_2_count,product_rating_3_count,product_rating_4_count,product_rating_5_count"
    response = requests.post(
        "https://open.tiktokapis.com/v2/research/tts/product/",
        headers={"Authorization": access_token.token},
        json={"shop_id": shop_id, "fields": fields, "page_start": 1, "page_size": 10},
    )
    return response


# curl --location 'https://open.tiktokapis.com/v2/research/tts/review/' \
# --header 'Authorization: Bearer <token>' \
# --header 'Content-Type: application/json' \
# --data '{
#     "product_id": 1729401755128991215,
#     "fields": "product_name,review_text,display_name,review_like_count,create_time,review_rating",
#     "page_start": 2,
#     "page_size": 1
# }'


def get_product_reviews(product_id: str, access_token: AccessToken) -> requests.Response:
    """
    As of 2025-01-13, the documentation showed conflicting descriptions: https://developers.tiktok.com/doc/research-api-specs-query-tiktok-shop-reviews?enter_method=left_navigation
    Its unclear if one has to pass shop_id or product_id.
    """
    fields = "product_name"  # ,review_text,display_name,review_like_count,create_time,review_rating"

    response = requests.post(
        "https://open.tiktokapis.com/v2/research/tts/review/",
        headers={"Authorization": access_token.token},
        json={
            "product_id": product_id,
            "fields": fields,
            "page_start": 1,
            "page_size": 10,
        },
    )
    return response
