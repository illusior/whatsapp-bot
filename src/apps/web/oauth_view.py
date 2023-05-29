from django.http import (
    HttpResponseRedirect,
)
from django.views import generic

from .src_bot.common.google.api import GoogleSheetsAuthData, update_google_token
from .src_bot.mailing import *
from .src_bot.common.google.api import GoogleSheetsAuthData


GET_GOOGLE_OAUTH2_MSG = "google_oauth2_msg"
GET_GOOGLE_OAUTH2_INSECURE_VALUE = "insecure_state"

# oauth2/google/return/


class GoogleApiOAuthReturnView(generic.TemplateView):
    template_name = "web/google_oauth.html"

    def get(self, request, *_, **__):
        if (
            request.GET[GoogleSheetsAuthData.GET_STATE_ARG]
            != GoogleSheetsAuthData.STATE_APP_INSTANCE
        ):
            return HttpResponseRedirect(
                f"{GoogleSheetsAuthData.REDIRECT_URI}?{GET_GOOGLE_OAUTH2_MSG}={GET_GOOGLE_OAUTH2_INSECURE_VALUE}"
            )

        update_google_token(request.GET[GoogleSheetsAuthData.GET_CODE_ARG])
        return HttpResponseRedirect(GoogleSheetsAuthData.REDIRECT_URI)
