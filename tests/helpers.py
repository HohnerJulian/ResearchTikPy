from functools import cache
from researchtikpy import get_access_token


import os


@cache
def access_token() -> str:
    data: dict = get_access_token(
        client_key=os.environ["TIKTOK_CLIENT_KEY"],
        client_secret=os.environ["TIKTOK_CLIENT_SECRET"],
    )
    return data["access_token"]