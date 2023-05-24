from django.urls import re_path

from apps.web.views import WebMainView
# from .views_oauth import RedirectOauthView
from .src_bot.common.google.api import GoogleSheetsAuthData

urlpatterns = [
    re_path("", WebMainView.as_view(), name="home"),
    # re_path("", mailing.generalMailing, name="sendmessage"),
    # re_path(GoogleSheetsAuthData.REDIRECT_URI, RedirectOauthView, name="oauth-google-spreadsheet"), 
]
