



<p align="left">
  <img src="/images/Package_logo.png" width="400" /> <!-- Adjust width as needed -->
</p>

ResearchTikPy is a Python library designed to facilitate access to TikTok's Research API, providing a simple and intuitive interface for collecting data on videos, users, comments, and more. This library is intended for academic and research purposes, aiming to streamline the data collection process from TikTok without having to interfere with the API directly.



### Installation

Currently, ResearchTikPy is not available on PyPI, so it needs to be installed directly from the source:

```bash
git clone https://github.com/HohnerJulian/ResearchTikPy.git
cd ResearchTikPy
pip install .
```
### Generating access token

Before using ResearchTikPy, you must obtain access credentials (client key and secret) from TikTok's developer platform. Once you have your credentials, you can use the library to generate an access token that you need to reference every time you run a command in this library:

```bash
# It is advided to store your tokens in seperate objects or save them in the environment of your system to avoid accidental publication of the credentials.

client_key = 'your_client_key'
client_secet = 'your_client_secret'

access_token = get_access_token(client_krey, client_secret)

# OR paste the credentials within the command

access_token = get_access_token('your_client_key', 'your_client_secret')


# print(access_token) # Testing, if necessary. It should look something like this:


Access Token: clt.Vl7HEasdfdeX28Z0G4wervRoPpY5f3zAGgYmGAAyGkowkYCusgbwqmb4NtNzn2QstXh
Expires In: 7200
Token Type: Bearer

```

## Features

This package features every possible query currently provided by the Researcher API of TikTok. For the full documentation, including a list of variables, see the official [Codebook](https://developers.tiktok.com/doc/research-api-codebook)


### Function: Keyterm search

Collect video information by hashtag. 

```bash
videos_df = search_videos_by_hashtag(hashtags, access_token, start_date, end_date, total_max_videos (optional),
     region_code (optional), music_id (optional), effect_id (optional), max_coount (optional),  rate_limit_pause (optional))
```

Possible parameters are: 

* **hashtags**: A list of hashtag(s) to search for, e.g., "FYP" or ["FYP", "FORYOURPAGE"].
* **access_token**: Your valid access token for the TikTok Research API. Stored as a string.
* **start_date**: The start date for the search. The format should be 'YYYYMMDD'.
* **end_date**: The end date for the search. The format should be 'YYYYMMDD'.
* **total_max_count** (Optional): The total maximum number of videos to collect. **It is advised to keep this within a manageable range because of computer duration and daily quota limit! The default is infinite.** Stored as an integer, e.g., 500.
* **region_code** (Optional): The region code to filter videos by. See list of [region_codes](https://developers.tiktok.com/doc/research-api-specs-query-videos).
* **music_id** (Optional): The music ID to filter videos by. Stored as a string.
* **effect_id** (Optional): The effect ID to filter videos by. Stored as a string.
* **max_count** (Optional):  The maximum number of videos to return per request (up to 100). The default is 500.
* **rate_limit_pause** (Optional):  Time in seconds to wait when a rate limit error is encountered. The default is 60 seconds. It can be adjusted as you like, e.g., 30.


### Function: User Search

Collect user information. Possible parameters are: 

```bash
user_df = get_users_info(usernames, access_token, start_date, end_date)
```

Fetches video information for given usernames within the specified date range.
    * **usernames**: List of username(s) to fetch videos for.
    * **access_token**: Authorization token for TikTok Research API.
    * **start_date**
    * **end_date**
    * **max_count** (Optional)
    * **verbose** (Optional): If True (Default), prints detailed logs; if False, suppresses most print statements.




**Video Data**: Using a list of usernames, collect details of each video from these users: 
```bash
videos_df = get_videos_info(usernames, access_token, fields, start_date, end_date, max_count)
```
Dates should be entered as string such as f.e. 'YYYYMMDD'.

max_count is set to 100 by default. 
