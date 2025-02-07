"""ResearchTikPy's functions for collecting TikTok's social graph.

Note:
    You might encounter a varying number of followers fetched per request. 
    This is due to how TikTok's API handles pagination and possibly how it limits data per request.
    As you approach the total limit of followers you want to fetch (total_count),
    the API might return fewer followers per request,
    especially if the remaining number to reach the total is less than your specified max_count.
    This is normal behavior for APIs when handling paginated results close to the limit of a dataset.
    It however unecessarily uses your daily quota faster than it should. Have to optimize that in the future. 
"""

import datetime
from enum import StrEnum, auto
from logging import getLogger
from pathlib import Path
from time import sleep
from typing import Iterator, List, TypedDict

import pandas as pd
import requests
import tqdm

from . import endpoints
from .get_access_token import get_access_token_cached
from .get_query import has_json
from .rtk_utilities import append_df_to_file

logger = getLogger(__name__)


class Username(TypedDict):
    display_name: str
    username: str


class FollowDirection(StrEnum):
    FOLLOWER = auto()
    FOLLOWING = auto()


def get_followers(
    usernames_list, access_token, max_count=100, total_count=None, verbose=True
):
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

            response = get_user_followers(
                access_token, session, username, cursor, effective_max_count
            )

            if response.status_code == 200:
                data = response.json().get("data", {})
                followers = data.get("user_followers", [])
                followers_list.extend(followers)
                retrieved_count += len(followers)
                has_more = data.get("has_more", False)
                cursor = data.get(
                    "cursor", cursor + effective_max_count
                )  # Update cursor based on response
                if verbose:
                    print(
                        f"Retrieved {len(followers)} followers for user {username} (total retrieved: {retrieved_count})"
                    )
            elif response.status_code == 429:
                if verbose:
                    print(
                        f"Rate limit exceeded fetching followers for user {username}. Pausing before retrying..."
                    )
        if followers_list:
            followers_df = pd.DataFrame(followers_list)
            followers_df["target_account"] = (
                username  # Identify the account these followers belong to
            )
            all_followers_df = pd.concat(
                [all_followers_df, followers_df], ignore_index=True
            )

    return all_followers_df


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
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            query_body = {
                "username": username,
                "max_count": max_count,
                "cursor": cursor,
            }

            response = session.post(endpoint, headers=headers, json=query_body)

            if response.status_code == 200:
                data = response.json().get("data", {})
                following = data.get("user_following", [])
                following_list.extend(following)
                has_more = data.get("has_more", False)
                cursor = data.get(
                    "cursor", cursor + max_count
                )  # Update cursor based on response
                if verbose:
                    print(f"Retrieved {len(following)} accounts for user {username}")
            elif response.status_code == 429:
                if verbose:
                    print(
                        f"Rate limit exceeded fetching following for user {username}. Pausing before retrying..."
                    )
                sleep(
                    60
                )  # Adjust sleep time based on the API's rate limit reset window
                continue  # Continue to the next iteration without breaking the loop
            else:
                if verbose:
                    print(
                        f"Error fetching followers for user {username}: {response.status_code}",
                        response.json(),
                    )
                break  # Stop the loop for the current user

        if following_list:
            following_df = pd.DataFrame(following_list)
            following_df["target_account"] = (
                username  # Identify the account these followers belong to
            )
            all_following_df = pd.concat(
                [all_following_df, following_df], ignore_index=True
            )

    return all_following_df


def get_user_followers(
    access_token: str,
    session: requests.Session,
    username: str,
    cursor: int = 0,
    max_count: int = 100,
) -> requests.Response:
    """Fetches the accounts that follows an user.

    Equivalent to `get_user_response(FollowDirection.FOLLOWERS, ...)`.

    Params:
        access_token (str): The access token for the TikTok API.
        session (requests.Session): The session to use for the request.
        username (str): The username to fetch the social graph for.
        cursor (int): The cursor to use for pagination.
        max_count (int): The maximum number of accounts to fetch per request.
    """
    return get_user_response(
        FollowDirection.FOLLOWER,
        access_token=access_token,
        session=session,
        username=username,
        cursor=cursor,
        max_count=max_count,
    )


def get_user_following(
    access_token: str,
    session: requests.Session,
    username: str,
    cursor: int = 0,
    max_count: int = 100,
) -> requests.Response:
    """Fetches the accounts that follows an user.

    Equivalent to `get_user_response(FollowDirection.FOLLOWINGS, ...)`.

    Params:
        access_token (str): The access token for the TikTok API.
        session (requests.Session): The session to use for the request.
        username (str): The username to fetch the social graph for.
        cursor (int): The cursor to use for pagination.
        max_count (int): The maximum number of accounts to fetch per request.
    """
    return get_user_response(
        FollowDirection.FOLLOWING,
        access_token=access_token,
        session=session,
        username=username,
        cursor=cursor,
        max_count=max_count,
    )


def get_user_response(
    mode: FollowDirection,
    access_token: str,
    session: requests.Session,
    username: str,
    cursor: int = 0,
    max_count: int = 100,
) -> requests.Response:
    date_str = to_date_str(cursor)
    endpoint = (
        endpoints.followers
        if mode == FollowDirection.FOLLOWER
        else endpoints.followings
    )

    logger.info(
        f"Calling get_{ mode } endpoint for {username}, cursor={cursor} (equivalent to {date_str}), max_count={max_count}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    query_body = {"username": username, "max_count": max_count, "cursor": cursor}
    return session.post(endpoint, headers=headers, json=query_body)


def to_date_str(x: int) -> str:
    return datetime.datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S")


def extract_followers(response: requests.Response) -> list[Username]:
    return _extract_user_list(response, "user_followers")


def extract_following(response: requests.Response) -> list[Username]:
    return _extract_user_list(response, "user_following")


def _extract_user_list(reponse: requests.Response, key: str) -> List[Username]:
    return reponse.json().get("data", {}).get(key)


def iter_user_responses(
    mode: FollowDirection, access_token: str, username: str
) -> Iterator[requests.Response]:
    """Creates an iterator that uses the cursor-based pagination to request all followers sequentially.
    Each element yielded is an http response from the API.

    Params:
        mode (Literat["following", "follower"]): The direction of the social graph to fetch.
        access_token (str): The access token for the TikTok API.
        username (str): The username to fetch the social graph for.

    Returns:
        Iterator[requests.Response]: An iterator that yields http responses from the API.
    """
    session = requests.Session()
    cursor = 0
    max_count = 100
    while True:
        response = get_user_response(
            mode=mode,
            access_token=access_token,
            session=session,
            username=username,
            cursor=cursor,
            max_count=max_count,
        )

        yield response

        if is_response_ok(response):
            data: dict = response.json()["data"]
            if not data["has_more"]:
                logger.info("No more content to fetch. has_more=False")
                return
            cursor = data["cursor"]
        else:
            logger.info(
                "Problem in response. status_code=%d, error='%s'",
                response.status_code,
                response.text,
            )
            return


def iter_followers_responses(
    access_token: str, username: str
) -> Iterator[requests.Response]:
    """Creates an iterator that uses the cursor-based pagination to request all followers sequentially.
    Each element yielded is an http response from the API.

    Params:
        access_token (str): The access token for the TikTok API.
        username (str): The username to fetch the social graph for.

    Returns:
        Iterator[requests.Response]: An iterator that yields http responses from the API.
    """
    yield from iter_user_responses(
        mode=FollowDirection.FOLLOWER, access_token=access_token, username=username
    )


def iter_following_responses(
    access_token: str, username: str
) -> Iterator[requests.Response]:
    """Creates an iterator that uses the cursor-based pagination to request all followers sequentially.
    Each element yielded is an http response from the API.

    Params:
        access_token (str): The access token for the TikTok API.
        username (str): The username to fetch the social graph for.

    Returns:
        Iterator[requests.Response]: An iterator that yields http responses from the API.
    """
    yield from iter_user_responses(
        mode=FollowDirection.FOLLOWING, access_token=access_token, username=username
    )


def is_response_ok(response: requests.Response) -> bool:
    return (
        response.status_code == 200
        and has_json(response)
        and response.json()["error"]["code"] == "ok"
    )


def is_ok_but_empty(response: requests.Response, direction: FollowDirection) -> bool:
    key = f"user_{direction}s"
    is_ok: bool = is_response_ok(response)

    return is_ok and key not in response.json()["data"]


def construct_dataframe(
    mode: FollowDirection, response: requests.Response
) -> pd.DataFrame:
    ok = is_response_ok(response)
    data = {"status_code": response.status_code, "success": ok}

    if ok and not is_ok_but_empty(response, mode):
        data["error"] = ""
        user_connections: list[Username] = _extract_user_list(mode, response)
        fdf = pd.DataFrame(user_connections)
        new_colnames = {
            "username": f"{mode}_username",
            "display_name": f"{mode}_display_name",
        }
        fdf = fdf.rename(columns=new_colnames)
        df = fdf.assign(**data)

        return df
    data = {**data, "error": response.text, "username": None, "display_name": None}
    df = pd.DataFrame([data])

    return df


def dump_users_connections(
    mode: FollowDirection, usernames: pd.Series, tgt_jsonl: Path
):
    if tgt_jsonl.exists():
        done_usernames = pd.read_json(tgt_jsonl, lines=True)["username"].unique()

        logger.info(f"JSONL exists. Skipping {len(done_usernames)} usernames")

        usernames = usernames[~usernames.isin(done_usernames)]

    for username in tqdm.tqdm(usernames):
        for response in iter_user_responses(
            mode=mode, access_token=get_access_token_cached(), username=username
        ):
            df = construct_dataframe(mode, response)
            df = df.assign(username=username)
            append_df_to_file(df=df, path=tgt_jsonl, jsonl=True)


def dump_users_following(usernames: pd.Series, tgt_jsonl: Path):
    dump_users_connections(FollowDirection.FOLLOWING, usernames, tgt_jsonl)


def dump_users_follower(usernames: pd.Series, tgt_jsonl: Path):
    dump_users_connections(FollowDirection.FOLLOWER, usernames, tgt_jsonl)
