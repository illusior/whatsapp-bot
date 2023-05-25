from django.forms import Textarea, TextInput
from django.shortcuts import render, redirect
from django.views import generic

# from django.contrib.messages.views import SuccessMessageMixin TODO: use mixin?

from .models import BotSettings, BotLogModel
from .forms import (
    BotSettingsForm,
    FormStatus,
    create_bot_settings_form_factory,
    get_form_status_str,
)

from apps.web.src_bot.common.google.api import (
    get_google_auth_url,
    is_token_exists,
    is_google_token_valid,
)

from .validators.bot_settings import (
    ValidationWarn,
    ValidationError,
    _ as gettext_lazy,
)

from .src_bot.mailing import *


BOT_SETTINGS_FORM_CLASS = BotSettingsForm
BOT_LOG_MODEL_CLASS = BotLogModel

K_ID_DATA_COLUMN_GOOGLE_SHEET = (
    BOT_SETTINGS_FORM_CLASS.Meta.K_ID_DATA_COLUMN_GOOGLE_SHEET
)
K_ID_GOOGLE_SHEET = BOT_SETTINGS_FORM_CLASS.Meta.K_ID_GOOGLE_SHEET
K_TO_SEND_MESSAGE = BOT_SETTINGS_FORM_CLASS.Meta.K_TO_SEND_MESSAGE


def _make_bot_settings_widgets(values_in_placeholders_map=None):
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

    widgets = {
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

    return widgets


# Context Keys

CK_BOT_SETTINGS_FORM = "settings_form"
CK_LOG_BOT_LIST = "log_list"
CK_WAS_ERROR = "was_error"
CK_ON_FORM_POST_POPUP_TYPE = "popup_type"  # FormStatus as str
CK_ERRORS = "errors"
CK_HAS_GOOGLE_TOKEN = "has_google_token"

# Context Keys


def _update_context_err(context, msg, code):
    context[CK_ERRORS] = {
        "msg": [
            ValidationError(
                gettext_lazy(msg),
                code=code,
            )
        ]
    }


class WebMainView(generic.CreateView):
    template_name = "web/base.html"
    form_class = BOT_SETTINGS_FORM_CLASS

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.object = None
        self.get_context_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[CK_LOG_BOT_LIST] = BOT_LOG_MODEL_CLASS.objects.all()
        context[CK_BOT_SETTINGS_FORM] = self._create_bot_settings_form_factory(
            self._get_completed_bot_settings()
        )()
        context[CK_WAS_ERROR] = False
        context[CK_HAS_GOOGLE_TOKEN] = is_google_token_valid() and is_token_exists()

        return context

    def get(self, request, *_, **kwargs):
        context = self.get_context_data(**kwargs)
        # BOT_SETTINGS_FORM_CLASS.Meta.model.objects.all().delete()
        # BOT_LOG_MODEL_CLASS.objects.all().delete()

        return render(
            request,
            self.template_name,
            context,
        )

    def post(self, request, *_, **kwargs):
        context = self.get_context_data(**kwargs)

        settings_empty_on_first_set = self._are_settings_empty(request.POST)

        context[CK_WAS_ERROR] = (settings_empty_on_first_set,)
        context[CK_ON_FORM_POST_POPUP_TYPE] = get_form_status_str(FormStatus.OK)

        if request.POST.get("action") == "send":
            if not is_google_token_valid():
                return redirect(get_google_auth_url())

            updated_context = self._handle_on_send_messages_btn_press(
                request, context
            )
            return render(request, self.template_name, updated_context)

        bot_settings_form: BOT_SETTINGS_FORM_CLASS = self.form_class(
            request.POST
        )

        if not settings_empty_on_first_set:
            bot_settings_form.save()

        form_is_valid = bot_settings_form.is_valid()
        if not form_is_valid or settings_empty_on_first_set:
            errors_data = bot_settings_form.errors.as_data()
            if not settings_empty_on_first_set:
                context[CK_ERRORS] = errors_data
            else:
                _update_context_err(
                    context,
                    "Необходимо ввести все данные при первой настройке",
                    code="err_empty_settings_on_first_set",
                )

            context[CK_ON_FORM_POST_POPUP_TYPE] = (
                get_form_status_str(FormStatus.ERR)
                if settings_empty_on_first_set
                or not all(
                    isinstance(err[0], ValidationWarn)
                    for err in errors_data.values()
                )
                else get_form_status_str(FormStatus.WARN)
            )

            context[CK_WAS_ERROR] = True

        bot_settings_form_factory = (
            self._create_bot_settings_form_factory()
            if context[CK_ON_FORM_POST_POPUP_TYPE]
            == get_form_status_str(FormStatus.ERR)
            else self._create_bot_settings_form_factory(
                self._get_completed_bot_settings(request)
            )
        )  # we're rendering current bot settings in placeholders in widgets of inputs if data is ok

        context[CK_BOT_SETTINGS_FORM] = bot_settings_form_factory()

        return render(request, self.template_name, context)

    def _get_completed_bot_settings(self, request=None):
        bot_settings = {
            K_ID_DATA_COLUMN_GOOGLE_SHEET: "",
            K_ID_GOOGLE_SHEET: "",
            K_TO_SEND_MESSAGE: "",
        }
        if request:
            for k, _ in bot_settings.items():
                bot_settings[k] = request.POST[k]

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

    def _handle_on_send_messages_btn_press(self, request, context):
        try:
            bot_complete_settings = self._get_completed_bot_settings(request)
            generalMailing(bot_complete_settings)
            _update_context_err(context, "Сообщения отправляются", code="OK")
        except Exception as err:
            _update_context_err(
                context,
                f"Не удалось отправить сообщения. Причина: {err}",
                code="err_empty_settings_on_first_set",
            )
            context[CK_ON_FORM_POST_POPUP_TYPE] = get_form_status_str(
                FormStatus.ERR
            )
            context[CK_WAS_ERROR] = True

        return context


__all__ = ["WebMainView"]
