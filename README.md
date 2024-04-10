# ResearchTikPy

ResearchTikPy is a Python library designed to facilitate access to TikTok's Research API, providing a simple and intuitive interface for collecting data on videos, users, comments, and more. This library is intended for academic and research purposes, aiming to streamline the data collection process from TikTok without having to interfere with the API directly.

## Installation

Currently, ResearchTikPy is not available on PyPI, so it needs to be installed directly from the source:

```bash
git clone https://github.com/HohnerJulian/ResearchTikPy.git
cd ResearchTikPy
pip install .
```


##Usage
Before using ResearchTikPy, you must obtain access credentials (client key and secret) from TikTok's developer platform. Once you have your credentials, you can use the library to generate an access token that you need to reference every time you run a command in this library:

```bash
from researchtikpy import get_access_token, get_user_info, get_videos_info

# Obtain an access token
token = get_access_token('your_client_key', 'your_client_secret')
```

## Features

This package features every possible querry currently provided by the Researcher API of TikTok. For full documentation, including a list of variables, see the official [Codebook](https://developers.tiktok.com/doc/research-api-codebook)

Access Token Retrieval: Easily obtain an access token for authenticating API requests (see code above).

**User Data**: Collect detailed information about TikTok users: 
```bash
user_df = get_users_info(usernames, access_token)
```

**Video Data**: Using a list of usernames, collect details of each video from these users: 
```bash
videos_df = get_videos_info(usernames, access_token, fields, start_date, end_date, max_count)
```
Dates should be entered as string such as f.e. 'YYYYMMDD'.

max_count is set to 100 by default. 
