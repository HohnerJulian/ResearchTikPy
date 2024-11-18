from datetime import datetime, timedelta
from typing import Dict, Literal, Optional, Union

import requests


class AccessToken:

    def __init__(self, client_key, client_secret):
        """Requests an access token from the TikTok API using client credentials.

        Parameters
        ----------
        client_key : str
            The client key provided by TikTok.
        client_secret : str
            The client secret provided by TikTok.

        Raises
        ------
        Exception
            If the request to the TikTok API fails or is not successful.
        """
        self.client_key = client_key
        self.client_secret = client_secret
        self._token_type_: Literal["Bearer"] = "Bearer"
        self._expires_in_: int = 7200
        self._access_token_: str = self._get_access_token_()
        self._issued_at_: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if the access token has expired."""
        return datetime.now() > self.expires_at

    @property
    def expires_at(self) -> datetime:
        """Return the datetime when the access token expires."""
        return datetime.now() + timedelta(seconds=self._expires_in_)

    @property
    def token(self) -> str:
        """Return the currently valid access token."""
        if self.is_expired():
            self.refresh()
        return self._access_token_

    def refresh(self):
        """Refresh the access token if it has expired."""
        if self.is_expired():
            self._get_access_token_()

    def _get_access_token_(self):
        endpoint_url = "https://open.tiktokapis.com/v2/oauth/token/"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        response = requests.post(
            endpoint_url, headers=headers, data=data, timeout=10
        )  # TODO: Add timeout parameter

        if response.status_code != 200:
            raise ValueError(f"Failed to obtain access token: {response.text}")
        response_json = response.json()
        if response_json.get("error"):
            raise ValueError(f"Failed to obtain access token: {response_json.get('error_description')}")
        access_token = response_json.get("access_token")
        if access_token is None:
            raise ValueError(f"Failed to obtain access token: {response_json}")
        self._issued_at_ = datetime.now()
        self._expires_in_ = response_json.get("expires_in")
        self._token_type_ = response_json.get("token_type")

        return  access_token

    def __str__(self):
        return f"{self._token_type_}: {self.token}, expires at: {self.expires_at}"
    
    def __repr__(self):
        return self.__str__()


def validate_access_token_object(access_token: Union[AccessToken, Dict, str]) -> str:
    """
    Validate the access token object and return the access token string.

    Parameters
    ----------
    access_token : AccessToken, str or dict
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
    if isinstance(access_token, dict):
        return access_token.get("access_token")
    if isinstance(access_token, AccessToken):
        return access_token.token
    raise ValueError(
        "Invalid access token object. Please provide a valid access token string or dictionary."
    )
