#!/usr/bin/env python
# coding: utf-8

# In[5]:


from typing import Iterator
import requests
import pandas as pd
from time import sleep

from .get_followers import Username, to_date_str

def get_following(usernames_list, access_token, max_count=100, verbose=True):
    """
    Fetches accounts that a user follows. Each username in the list is used to fetch accounts they follow.

    Parameters:
    - usernames_list (list): List of usernames to fetch followed accounts for.
    - access_token (str): Access token for TikTok's API.
    - max_count (int): Maximum number of followed accounts to retrieve per request (default 100).
    - verbose (bool): If True, prints detailed logs; if False, suppresses most print statements.

    Returns:
    - pd.DataFrame: DataFrame containing all followed accounts from the provided usernames.
    """
    all_following_df = pd.DataFrame()
    session = requests.Session()  # Use session for improved performance

    for username in usernames_list:
        following_list = []
        cursor = 0  # Initialize cursor for pagination
        has_more = True

        while has_more:
            endpoint = "https://open.tiktokapis.com/v2/research/user/following/"
            headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
            query_body = {"username": username, "max_count": max_count, "cursor": cursor}

            response = session.post(endpoint, headers=headers, json=query_body)

            if response.status_code == 200:
                data = response.json().get("data", {})
                following = data.get("user_following", [])
                following_list.extend(following)
                has_more = data.get("has_more", False)
                cursor = data.get("cursor", cursor + max_count)  # Update cursor based on response
                if verbose:
                    print(f"Retrieved {len(following)} accounts for user {username}")
            elif response.status_code == 429:
                if verbose:
                    print(f"Rate limit exceeded fetching following for user {username}. Pausing before retrying...")
                sleep(60)  # Adjust sleep time based on the API's rate limit reset window
                continue  # Continue to the next iteration without breaking the loop
            else:
                if verbose:
                    print(f"Error fetching following for user {username}: {response.status_code}", response.json())
                break  # Stop the loop for the current user

        if following_list:
            following_df = pd.DataFrame(following_list)
            following_df['target_account'] = username  # Identify the account these followings belong to
            all_following_df = pd.concat([all_following_df, following_df], ignore_index=True)

    return all_following_df


def get_user_following(
    access_token: str, session: requests.Session, username: str, cursor: int = 0
) -> requests.Response:
    max_count = 100
    date_str = to_date_str(cursor)
    print(
        f"Calling get following endpoint for username='{username}', cursor={cursor} (equivalent to '{date_str}'), max_count={max_count}"
    )
    endpoint = "https://open.tiktokapis.com/v2/research/user/following/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    query_body = {"username": username, "max_count": max_count, "cursor": cursor}
    return session.post(endpoint, headers=headers, json=query_body)


def extract_following(response: requests.Response) -> list[Username]:
    return response.json()["data"]["user_following"]


def iter_following_responses(
    access_token: str, username: str
) -> Iterator[requests.Response]:
    session = requests.Session()
    cursor = 0
    while True:
        response = get_user_following(access_token, session, username, cursor)
        yield response
        if response.status_code == 200:
            data: dict = response.json()["data"]
            if not data["has_more"]:
                print("No more content to fetch. has_more=False")
                return
            cursor = data["cursor"]
