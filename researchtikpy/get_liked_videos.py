#!/usr/bin/env python
# coding: utf-8

# In[4]:


import requests
import pandas as pd
from time import sleep

def get_liked_videos(usernames, access_token, fields="id,video_description,create_time,username,like_count,comment_count,share_count,view_count,hashtag_names", max_count=100, verbose=True):
    """
    Fetches liked videos for multiple usernames and compiles them into a single DataFrame.
    
    Parameters:
    - usernames (list): List of usernames to fetch liked videos for.
    - access_token (str): Access token for TikTok's API.
    - fields (str): Comma-separated string of fields to retrieve for each liked video.
    - max_count (int): Maximum number of liked videos to retrieve per request (default 100).
    - verbose (bool): If True, prints detailed logs; if False, suppresses most print statements.
    
    Returns:
    - pd.DataFrame: DataFrame containing all liked videos from the provided usernames.
    """
    endpoint = "https://open.tiktokapis.com/v2/research/user/liked_videos/"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    liked_videos_df = pd.DataFrame()
    session = requests.Session()  # Use session for improved performance

    for username in usernames:
        has_more = True
        cursor = 0  # Start with initial cursor at 0

        while has_more:
            query_body = {"username": username, "max_count": max_count, "cursor": cursor}
            response = session.post(f"{endpoint}?fields={fields}", headers=headers, json=query_body)
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                user_liked_videos = data.get("user_liked_videos", [])
                
                if user_liked_videos:
                    current_df = pd.DataFrame(user_liked_videos)
                    liked_videos_df = pd.concat([liked_videos_df, current_df], ignore_index=True)
                    if verbose:
                        print(f"Successfully fetched {len(user_liked_videos)} liked videos for user {username}")
                else:
                    if verbose:
                        print(f"No liked videos found for user {username}")
                
                has_more = data.get("has_more", False)
                cursor = data.get("cursor", cursor + max_count)  # Use API provided cursor if available, else increment
            elif response.status_code == 403:
                if verbose:
                    print(f"Access denied: User {username} has not enabled collecting liked videos.")
                break  # Exit the loop for the current username if access is denied
            elif response.status_code == 429:
                if verbose:
                    print("Rate limit exceeded. Pausing before retrying...")
                sleep(60)  # Pause execution before retrying
                continue  # Optional: retry the last request
            else:
                if verbose:
                    print(f"Error fetching liked videos for user {username}: {response.status_code}", response.json())
                break  # Stop fetching for current user in case of an error

    return liked_videos_df

