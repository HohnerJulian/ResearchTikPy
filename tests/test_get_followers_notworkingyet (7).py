#!/usr/bin/env python
# coding: utf-8

# In[23]:


import requests
import pandas as pd
import time
from datetime import datetime, timedelta

def get_videos_hashtag(hashtags, access_token, start_date, end_date, total_max_count, region_code=None, music_id=None, effect_id=None, max_count=100, rate_limit_pause=60):
    """
    Searches for videos by hashtag with optional filters for region code, music ID, or effect ID, and includes rate limit handling. All available fields are retrieved by default, queries are segmented if the range between start_date and end_date exceeds 30 days.

    Parameters:
    - hashtags: A list of hashtags to search for.
    - access_token: Your valid access token for the TikTok Research API.
    - start_date: The start date for the search (format YYYYMMDD).
    - end_date: The end date for the search (format YYYYMMDD).
    - total_max_count: The total maximum number of videos to collect. 
    - region_code: Optional; the region code to filter videos by.
    - music_id: Optional; the music ID to filter videos by.
    - effect_id: Optional; the effect ID to filter videos by.
    - max_count: The maximum number of videos to return per request (up to 100).
    - rate_limit_pause: Time in seconds to wait when a rate limit error is encountered.

    Returns:
    - A DataFrame containing the videos that match the given criteria.
    """
    fields = "id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text"

    endpoint = "https://open.tiktokapis.com/v2/research/video/query/"
    url_with_fields = f"{endpoint}?fields={fields}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    start_date_dt = datetime.strptime(start_date, "%Y%m%d")
    end_date_dt = datetime.strptime(end_date, "%Y%m%d")
    delta = timedelta(days=30)

    collected_videos = []

    while start_date_dt < end_date_dt:
        current_end_date = min(start_date_dt + delta, end_date_dt)
        and_conditions = [{"operation": "IN", "field_name": "hashtag_name", "field_values": hashtags}]
        if region_code:
            and_conditions.append({"operation": "EQ", "field_name": "region_code", "field_values": [region_code]})
        if music_id:
            and_conditions.append({"operation": "EQ", "field_name": "music_id", "field_values": [music_id]})
        if effect_id:
            and_conditions.append({"operation": "EQ", "field_name": "effect_id", "field_values": [effect_id]})

        query_body = {
            "query": {"and": and_conditions},
            "start_date": start_date_dt.strftime("%Y%m%d"),
            "end_date": current_end_date.strftime("%Y%m%d"),
            "max_count": max_count
        }

        response = requests.post(url_with_fields, headers=headers, json=query_body)
        if response.status_code == 200:
            data = response.json().get("data", {})
            videos = data.get("videos", [])
            collected_videos.extend(videos)
            if not data.get("has_more", False) or len(collected_videos) >= total_max_count:
                break
        elif response.status_code == 429:
            print("Rate limit exceeded. Pausing before retrying...")
            time.sleep(rate_limit_pause)
        else:
            print(f"Error: {response.status_code}", response.json())
            break

        start_date_dt = current_end_date + timedelta(days=1)

    return pd.DataFrame(collected_videos[:total_max_count])

