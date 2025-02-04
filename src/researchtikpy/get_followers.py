#!/usr/bin/env python
# coding: utf-8

# In[8]:




# Note: you might encounter a varying number of followers fetched per request. 
# This is due to how TikTok's API handles pagination and possibly how it limits data per request.
# As you approach the total limit of followers you want to fetch (total_count),
# the API might return fewer followers per request,
# especially if the remaining number to reach the total is less than your specified max_count.
# This is normal behavior for APIs when handling paginated results close to the limit of a dataset.
# It however unecessarily uses your daily quota faster than it should. Have to optimize that in the future. 
from logging import getLogger
import datetime
from typing import Iterator, TypedDict
import requests
import pandas as pd
from time import sleep


logger = getLogger(__name__)


def get_followers(usernames_list, access_token, max_count=100, total_count=None, verbose=True):
    """
    Fetches followers for multiple users and compiles them into a single DataFrame. It is advised to keep the list of 
    usernames short to avoid longer runtimes.

    Parameters:
    - usernames_list (list): List of usernames to fetch followers for.
    - access_token (str): Access token for TikTok's API.
    - max_count (int): Maximum number of followers to retrieve per request (default 100).
    - total_count (int): Maximum total number of followers to retrieve per user.
    - verbose (bool): If True, prints detailed logs; if False, suppresses most print statements.

    Returns:
    - pd.DataFrame: DataFrame containing all followers from the provided usernames.
    """
    all_followers_df = pd.DataFrame()
    session = requests.Session()  # Use session for improved performance

    for username in usernames_list:
        followers_list = []
        cursor = 0  # Initialize cursor for pagination
        has_more = True
        retrieved_count = 0  # Track the count of retrieved followers
        effective_max_count = max_count  # Reset max_count for each user

        while has_more and (total_count is None or retrieved_count < total_count):
            # Adjust max_count based on remaining followers needed
            if total_count is not None:
                effective_max_count = min(max_count, total_count - retrieved_count)

            response = get_user_followers(access_token, session, username, cursor, effective_max_count)
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                followers = data.get("user_followers", [])
                followers_list.extend(followers)
                retrieved_count += len(followers)
                has_more = data.get("has_more", False)
                cursor = data.get("cursor", cursor + effective_max_count)  # Update cursor based on response
                if verbose:
                    print(f"Retrieved {len(followers)} followers for user {username} (total retrieved: {retrieved_count})")
            elif response.status_code == 429:
                if verbose:
                    print(f"Rate limit exceeded fetching followers for user {username}. Pausing before retrying...")
                sleep(60)  # Adjust sleep time based on the API's rate limit reset window
                continue  # Continue to the next iteration without breaking the loop
            else:
                if verbose:
                    print(f"Error fetching followers for user {username}: {response.status_code}", response.json())
                break  # Stop the loop for the current user

        if followers_list:
            followers_df = pd.DataFrame(followers_list)
            followers_df['target_account'] = username  # Identify the account these followers belong to
            all_followers_df = pd.concat([all_followers_df, followers_df], ignore_index=True)

    return all_followers_df


def get_user_followers(
    access_token: str,
    session: requests.Session,
    username: str,
    cursor: int = 0,
    max_count: int = 100,
) -> requests.Response:
    date_str = to_date_str(cursor)
    logger.info(f"Calling get followers endpoint for username='{username}', cursor={cursor} (equivalent to '{date_str}'), max_count={max_count}")
    endpoint = "https://open.tiktokapis.com/v2/research/user/followers/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    query_body = {"username": username, "max_count": max_count, "cursor": cursor}
    return session.post(endpoint, headers=headers, json=query_body)


def to_date_str(x: int) -> str:
    return datetime.datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S")


class Username(TypedDict):
    display_name: str
    username: str


def extract_followers(response: requests.Response) -> list[Username]:
    return response.json()["data"]["user_followers"]


def iter_followers_responses(access_token: str, username: str) -> Iterator[requests.Response]:
    """
    Creates an iterator that uses the cursor-based pagination to request all followers sequentially.
    Each element yielded is an http response from the API.
    """
    session = requests.Session()
    cursor = 0
    max_count = 100
    while True:
        response = get_user_followers(
            access_token=access_token,
            session=session,
            username=username,
            cursor=cursor,
            max_count=max_count,
        )
        yield response
        if response.status_code == 200:
            data: dict = response.json()["data"]
            if not data["has_more"]:
                print("No more content to fetch. has_more=False")
                return
            cursor = data["cursor"]