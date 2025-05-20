
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![PyPI Version](https://img.shields.io/pypi/v/ResearchTikPy.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

<p align="middle">
  <img src="/images/logo.png" width="400" /> 
</p>

ResearchTikPy is a Python library designed to facilitate access to [TikTok's Research API](https://developers.tiktok.com/products/research-api/), providing a simple and intuitive interface for collecting data on videos, users, comments, and more. This library is intended for academic and research purposes, aiming to streamline the data collection process from TikTok without directly interfering with the API.

**You need to have access to the Research API to use this library**

**Features of ResearchTikPy:**

<div align="center">

| Available Functions |
|-----------------------------|
| [Query videos using custom conditions](#get_videos_query) |
| [Fetch video infos by key term(s)](#keyterm_search) |
| [Fetch user infos](#get_users_info) |
| [Search for videos by user(s)](#get_videos_info) |
| [Collect comments from video(s)](#get_video_comments) |
| [Fetch the followers of account(s)](#get_followers) |
| [Fetch account(s) followed by a user](#get_following) |
| [Fetch videos liked by a user](#get_liked_videos) |
| [Fetch videos pinned by a user](#get_pinned_videos) |


</div>

<br><br>

## What you need to consider before getting started:


1. **This package is in active development! Please report bugs & errors, and feel free to suggest additional functions!**
2. Read [TikTok's guide](https://developers.tiktok.com/doc/about-research-api/) about the research API to inform you about restrictions, daily quotas, and FAQs.
3. Currently, The Research API does not allow the download of videos. You need to use other sources for this outside the spectrum of the official API.
4. Splitting your requests into smaller chunks is generally advised to avoid longer fetching times and data loss.
5. The library uses automatic rate-limiting (pausing when TikTok returns HTTP 429 errors), but manual adjustments to wait times may improve performance.



## Installation
### Generating access token

Before using ResearchTikPy, you must obtain access credentials (client key and secret) from TikTok's developer platform. Navigate to `manage apps` on TikToks developer webpage to find your `client_key` and `client_secret` <p align="middle">
  <img src="/images/Credentials_2.png" width="800" />

  
</p>

**Currently, the most efficient method is to install the package via pip.**

```bash
# Install
pip install researchtikpy

# Import
import researchtikpy as rtk


# Or import individual modules: F.e.

from researchtikpy import get_access_token  # This way you could leave out the `rtk.` at the beginning of every researchtikpy function.
```



Once you have your credentials, you can use the library to generate an access token that you need to reference every time you run a command in this library:

```bash
# It is advised to store your tokens in separate objects or save them in your system's environment to avoid accidental publication of the credentials.

client_key = 'your_client_key'
client_secret = 'your_client_secret'

access_token = rtk.get_access_token(client_key, client_secret)

# OR paste the credentials within the command

access_token_dict = rtk.get_access_token(client_key, client_secret)  # Get the full dictionary
access_token = access_token_dict["access_token"] # stores the access token string as a separate object that you can reference in every command.

# print(access_token_dict) # Testing, if necessary. It should look something like this:


#Access Token: clt.Vl7HEasdfdeX28Z0G4wervRoPpY5f3zAGgYmGAAyGkowkYCusgbwqmb4NtNzn2QstXh
#Expires In: 7200
#Token Type: Bearer

```

# Features

This package features every possible query currently provided by the Researcher API of TikTok. For the full documentation, including a list of variables, see the official [Codebook](https://developers.tiktok.com/doc/research-api-codebook).

<br>

<a name="keyterm_search"></a>

## Field Paramaters

* **query/hashtag(s)/username(s)/video_id(s)/shop_id(s)/product_id(s)**: A list of strings to search for, e.g., "FYP" or ["FYP", "FORYOURPAGE"].
* **access_token**: Your valid access token for the TikTok Research API. Stored as a string.
* **start_date**: The start date for the search. The format should be 'YYYYMMDD'.
* **end_date**: The end date for the search. The format should be 'YYYYMMDD'. Start & end dates should be within a 30-day range. Otherwise, the TikTok Endpoint will report an error.
* **max_count** (Optional): Maximum units per request is 100 (the default). It is advised to keep it like this or specify a smaller value.
* **total_max_count** (Optional): The total maximum number of videos to collect. **Keeping this within a manageable range is advised because of the fetching duration and daily quota limit! The default is infinite.** Stored as an integer, e.g., 500.
* **region_code** (Optional): The region code to filter videos by. See list of [region_codes](https://developers.tiktok.com/doc/research-api-specs-query-videos).
* **music_id** (Optional): The music ID to filter videos by. Stored as a string.
* **effect_id** (Optional): The effect ID to filter videos by. Stored as a string.
* **max_count** (Optional):  The maximum number of videos to return **per individual get request** (default & max is 100). 
* **rate_limit_pause** (Optional):  Time in seconds to wait when a rate limit error is encountered. The default is 60 seconds. It can be adjusted as you like, e.g., 30.
* **verbose** (Optional): If True (default), prints detailed logs; if False, suppresses most print statements.
  
<br><be>

<a name="get_users_query"></a>
### Function: **get_videos_query**

Fetches video information using a custom query in a more flexible way (e.g. combining usernames, hashtags and other conditions) than the specialized features that follow beneath. See [TikTok's guide](https://developers.tiktok.com/doc/about-research-api/) for possible parameters. If you only want to collect data on users use [Fetch user infos](#get_users_info) instead.

```bash
videos_df = rtk.get_videos_query(query, access_token, start_date, end_date, total_max_count, max_count=100)
```

Example call

```bash
from researchtikpy.query_lang import Query, Condition, Operators, Fields

query = Query(
    and_=[
        Condition(Fields.username, Operators.equals, ["username1"]),
        Condition(Fields.hashtag_name, Operators.equals, ["hashtag"]) 
    ]
)
start_date = "20250101"
end_date = "20250131"
total_max_count = 100

data = rtk.get_videos_query(query, access_token, start_date, end_date, total_max_count)
```


### Function: **Keyterm search**

Fetches video information by hashtag. 

```bash
videos_df = rtk.get_videos_hashtag(hashtags, access_token, start_date, end_date, total_max_count (optional),
     region_code (optional), music_id (optional), effect_id (optional), max_count (optional),  rate_limit_pause (optional))
```

Example Call

```bash
access_token = "clt.rasddUatUsHasdnHYV2zGw7aQasdxpYpxNz3zjaMfBksdfxXA7" # Randomized token. Don't share your access token! 
hashtags = ["fyp", "FYP"]
start_date = "20230101"
end_date = "20240131"

videos_df = rtk.get_videos_hashtag(hashtags, access_token, start_date, end_date, total_max_count = 500)
```


<a name="get_users_info"></a>
### Function: **get_users_info**

Fetches account information for given usernames within the specified date range and compiles them into a single data frame.

```bash
user_df = rtk.get_users_info(usernames, access_token, start_date, end_date)
```



<br><br>

<a name="get_videos_info"></a>
### Function: **get_videos_info**

Fetches all videos & video metadata of an account or accounts and compiles them into a single data frame (with account IDs).

```bash
videos_df = rtk.get_videos_info(usernames, access_token, start_date, end_date, total_max_count (optional), fields (optional), max_count(optional))
```


<br><br>

<a name="get_video_comments"></a>
### Function: **get_video_comments**

Fetches comments on video(s) and compiles them into a single data frame (with video IDs).

```bash
comments_df = rtk.get_video_comments(videos_df, access_token, fields (optional), max_count (optional), verbose (optional))
```

<br><br>

<a name="get_pinned_videos"></a>
### Function: **get_pinned_videos**

Fetches pinned videos of accounts and compiles them into a single DataFrame.

```bash
pinned_df = rtk.get_pinned_videos(usernames, access_token, fields (optional), max_count (optional), verbose (optional))
```

* **usernames**: List of usernames to fetch videos for. Reports no pinned videos if the account has none. 
* **access_token**: Authorization token for TikTok Research API.
* **fields** (optional)
* **verbose** (optional)

<br><br>

<a name="get_liked_videos"></a>
### Function: **get_liked_videos**

Fetches metadata of videos accounts have like. Only works if the user has enabled public access to liked videos. This is disabled by default on most accounts.

```bash
liked_df = rtk.get_liked_videos(usernames, access_token, fields (optional), max_count (optional), verbose (optional))
```

<br><br>

<a name="get_following_users"></a>
### Function: **get_following_users**

Fetches followers of accounts and compiles them into a single data frame. It is advised to keep the list of usernames short to avoid longer runtimes and account for a large number of possible followers! 
Compiles them into a single data frame with the variable `target_account` indicating the seed account.

```bash
following = rtk.get_following (usernames, access_token, fields (optional), max_count (optional), verbose (optional))
```

<br><br>

<a name="get_followers"></a>
### Function: **get_followers**

Fetches followers for multiple users and compiles them into a single data frame. It is advised to keep the list of 
usernames short to avoid longer runtimes OR to use the `total_count` parameter to avoid reaching daily quotas rather quickly.

```bash
followers = rtk.get_followers (usernames, access_token, total_count (optional) fields (optional), max_count (optional), verbose (optional))
```

  
</p>



## TikTok Shops API

<a name="get_shop_info"></a>
### Function: **get_shop_info**
Fetches shop-level metadata.

```bash
shop_info = rtk.get_shop_info(shop_name, access_token)
```
<a name="get_product_info"></a>
### Function: get_product_info
Fetches product details from a given shop.

```bash
product_info = rtk.get_product_info(shop_id, access_token)
```

<a name="get_shop_reviews"></a>
### Function: get_product_reviews
Fetches reviews for a given product.

```bash
product_reviews = rtk.get_product_reviews(product_id, access_token)
```


## Cite

Please feel free to cite me when using the package: 

Hohner, J., Ruiz, Tomas & Kessling, Philipp (2024). ResearchPikTy (Python Library). GitHub Repository: https://github.com/HohnerJulian/ResearchTikPy
doi:10.13140/RG.2.2.24209.03682

<br>
or Bibtex: 
<br>
@misc{Hohner2024ResearchTikPy,
  author = {Hohner, Julian; Ruiz, Tomas; Kessling, Philipp},
  title = {{ResearchTikPy: Python Library for TikTok's Research API}},
  year = {2024},
  howpublished = {\url{https://github.com/HohnerJulian/ResearchTikPy}},
  note = {Accessed: yyyy-mm-dd},
  doi = {10.13140/RG.2.2.24209.03682}
}
















