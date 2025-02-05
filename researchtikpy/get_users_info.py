#!/usr/bin/env python
# coding: utf-8

# In[1]:
import requests
import pandas as pd


default_fields = "display_name,bio_description,avatar_url,is_verified,follower_count,following_count,likes_count,video_count"


def get_users_info(usernames, access_token, fields=default_fields, verbose=True):
    """
    Fetches user information for a list of usernames.

    Parameters:
    - usernames (list): List of TikTok usernames to fetch info for.
    - access_token (str): Access token for TikTok's API.
    - fields (str): Comma-separated string of user fields to retrieve. 
    - verbose (bool): If True, prints detailed logs; if False, suppresses most print statements.

    Returns:
    - pd.DataFrame: DataFrame containing user information.
    """
    users_data = []
    session = requests.Session()  # Use session for improved performance

    for username in usernames:
        response = fetch_user_info(session, username, access_token, fields)

        if verbose:
            print(f"Fetching info for user: {username}")

        if response.status_code == 200:
            user_data = response.json().get("data", {})
            if user_data:  # Check if data is not empty
                users_data.append(user_data)
            else:
                if verbose:
                    print(f"No data found for user: {username}")
        else:
            if verbose:
                print(f"Error for user {username}: {response.status_code}", response.json())
            users_data.append({"username": username, "error": "Failed to retrieve data"})

    users_df = pd.DataFrame(users_data)
    
    if verbose:
        print("User info retrieval complete.")
    
    return users_df


def fetch_user_info(
    session: requests.Session, username: str, access_token: str, fields: str
) -> requests.Response:
    query_body = {"username": username}
    params = {"fields": fields}
    endpoint = "https://open.tiktokapis.com/v2/research/user/info/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    return session.post(endpoint, headers=headers, json=query_body, params=params)


default_fields = "display_name,bio_description,avatar_url,is_verified,follower_count,following_count,likes_count,video_count"