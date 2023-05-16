from django.urls import path

from src.apps.bot.views import BotSettingsView

urlpatterns = [path("", BotSettingsView.as_view(), name="home")]
