from dataclasses import dataclass
import os

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config.settings import BASE_DIR, DEBUG

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

    REDIRECT_URI: str = "localhost"

    API_KEY = os.environ.get("GOOGLE_SPREADSHEET_API_KEY")


# GOOGLE SHEETS #


def make_credentials() -> Credentials:
    creds: Credentials = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(GoogleSheetsAuthData.TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(
            GoogleSheetsAuthData.TOKEN_PATH, GoogleSheetsAuthData.SCOPES
        )

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Refresh token")
        else:
            print("Create new token")
            flow = InstalledAppFlow.from_client_secrets_file(
                GoogleSheetsAuthData.CREDENTIALS_PATH,
                GoogleSheetsAuthData.SCOPES,
            )
            # if DEBUG:
            creds = flow.run_local_server(port=0)
            # else:
            #     authorization_url, state = flow.authorization_url(
            #         access_type="offline",
            #         include_granted_scopes="true",
            #         redirect_uri=GoogleSheetsAuthData.REDIRECT_URI,
            #     )

        # Save the credentials for the next run
        with open(GoogleSheetsAuthData.TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds


class GoogleApiServiceBuilder:
    @classmethod
    def from_api_key(cls, service_name, api_version, api_key):
        return build(
            serviceName=service_name, version=api_version, developerKey=api_key
        )

    @classmethod
    def from_oauth_2(cls, service_name, api_version, creds=None):
        if not creds:
            creds = make_credentials()
        return build(serviceName=service_name, version=api_version, credentials=creds)


__all__ = ["GoogleSheetsAuthData", "make_credentials"]
