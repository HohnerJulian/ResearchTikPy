#!/usr/bin/env python
# coding: utf-8

# In[5]:


import requests
import pandas as pd

def get_pinned_videos(usernames, access_token, fields="id,video_description,create_time,username,like_count,comment_count,share_count,view_count,hashtag_names", verbose=True):
    """
    Fetches pinned videos for multiple usernames and compiles them into a single DataFrame.
    - usernames (list): List of usernames to fetch pinned videos for.
    - access_token (str): Access token for TikTok's API.
    - fields (str): Comma-separated string of fields to retrieve for each pinned video.
    - verbose (bool): If True, print additional logging information.
    Returns:
    - pd.DataFrame: DataFrame containing all pinned videos from the provided usernames.
    """
    endpoint = "https://open.tiktokapis.com/v2/research/user/pinned_videos/"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    pinned_videos_df = pd.DataFrame()
    session = requests.Session()  # Use session for improved performance

    for username in usernames:
        query_body = {"username": username}
        response = session.post(f"{endpoint}?fields={fields}", headers=headers, json=query_body)
        
        if response.status_code == 200:
            data = response.json().get("data", {})
            pinned_videos = data.get("pinned_videos_list", [])
            
            if pinned_videos:
                temp_df = pd.DataFrame(pinned_videos)
                temp_df['username'] = username  # Include username for clarity
                pinned_videos_df = pd.concat([pinned_videos_df, temp_df], ignore_index=True)
                if verbose:
                    print(f"Successfully fetched {len(pinned_videos)} pinned videos for user {username}")
            else:
                if verbose:
                    print(f"No pinned videos found for user {username}")
        else:
            if verbose:
                print(f"Error fetching pinned videos for user {username}: {response.status_code}")
                try:
                    print(response.json())
                except ValueError:  # handles the JSONDecodeError for non-JSON responses
                    print("No valid JSON response available.")

    return pinned_videos_df

