#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
from time import sleep

def get_video_comments(videos_df, access_token, fields="id,video_id,text,like_count,reply_count, create_time, parent_comment_id", max_count=100, verbose=True):
    """
    Fetches comments for multiple videos and compiles them into a single DataFrame.

    Parameters:
    - videos_df (pd.DataFrame): DataFrame with a column 'id' containing video IDs.
    - access_token (str): Access token for TikTok's API.
    - fields (str): Comma-separated string of fields to retrieve for each comment. Defaults to a basic set of fields.
    - max_count (int): Maximum number of comments to retrieve per request (default is 100).
    - verbose (bool): If True (default), prints detailed logs; if False, suppresses most print statements.

    Returns:
    - pd.DataFrame: DataFrame containing all comments from the provided videos.
    """
    endpoint = "https://open.tiktokapis.com/v2/research/video/comment/list/"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    all_comments_df = pd.DataFrame()
    session = requests.Session()  # Use session for improved performance

    for _, video in videos_df.iterrows():
        video_id = video['id']
        has_more = True
        cursor = 0

        while has_more and cursor < 1000:  # To respect the API's limit
            body_params = {"video_id": video_id, "max_count": max_count, "cursor": cursor}
            response = session.post(f"{endpoint}?fields={fields}", headers=headers, json=body_params)
            
            if verbose:
                print(f"Fetching comments for video {video_id} with cursor at {cursor}")
                
            if response.status_code == 200:
                data = response.json().get("data", {})
                comments = data.get("comments", [])
                
                if comments:
                    comments_df = pd.DataFrame(comments)
                    comments_df['video_id'] = video_id  # Add the video_id to each comment
                    all_comments_df = pd.concat([all_comments_df, comments_df], ignore_index=True)
                
                has_more = data.get("has_more", False)
                cursor += max_count  # Increment cursor based on max_count
            elif response.status_code == 429:
                if verbose:
                    print("Rate limit exceeded. Pausing before retrying...")
                sleep(30)  # Pause execution before retrying
            else:
                if verbose:
                    print(f"Error fetching comments for video {video_id}: {response.status_code}", response.json())
                break  # Stop the loop in case of an error

    return all_comments_df

