from researchtikpy.utils import AccessToken


def get_access_token(client_key, client_secret) -> AccessToken:
    """
    Requests an access token from the TikTok API using client credentials.

    Parameters:
    - client_key (str): The client key provided by TikTok.
    - client_secret (str): The client secret provided by TikTok.

    Returns:
    - AccessToken: The access token, with its expiry duration, and the token type set.


    Raises:
    - Exception: If the request to the TikTok API fails or is not successful.
    """
    return AccessToken(client_key, client_secret)
