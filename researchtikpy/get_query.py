import re
import time
from datetime import datetime
from logging import getLogger
from typing import Iterator

import pandas as pd
import requests

from researchtikpy.query_lang import Query, Condition, Operators, Fields, as_dict

logger = getLogger(__name__)


def get_videos_hashtag(
    hashtags,
    access_token,
    start_date,
    end_date,
    total_max_count,
    region_code=None,
    music_id=None,
    effect_id=None,
    max_count=100,
):
    """
    Searches for videos by hashtag with optional filters for region code, music ID,
    or effect ID, and includes rate limit handling. All available fields are
    retrieved by default, queries are segmented if the range between
    start_date and end_date exceeds 30 days.

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
    query: dict = _create_hashtag_query_(hashtags, region_code, music_id, effect_id)
    return get_videos_query(
        query=query,
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        total_max_count=total_max_count,
        max_count=max_count,
    )


def get_videos_info(
    usernames,
    access_token,
    start_date,
    end_date,
    max_count=100,
    verbose=False,
):
    """Get videos for a list of usernames."""
    query = Query(
        or_=[
            Condition(Fields.username, Operators.equals, [username])
            for username in usernames
        ]
    )
    return get_videos_query(
        query=query,
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        max_count=max_count,
    )


def _create_hashtag_query_(
    hashtags: list[str], region_code: str, music_id: str, effect_id: str
) -> dict:
    and_conditions = [Condition(Fields.hashtag_name, Operators.isin, hashtags)]
    if region_code:
        and_conditions.append(
            Condition(Fields.region_code, Operators.equals, [region_code])
        )
    if music_id:
        and_conditions.append(Condition(Fields.music_id, Operators.equals, [music_id]))
    if effect_id:
        and_conditions.append(
            Condition(Fields.effect_id, Operators.equals, [effect_id])
        )
    return Query(and_=and_conditions)


def get_videos_query(
    query: Query,
    access_token: str,
    start_date: str,
    end_date: str,
    total_max_count: int,
    max_count=100,
) -> pd.DataFrame:
    """Post a query to the TikTok API. For the `query` parameter, see the
    TikTok API documentation:
    https://developers.tiktok.com/doc/research-api-specs-query-videos/

    Parameters:
    - query: The query to post to the API.
    - access_token: Your valid access token for the TikTok Research API.
    - start_date: The start date for the search (format YYYYMMDD).
    - end_date: The end date for the search (format YYYYMMDD).
    - total_max_count: The total maximum number of videos to collect.
    - max_count: The maximum number of videos to return per request (up to 100).

    Returns:
    - A DataFrame containing the videos that match the given criteria.

    Example:
    ```
    query = Query(
        or_=[
            Condition(Fields.username, Operators.equals, ["username1", "username2"])
        ]
    )
    access_token = AccessToken("your_client_key", "your_client_secret")
    start_date = "20220101"
    end_date = "20220131"
    total_max_count = 1000
    data = get_videos_query(query, access_token, start_date, end_date, total_max_count)
    ```
    """

    start_date_dt = datetime.strptime(start_date, "%Y%m%d")
    end_date_dt = datetime.strptime(end_date, "%Y%m%d")

    if start_date_dt > end_date_dt:
        raise ValueError("start_date must be before or equal end_date!")

    collected_videos = []

    query_body = {
        "query": as_dict(query),
        "start_date": start_date_dt.strftime("%Y%m%d"),
        "end_date": end_date_dt.strftime("%Y%m%d"),
        "max_count": max_count,
    }

    logger.info(f"Querying TikTok API with query={query_body}")

    for response in iter_responses(query_body, access_token):
        if_needed_log_failures_and_wait(response)

        if response.status_code == 200:
            videos: list[dict] = response.json()["data"]["videos"]

            logger.info(f"Received {len(videos)} videos.")

            collected_videos.extend(videos)

        if len(collected_videos) >= total_max_count:
            break

    return pd.DataFrame(collected_videos[:total_max_count])


def post_query(full_query: dict, access_token: str) -> requests.Response:
    """The full query includes e.g. 'max_count', 'search_id' and 'cursor' fields."""
    assert isinstance(access_token, str), "access_token must be a string!"

    endpoint = "https://open.tiktokapis.com/v2/research/video/query/"
    fields = "id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text"
    url_with_fields = f"{endpoint}?fields={fields}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    logger.debug(f"Calling TikTok API with url={url_with_fields} data={full_query}")
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
                    logger.info("No more content to fetch. has_more=False")
                    return
                search_id = data["search_id"]
                cursor = data["cursor"]


def if_needed_log_failures_and_wait(
    response: requests.Response, secs: int = 10
) -> None:
    if response.status_code == 200:
        return
    elif not has_json(response):
        raise new_api_response_error(response)
    elif rate_limit_exceeded(response):
        log_rate_limit_hit_and_wait(response)
    elif is_uninformative_backend_failure(response):
        log_backend_failure_and_wait(response, secs=secs)
    elif search_id_was_not_found(response):
        logger.warning(
            "The search_id is not found in the beginning, but is found after waiting some seconds."
        )
        log_backend_failure_and_wait(response, secs=secs)
    else:
        raise new_api_response_error(response)


def rate_limit_exceeded(response) -> bool:
    """This is different from the daily quota limit."""
    return (
        response.status_code == 429
        and response.json()["error"]["code"] == "rate_limit_exceeded"
    )


def log_rate_limit_hit_and_wait(response) -> None:
    logger.warning(
        f"Rate limit hit: status_code={response.status_code} Response={response.json()}\n"
        f"Pausing 10s before continuing..."
    )
    time.sleep(10)


def new_api_response_error(response):
    msg = f"API response error: status_code={response.status_code} body={response.text}"
    return ValueError(msg)


def log_backend_failure_and_wait(response, secs: int = 10) -> None:
    logger.warning(
        f"Backend failure: status_code={response.status_code} Response={response.json()}\n"
        f"Pausing {secs}s before retrying..."
    )
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
