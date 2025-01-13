# Example from Docs
# curl --location 'https://open.tiktokapis.com/v2/research/tts/shop/' \
# --header 'Content-Type: application/json' \
# --header 'Authorization: Bearer clt.2.Hl4lozkBGnBSz0VkTWTscSJDOC55TlPmvA4v2hoaEnRPqF1wHCZzspacy9q2YIqyglTFG6h4k3Ux2oljH-fc8g*3' \
# --data '{
#     "shop_name": "Free Soul",
#     "fields":"shop_name,shop_rating,shop_review_count,item_sold_count,shop_id,shop_performance_value",
#     "limit": 10
# }'

import requests


def get_shop_info(shop_name: str, access_token: str) -> requests.Response:
    fields = "shop_name,shop_rating,shop_review_count,item_sold_count,shop_id,shop_performance_value"
    response = requests.post(
        "https://open.tiktokapis.com/v2/research/tts/shop/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"shop_name": shop_name, "fields": fields, "limit": 10},
    )
    return response
