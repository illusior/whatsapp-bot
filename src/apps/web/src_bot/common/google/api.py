from dataclasses import dataclass
import os
import requests

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


from config.settings import BASE_DIR, PORT, ALLOWED_HOSTS, DEBUG

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
    REDIRECT_URI = (
        f"http{'s' if not DEBUG else ''}://{ALLOWED_HOSTS[0]}:{PORT}/"
    )

    API_KEY = os.environ.get("GOOGLE_SPREADSHEET_API_KEY")


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


def get_google_auth_url():
    flow = InstalledAppFlow.from_client_secrets_file(
        GoogleSheetsAuthData.CREDENTIALS_PATH,
        GoogleSheetsAuthData.SCOPES,
        redirect_uri= f"{GoogleSheetsAuthData.REDIRECT_URI}{GoogleSheetsAuthData.REDIRECT_PAGE_URL}",
        # state="" TODO: use state to more security
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )

    return auth_url


def update_google_token(code) -> Credentials:
    creds: Credentials | None = get_google_token()

    # If there are no (valid) credentials available, let the user log in.
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            GoogleSheetsAuthData.CREDENTIALS_PATH,
            GoogleSheetsAuthData.SCOPES,
            redirect_uri= f"{GoogleSheetsAuthData.REDIRECT_URI}{GoogleSheetsAuthData.REDIRECT_PAGE_URL}",
            # state="" TODO: use state for more security
        )
        flow.fetch_token(code=code)
        creds = flow.credentials

        with open(GoogleSheetsAuthData.TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    elif not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())


def get_google_token() -> Credentials | None:
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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
            raise RuntimeError("Failed to build Google's service from oauth2. Credentials are missing")

        return build(
            serviceName=service_name, version=api_version, credentials=creds
        )


__all__ = ["GoogleSheetsAuthData"]
