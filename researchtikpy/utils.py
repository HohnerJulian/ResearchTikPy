def validate_access_token_object(access_token) -> str:
    """
    Validate the access token object and return the access token string.

    Parameters
    ----------
    access_token : str or dict
        Access token for TikTok's API.

    Returns
    -------
    str
        Access token string.

    Raises
    ------
    ValueError
        If the access token object is invalid.
    """
    if isinstance(access_token, str):
        return access_token
    elif isinstance(access_token, dict):
        return access_token.get("access_token")
    else:
        raise ValueError("Invalid access token object. Please provide a valid access token string or dictionary.")
