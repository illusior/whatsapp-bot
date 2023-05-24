import os.path

from dataclasses import dataclass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config.settings import BASE_DIR

# GOOGLE SHEETS #

@dataclass
class GoogleSheetsAuthData:
    CREDENTIALS_PATH: str = (
        BASE_DIR / "user_data/google/credentials_google_sheet.json"
    )

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]

    TOKEN_PATH: str = BASE_DIR / "user_data/google/gs_token.json"


# GOOGLE SHEETS #


def make_credentials(auth_data: GoogleSheetsAuthData) -> Credentials:
    creds: Credentials = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(auth_data.TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(
            auth_data.TOKEN_PATH, auth_data.SCOPES
        )

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                auth_data.CREDENTIALS_PATH, auth_data.SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(auth_data.TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds


__all__ = ["GoogleSheetsAuthData", "make_credentials"]
