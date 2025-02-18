from researchtikpy.utils import AccessToken


import os
import requests
from cachetools.func import ttl_cache
from logging import getLogger


logger = getLogger(__name__)


def get_access_token(client_key, client_secret):
    """
    Requests an access token from the TikTok API using client credentials.

    Parameters:
    - client_key (str): The client key provided by TikTok.
    - client_secret (str): The client secret provided by TikTok.

    Returns:
    - AccessToken: The access token, with its expiry duration, and the token type set.


    Raises:
    - Exception: If the request to the TikTok API fails or is not successful.
    """
    endpoint_url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'client_key': client_key,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }

    response = requests.post(endpoint_url, headers=headers, data=data)

    if response.status_code == 200:
        response_json = response.json()
        return {
            "access_token": response_json['access_token'],
            "expires_in": response_json['expires_in'],
            "token_type": response_json['token_type']
        }
    else:
        raise Exception(f"Failed to obtain access token: {response.text}")


@ttl_cache(ttl=7200 - 1)  # to be safe
def get_access_token_cached() -> str:
    client_key = os.environ["TIKTOK_CLIENT_KEY"]
    client_secret = os.environ["TIKTOK_CLIENT_SECRET"]
    logger.info("Getting access token...")
    data: dict = get_access_token(
        client_key=client_key, client_secret=client_secret
    )
    return data["access_token"]
