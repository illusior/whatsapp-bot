from django.views import generic
from django.shortcuts import render

# from .forms import MeetingForm

import enum


class BotSettingsPage(enum.IntEnum):
    message = 0
    google_sheet = 1
    log = 2


DEFAULT_PAGE = BotSettingsPage.message


class BotSettingsView:
    __slots__ = ['_cur_page']
    
    def __init__(self):
        self._cur_page: BotSettingsPage = DEFAULT_PAGE

    def get_current_page(self):
        return self._cur_page


class WebMainView(generic.TemplateView):
    template_name = "web/main.html"
    bot_settings_view = BotSettingsView()
    #form_class = MeetingForm #(request.POST or None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({"bot_settings_page": self.bot_settings_view.get_current_page()})

        return context

    def post(self, request, *args, **kwargs):
        context = {}
        print(request.POST)
        return render(request, self.template_name, context)


__all__ = ["WebMainView"]
