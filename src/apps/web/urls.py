from django.urls import re_path

from apps.web.views import WebMainView
from .src_bot import mailing

urlpatterns = [
    re_path("", WebMainView.as_view(), name="home"),
    # re_path("", mailing.generalMailing, name="sendmessage"),
]
