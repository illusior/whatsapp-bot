from dataclasses import dataclass

import os
import random
import string

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config.settings import BASE_DIR, PORT, ALLOWED_HOSTS, LOCAL_, PROD_

from logger.server_logger import SERVER_LOGGER


def _random_string(length=16):
    letters = string.printable

    return "".join(random.choice(letters) for _ in range(length))


# GOOGLE SHEETS #


@dataclass
class GoogleSheetsAuthData:
    CREDENTIALS_PATH: str = (
        BASE_DIR / "user_data/google/credentials_google_sheet_web.json"
    )

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]

    TOKEN_PATH: str = BASE_DIR / "user_data/google/token_google_sheet.json"

    REDIRECT_PAGE_URL = "oauth2/google/return/"  # append to REDIRECT_URI
    REDIRECT_URI = f"http{'s' if PROD_ else ''}://{ALLOWED_HOSTS[0]}{f':{PORT}' if LOCAL_ else ''}/"

    STATE_APP_INSTANCE = _random_string()

    GET_STATE_ARG = "state"
    GET_CODE_ARG = "code"


# GOOGLE SHEETS #


def is_token_exists() -> bool:
    return os.path.exists(GoogleSheetsAuthData.TOKEN_PATH)


def is_google_token_valid() -> bool:
    creds: Credentials = None

    if is_token_exists():
        creds = Credentials.from_authorized_user_file(
            GoogleSheetsAuthData.TOKEN_PATH, GoogleSheetsAuthData.SCOPES
        )
        return creds and creds.valid

    return False


def get_google_auth_url():
    flow = InstalledAppFlow.from_client_secrets_file(
        GoogleSheetsAuthData.CREDENTIALS_PATH,
        GoogleSheetsAuthData.SCOPES,
        redirect_uri=f"{GoogleSheetsAuthData.REDIRECT_URI}{GoogleSheetsAuthData.REDIRECT_PAGE_URL}",
        state=GoogleSheetsAuthData.STATE_APP_INSTANCE,
    )

    auth_url, state = flow.authorization_url(
        prompt="consent", access_type="offline", include_granted_scopes="true"
    )

    return auth_url, state


def update_google_token(code) -> Credentials:
    creds: Credentials | None = get_google_token()

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            GoogleSheetsAuthData.CREDENTIALS_PATH,
            GoogleSheetsAuthData.SCOPES,
            redirect_uri=f"{GoogleSheetsAuthData.REDIRECT_URI}{GoogleSheetsAuthData.REDIRECT_PAGE_URL}",
        )
        flow.fetch_token(code=code)
        creds = flow.credentials

        with open(GoogleSheetsAuthData.TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    elif not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())


def get_google_token() -> Credentials | None:
    if os.path.exists(GoogleSheetsAuthData.TOKEN_PATH):
        return Credentials.from_authorized_user_file(
            GoogleSheetsAuthData.TOKEN_PATH, GoogleSheetsAuthData.SCOPES
        )
    return None


class GoogleApiServiceBuilder:
    @classmethod
    def from_api_key(cls, service_name, api_version, api_key):
        return build(
            serviceName=service_name, version=api_version, developerKey=api_key
        )

    @classmethod
    def from_oauth_2(cls, service_name, api_version, creds=None):
        if not creds:
            creds = get_google_token()

        if not creds:
            err = RuntimeError(
                "Failed to build Google's service from oauth2. Credentials are missing"
            )
            SERVER_LOGGER.log(SERVER_LOGGER.ERROR, err)
            raise err

        return build(
            serviceName=service_name, version=api_version, credentials=creds
        )


__all__ = ["GoogleSheetsAuthData"]
