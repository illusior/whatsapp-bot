from django.forms import Textarea, TextInput
from django.shortcuts import render, redirect, HttpResponse
from django.views import generic

import os

# from django.contrib.messages.views import SuccessMessageMixin TODO: use mixin?

from .oauth_view import GET_GOOGLE_OAUTH2_MSG, GET_GOOGLE_OAUTH2_INSECURE_VALUE

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
from .src_bot.common.google.api import *


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
                "class": "input input--stretch input--xl send--message--input",
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
                "placeholder": f"Столбик с номерами (A-Z), текущий столбик: {values_map[K_ID_DATA_COLUMN_GOOGLE_SHEET]}",
            },
        ),
    }

    return widgets


# Context Keys

CK_BOT_SETTINGS_FORM = "settings_form"
CK_LOG_BOT_LIST = "log_list"
CK_WAS_ERROR = "was_error"
CK_ON_FORM_POST_POPUP_TYPE = "popup_type"  # FormStatus as str
CK_ON_SEND_MESSAGES_POPUP = "messages_are_sending_popup"
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
        context[CK_HAS_GOOGLE_TOKEN] = is_google_token_valid()

        if BOT_LOG_MODEL_CLASS.objects.all().count() > 5000:
            BOT_LOG_MODEL_CLASS.objects.all().delete()

        return context

    def get(self, request, *_, **kwargs):
        context = self.get_context_data(**kwargs)
        # BOT_SETTINGS_FORM_CLASS.Meta.model.objects.all().delete()

        if GET_GOOGLE_OAUTH2_MSG in request.GET:
            if (
                request.GET[GET_GOOGLE_OAUTH2_MSG]
                == GET_GOOGLE_OAUTH2_INSECURE_VALUE
            ):
                context[CK_WAS_ERROR] = True
                context[CK_ON_FORM_POST_POPUP_TYPE] = get_form_status_str(
                    FormStatus.ERR
                )
                _update_context_err(
                    context,
                    "Не удалось дать доступ к Гугл-сервису. Ваше соединение небезопасно.",
                    code="err_insecure_google_ouath2",
                )

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
                auth_url, _ = get_google_auth_url()
                return redirect(auth_url)

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
            if context[CK_ON_FORM_POST_POPUP_TYPE] == get_form_status_str(
                FormStatus.ERR
            ):
                for k, err in list(context[CK_ERRORS].items()):
                    if isinstance(err[0], ValidationWarn):
                        del context[CK_ERRORS][k]

            context[CK_WAS_ERROR] = True

        bot_settings_form_factory = (
            self._create_bot_settings_form_factory(
                self._get_completed_bot_settings()
            )
            if CK_ERRORS in context
            else self._create_bot_settings_form_factory(
                self._get_completed_bot_settings(request)
            )
        )  # we're rendering current bot settings in placeholders in widgets of inputs if data is ok

        context[CK_BOT_SETTINGS_FORM] = bot_settings_form_factory()

        return render(request, self.template_name, context)

    def _get_completed_bot_settings(self, request=None):
        # TODO: remove all non-relative for this view instances methods, that are not using `self`
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
            context[CK_ON_SEND_MESSAGES_POPUP] = get_form_status_str(
                FormStatus.OK
            )
        except Exception:
            _update_context_err(
                context,
                f"Не удалось отправить сообщения. Подробнее в логе бота",
                code="err_empty_settings_on_first_set",
            )
            context[CK_ON_FORM_POST_POPUP_TYPE] = get_form_status_str(
                FormStatus.ERR
            )
            context[CK_WAS_ERROR] = True

        return context


def reset_settings(request):
    BOT_SETTINGS_FORM_CLASS.Meta.model.objects.all().delete()
    if os.path.exists(GoogleSheetsAuthData.TOKEN_PATH):
        os.remove(GoogleSheetsAuthData.TOKEN_PATH)

    return HttpResponse()


__all__ = ["WebMainView", "reset_settings"]
