#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests

def get_access_token(client_key, client_secret):
    """
    Requests an access token from the TikTok API using client credentials.

    Parameters:
    - client_key (str): The client key provided by TikTok.
    - client_secret (str): The client secret provided by TikTok.

    Returns:
    - dict: A dictionary containing the access token, its expiry duration, and the token type.

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

