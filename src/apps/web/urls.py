from django.urls import re_path

from apps.web.views import WebMainView

urlpatterns = [re_path("", WebMainView.as_view(), name="home")]
