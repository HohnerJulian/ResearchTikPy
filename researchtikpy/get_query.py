#!/usr/bin/env python
# coding: utf-8

# In[23]:


from dataclasses import dataclass
import re
from typing import Iterator
import requests
import pandas as pd
import time
from datetime import datetime, timedelta


def get_videos_hashtag(hashtags, access_token, start_date, end_date, total_max_count, region_code=None, music_id=None, effect_id=None, max_count=100):
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
    query: dict = _create_query(hashtags, region_code, music_id, effect_id)
    return get_videos_query(
        query=query,
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        total_max_count=total_max_count,
        max_count=max_count,
    )


def _create_query(hashtags: list[str], region_code: str, music_id: str, effect_id: str) -> dict:
    and_conditions = [{"operation": "IN", "field_name": "hashtag_name", "field_values": hashtags}]
    if region_code:
        and_conditions.append({"operation": "EQ", "field_name": "region_code", "field_values": [region_code]})
    if music_id:
        and_conditions.append({"operation": "EQ", "field_name": "music_id", "field_values": [music_id]})
    if effect_id:
        and_conditions.append({"operation": "EQ", "field_name": "effect_id", "field_values": [effect_id]})
    query = {"and": and_conditions}
    return query


def get_videos_query(query: dict, access_token: str, start_date: str, end_date: str, total_max_count: int, max_count=100) -> pd.DataFrame:
    """
    Like get_videos_hashtag(), but you can pass a custom `query` object
    For the `query` parameter, see the TikTok API documentation: https://developers.tiktok.com/doc/research-api-specs-query-videos/
    For the rest of parameters, see get_videos_hashtag()
    """

    start_date_dt = datetime.strptime(start_date, "%Y%m%d")
    end_date_dt = datetime.strptime(end_date, "%Y%m%d")
    if start_date_dt > end_date_dt:
        raise ValueError("start_date must be before or equal end_date!")
    delta = timedelta(days=30)

    collected_videos = []

    while start_date_dt < end_date_dt:
        current_end_date = min(start_date_dt + delta, end_date_dt)

        query_body = {
            "query": query,
            "start_date": start_date_dt.strftime("%Y%m%d"),
            "end_date": current_end_date.strftime("%Y%m%d"),
            "max_count": max_count
        }

        for response in iter_responses(query_body, access_token):
            if_needed_log_failures_and_wait(response)
            if response.status_code == 200:
                videos: list[dict] = response.json()["data"]["videos"]
                print(f"Received {len(videos)} videos.")
                collected_videos.extend(videos)
            if len(collected_videos) >= total_max_count:
                break

        start_date_dt = current_end_date + timedelta(days=1)

    return pd.DataFrame(collected_videos[:total_max_count])


def post_query(full_query: dict, access_token: str) -> requests.Response:
    """The full query includes e.g. 'max_count', 'search_id' and 'cursor' fields."""
    assert isinstance(access_token, str), "access_token must be a string!"
    endpoint = "https://open.tiktokapis.com/v2/research/video/query/"
    fields = "id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text"
    url_with_fields = f"{endpoint}?fields={fields}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    print(f"Calling TikTok API with data={full_query}")
    return requests.post(url_with_fields, headers=headers, json=full_query)


def iter_responses(query_body: dict, access_token: str) -> Iterator[requests.Response]:
    """
    Creates an iterator that uses the cursor-based pagination to request all videos sequentially.
    If query_body['is_random'] is True, the iterator will not use cursor pagination.
    Each element yielded is an http response from the API.
    """
    search_id = query_body.get("search_id", None)
    cursor = query_body.get("cursor", 0)
    is_sequential = not bool(query_body.get("is_random", False))

    while True:
        full_query = query_body | dict(search_id=search_id, cursor=cursor)
        response = post_query(full_query=full_query, access_token=access_token)
        yield response
        if response.status_code == 200:
            data: dict = response.json()["data"]
            if is_sequential:
                if not data["has_more"]:
                    print("No more content to fetch. has_more=False")
                    return
                search_id = data["search_id"]
                cursor = data["cursor"]


def if_needed_log_failures_and_wait(response: requests.Response, secs: int = 10) -> None:
    if response.status_code == 200:
        return
    elif not has_json(response):
        raise new_api_response_error(response)
    elif is_uninformative_backend_failure(response):
        log_backend_failure_and_wait(response, secs=secs)
    elif search_id_was_not_found(response):
        print("The search_id is not found in the beginning, but is found after waiting some seconds.")
        log_backend_failure_and_wait(response, secs=secs)
    else:
        raise new_api_response_error(response)

def new_api_response_error(response):
    msg = f"API response error: status_code={response.status_code} body={response.text}"
    return ValueError(msg)


def log_backend_failure_and_wait(response, secs: int = 10) -> None:
    print(f"Backend failure: status_code={response.status_code} Response={response.json()}")
    print(f"Pausing {secs}s before retrying...")
    time.sleep(secs)


def is_uninformative_backend_failure(response) -> bool:
    error_msg: str = json_error_message(response)
    err_msgs = {
        "Something is wrong. Please try again later.",
        "Something went wrong. Please try again later.",
        "Server Internal Error",
        "Invalid count or cursor",
    }
    status_codes = {400, 500}
    return response.status_code in status_codes and error_msg in err_msgs


def json_error_message(response) -> str:
    return response.json()["error"]["message"]


def has_json(response: requests.Response) -> bool:
    try:
        response.json()
        return True
    except requests.JSONDecodeError:
        return False


def search_id_was_not_found(response) -> bool:
    pattern = r"Search Id \d+ is invalid or expired"
    match = re.match(pattern, json_error_message(response))
    return response.status_code == 400 and bool(match)
