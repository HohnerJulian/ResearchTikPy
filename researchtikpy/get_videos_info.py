#!/usr/bin/env python
# coding: utf-8

# In[20]:


from datetime import datetime, timedelta
import requests
import pandas as pd
import time

def get_videos_info(usernames, access_token, start_date, end_date, max_count=100, verbose=True):
    """
    Fetches video information for given usernames within the specified date range.
    
    Parameters:
    - usernames: List of usernames to fetch videos for.
    - access_token: Authorization token for TikTok Research API.
    - start_date: Start date for the video search (format YYYYMMDD).
    - end_date: End date for the video search (format YYYYMMDD).
    - max_count: Maximum number of videos to return per request (default is 100).
    - verbose: If True, prints detailed logs; if False, suppresses most print statements.

    Returns:
    - DataFrame containing the video information.
    """
    fields = "id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text"
    query_fields = fields.split(',')
    
    endpoint = "https://open.tiktokapis.com/v2/research/video/query/"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    start_date_dt = datetime.strptime(start_date, "%Y%m%d")
    end_date_dt = datetime.strptime(end_date, "%Y%m%d")
    delta = timedelta(days=30)
    session = requests.Session()

    videos_df = pd.DataFrame(columns=query_fields)

    for username in usernames:
        current_start_date = start_date_dt
        while current_start_date <= end_date_dt:
            current_end_date = min(current_start_date + delta, end_date_dt)
            query_body = {
                "query": {
                    "and": [{"operation": "EQ", "field_name": "username", "field_values": [username]}]
                },
                "start_date": current_start_date.strftime("%Y%m%d"),
                "end_date": current_end_date.strftime("%Y%m%d"),
                "max_count": max_count
            }

            if verbose:
                print(f"Querying videos for {username} from {current_start_date.strftime('%Y%m%d')} to {current_end_date.strftime('%Y%m%d')}")
            response = session.post(f"{endpoint}?fields={','.join(query_fields)}", headers=headers, json=query_body)
            if verbose:
                print(f"Response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json().get("data", {})
                videos = data.get("videos", [])
                if verbose:
                    print(f"Found {len(videos)} videos for {username}")
                videos_df = pd.concat([videos_df, pd.DataFrame(videos)], ignore_index=True)
            else:
                if verbose:
                    print(f"Error fetching videos for user {username}: {response.status_code} - {response.text}")
            current_start_date += delta + timedelta(days=1)
    
    return videos_df

