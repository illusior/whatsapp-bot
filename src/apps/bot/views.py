from django.views import generic


class BotSettingsView(generic.TemplateView):
    template_name = "index.html"


__all__ = ["HOME_URL", "BotSettingsView"]
