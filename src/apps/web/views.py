from django.views import generic
from django.shortcuts import render

# from django.contrib.messages.views import SuccessMessageMixin TODO: use mixin?

from django.forms import Textarea, TextInput
from .models import BotSettings, BotLogModel
from .forms import (
    BotSettingsForm,
    create_bot_settings_form_factory,
    FormStatus,
    get_form_status_str,
)

from .validators.bot_settings import (
    ValidationWarn,
    ValidationError,
    _ as gettext_lazy,
)

from .src_bot.mailing import *


def _make_bot_settings_widgets(values_in_placeholders_map=None):
    K_TO_SEND_MESSAGE = BotSettingsForm.Meta.K_TO_SEND_MESSAGE
    K_ID_GOOGLE_SHEET = BotSettingsForm.Meta.K_ID_GOOGLE_SHEET
    K_ID_DATA_COLUMN_GOOGLE_SHEET = (
        BotSettingsForm.Meta.K_ID_DATA_COLUMN_GOOGLE_SHEET
    )

    values_are_not_none = (
        False if (values_in_placeholders_map is None) else True
    )
    values_map = {
        K_TO_SEND_MESSAGE: values_in_placeholders_map[K_TO_SEND_MESSAGE]
        if values_are_not_none
        else "",
        K_ID_GOOGLE_SHEET: values_in_placeholders_map[K_ID_GOOGLE_SHEET]
        if values_are_not_none
        else "",
        K_ID_DATA_COLUMN_GOOGLE_SHEET: values_in_placeholders_map[
            K_ID_DATA_COLUMN_GOOGLE_SHEET
        ]
        if values_are_not_none
        else "",
    }

    widgets_ = {
        K_TO_SEND_MESSAGE: Textarea(
            attrs={
                "class": "input input--stretch input--xl",
                "cols": 45,
                "rows": 5,
                "placeholder": f"Введите сообщение для отправки. Текущее сообщение: {values_map[K_TO_SEND_MESSAGE]}",
            },
        ),
        K_ID_GOOGLE_SHEET: TextInput(
            attrs={
                "class": "input input--stretch input--s",
                "placeholder": f"ID Google-таблицы: {values_map[K_ID_GOOGLE_SHEET]}",
            },
        ),
        K_ID_DATA_COLUMN_GOOGLE_SHEET: TextInput(
            attrs={
                "class": "input input--stretch input--s",
                "placeholder": f"Введите букву столбика, где лежат номера (A-Z), текущий столбик: {values_map[K_ID_DATA_COLUMN_GOOGLE_SHEET]}",
            },
        ),
    }

    return widgets_


# Context Keys

CK_BOT_SETTINGS_FORM = "settings_form"
CK_LOG_BOT_LIST = "log_list"
CK_WAS_ERROR = "was_error"
CK_ON_FORM_POST_POPUP_TYPE = "popup_type"  # FormStatus as str

# Context Keys


class WebMainView(generic.CreateView):
    template_name = "web/base.html"
    form_class = BotSettingsForm

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.object = None
        self.get_context_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[CK_LOG_BOT_LIST] = BotLogModel.objects.all()
        return context

    def get(self, request, *_, **kwargs):
        context = self.get_context_data(**kwargs)
        # self._get_all_bot_settings_records().delete()

        context = {
            CK_BOT_SETTINGS_FORM: self._create_bot_settings_form_factory(
                self._complete_bot_settings()
            )(),
            CK_WAS_ERROR: False,
            CK_LOG_BOT_LIST: BotLogModel.objects.all(),
        }

        return render(
            request,
            self.template_name,
            context,
        )

    def post(self, request, *_, **__):
        settings_empty_on_first_set = self._are_settings_empty(request.POST)
        context = {
            CK_WAS_ERROR: settings_empty_on_first_set,
            CK_LOG_BOT_LIST: BotLogModel.objects.all(),
        }

        if request.POST.get("action") == "send":
            context.update(
                {
                    CK_BOT_SETTINGS_FORM: self._create_bot_settings_form_factory(
                        self._complete_bot_settings()
                    )(),
                }
            )
            bot_complete_settings = self._complete_bot_settings(request)
            generalMailing(bot_complete_settings)
            return render(request, self.template_name, context)

        bot_settings_form: BotSettingsForm = self.form_class(request.POST)

        if not settings_empty_on_first_set:
            context.update(
                {CK_ON_FORM_POST_POPUP_TYPE: get_form_status_str(FormStatus.OK)}
            )
            bot_settings_form.save()

        form_is_valid = bot_settings_form.is_valid()
        if not form_is_valid or settings_empty_on_first_set:
            errors_data = bot_settings_form.errors.as_data()
            context.update(
                {
                    "errors": errors_data
                    if not settings_empty_on_first_set
                    else {
                        "msg": [
                            ValidationError(
                                gettext_lazy(
                                    "Необходимо ввести все данные при первой настройке"
                                ),
                                code="err_empty_settings_on_first_set",
                            )
                        ]
                    }
                }
            )

            context.update(
                {
                    CK_ON_FORM_POST_POPUP_TYPE: (
                        get_form_status_str(FormStatus.ERR)
                        if settings_empty_on_first_set
                        or not all(
                            isinstance(err[0], ValidationWarn)
                            for err in errors_data.values()
                        )
                        else get_form_status_str(FormStatus.WARN)
                    )
                }
            )
            context.update({CK_WAS_ERROR: True})

        bot_settings_form_factory = (
            self._create_bot_settings_form_factory()
            if context[CK_ON_FORM_POST_POPUP_TYPE]
            == get_form_status_str(FormStatus.ERR)
            else self._create_bot_settings_form_factory(
                self._complete_bot_settings(request)
            )
        )  # we're rendering current bot settings in placeholders in widgets of inputs if data is ok

        context.update({CK_BOT_SETTINGS_FORM: bot_settings_form_factory()})

        return render(request, self.template_name, context)

    def _complete_bot_settings(self, request=None):
        K_ID_DATA_COLUMN_GOOGLE_SHEET = (
            self.form_class.Meta.K_ID_DATA_COLUMN_GOOGLE_SHEET
        )
        K_ID_GOOGLE_SHEET = self.form_class.Meta.K_ID_GOOGLE_SHEET
        K_TO_SEND_MESSAGE = self.form_class.Meta.K_TO_SEND_MESSAGE

        bot_settings = {
            K_ID_DATA_COLUMN_GOOGLE_SHEET: request.POST[
                K_ID_DATA_COLUMN_GOOGLE_SHEET
            ]
            if request != None
            else "",
            K_ID_GOOGLE_SHEET: request.POST[K_ID_GOOGLE_SHEET]
            if request != None
            else "",
            K_TO_SEND_MESSAGE: request.POST[K_TO_SEND_MESSAGE]
            if request != None
            else "",
        }

        manager = BotSettings.objects
        if manager.count() != 0:
            if len(bot_settings[K_TO_SEND_MESSAGE]) == 0:
                bot_settings[K_TO_SEND_MESSAGE] = manager.filter()[
                    0
                ].to_send_message
            bot_settings[K_ID_GOOGLE_SHEET] = manager.filter()[
                0
            ].id_google_sheet
            if len(bot_settings[K_ID_DATA_COLUMN_GOOGLE_SHEET]) == 0:
                bot_settings[K_ID_DATA_COLUMN_GOOGLE_SHEET] = manager.filter()[
                    0
                ].id_data_column_google_sheet
        return bot_settings

    def _are_settings_empty(self, post_query) -> bool:
        no_settings_in_bd = self._get_all_bot_settings_records().count() == 0

        if not no_settings_in_bd:
            return False

        post_data = {
            key: post_query[key] for key in self.form_class.Meta.fields
        }
        any_setting_is_empty_from_post = any(
            len(value) == 0 for value in post_query.values()
        )

        return no_settings_in_bd and any_setting_is_empty_from_post

    def _create_bot_settings_form_factory(
        self, bot_settings_to_show_in_widgets=None
    ):
        return create_bot_settings_form_factory(
            _make_bot_settings_widgets(bot_settings_to_show_in_widgets)
        )

    def _get_all_bot_settings_records(self):
        return BotSettings.objects.all()


__all__ = ["WebMainView"]
