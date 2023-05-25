from django.forms import Textarea, TextInput
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse

from django.http import HttpResponse, HttpRequest, QueryDict, HttpResponseRedirect
from .src_bot.common.google.api import GoogleSheetsAuthData, update_google_token

# from django.contrib.messages.views import SuccessMessageMixin TODO: use mixin?

from .src_bot.mailing import *

#oauth2/google/return/


class GoogleApiOAuthReturnView(generic.TemplateView):
   template_name = "web/google_oauth.html"

   def get(self, request, *_, **__):
        update_google_token(request.GET["code"])
        return HttpResponseRedirect(GoogleSheetsAuthData.REDIRECT_URI)
