from django.http import (
    HttpResponseRedirect,
)
from django.views import generic

from logger.django_logger import DJANGO_LOGGER

from .src_bot.common.google.api import GoogleSheetsAuthData, update_google_token
from .src_bot.mailing import *
from .src_bot.common.google.api import GoogleSheetsAuthData


GET_GOOGLE_OAUTH2_MSG = "google_oauth2_msg"
GET_GOOGLE_OAUTH2_INSECURE_VALUE = "insecure_state"

# oauth2/google/return/


class GoogleApiOAuthReturnView(generic.TemplateView):
    template_name = "web/google_oauth.html"

    def get(self, request, *_, **__):
        update_google_token(request.GET[GoogleSheetsAuthData.GET_CODE_ARG])
        return HttpResponseRedirect(GoogleSheetsAuthData.REDIRECT_URI)
