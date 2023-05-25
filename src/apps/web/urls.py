from django.urls import path

from apps.web.views import WebMainView
from apps.web.oauth_view import GoogleApiOAuthReturnView
from .src_bot.common.google.api import GoogleSheetsAuthData

WEB_MAIN = "WEB_MAIN"
GOOGLE_OAUTH_RETURN = "GOOGLE_OAUTH_RETURN"

URLS_NAMES = {
    WEB_MAIN: "home",
    GOOGLE_OAUTH_RETURN: "oauth-google-return",
}

urlpatterns = [
    path("", WebMainView.as_view(), name=URLS_NAMES[WEB_MAIN]),
    path(f"{GoogleSheetsAuthData.REDIRECT_PAGE_URL}", GoogleApiOAuthReturnView.as_view(), name=URLS_NAMES[GOOGLE_OAUTH_RETURN])
]
