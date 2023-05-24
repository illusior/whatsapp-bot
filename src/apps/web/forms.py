from django import forms
from django.forms import modelform_factory

from .models import BotSettings
from .validators.bot_settings import *

import enum


@enum.unique
class FormStatus(enum.Enum):
    OK = 0
    WARN = 1
    ERR = 2


def get_form_status_str(form_status: FormStatus) -> str:
    if form_status == FormStatus.OK:
        return "ok"
    if form_status == FormStatus.WARN:
        return "warn"
    if form_status == FormStatus.ERR:
        return "err"
    return "err"


class BotSettingsForm(forms.ModelForm):
    class Meta:
        K_ID_DATA_COLUMN_GOOGLE_SHEET = "id_data_column_google_sheet"
        K_ID_GOOGLE_SHEET = "id_google_sheet"
        K_TO_SEND_MESSAGE = "to_send_message"

        model = BotSettings
        fields = [
            K_TO_SEND_MESSAGE,
            K_ID_GOOGLE_SHEET,
            K_ID_DATA_COLUMN_GOOGLE_SHEET,
        ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.auto_id = "%s"

    def clean_to_send_message(self):
        msg = self.cleaned_data[self.Meta.K_TO_SEND_MESSAGE]
        validate_message_to_send(msg)
        return msg

    def clean_id_google_sheet(self):
        id_spreadsheet = self.cleaned_data[self.Meta.K_ID_GOOGLE_SHEET]
        validate_google_spreadsheet_url_as_id(id_spreadsheet)
        return id_spreadsheet

    def clean_id_data_column_google_sheet(self):
        column_id = self.cleaned_data[self.Meta.K_ID_DATA_COLUMN_GOOGLE_SHEET]
        validate_google_spreadsheet_column_index(column_id)
        return column_id

    def save(self, commit=True):
        self.full_clean()

        manager = BotSettings.objects
        settings = manager.filter()[0] if manager.filter() else manager.create()

        url_or_id = self.cleaned_data.get(self.Meta.K_ID_GOOGLE_SHEET)
        url_or_id = url_or_id if url_or_id else settings.id_google_sheet
        match = re.search(SPREADSHEET_ID_REGEX, url_or_id)
        id = match[0] if match else url_or_id

        settings.id_google_sheet = id

        message = self.cleaned_data.get(self.Meta.K_TO_SEND_MESSAGE)
        message = message if message else settings.to_send_message
        settings.to_send_message = message

        column_id = self.cleaned_data.get(
            self.Meta.K_ID_DATA_COLUMN_GOOGLE_SHEET
        )
        column_id = (
            column_id if column_id else settings.id_data_column_google_sheet
        )
        settings.id_data_column_google_sheet = column_id

        settings.save()

        return settings


def create_bot_settings_form_factory(widgets_map=None) -> BotSettingsForm:
    K_ID_DATA_COLUMN_GOOGLE_SHEET = (
        BotSettingsForm.Meta.K_ID_DATA_COLUMN_GOOGLE_SHEET
    )
    K_ID_GOOGLE_SHEET = BotSettingsForm.Meta.K_ID_GOOGLE_SHEET
    K_TO_SEND_MESSAGE = BotSettingsForm.Meta.K_TO_SEND_MESSAGE

    values = {
        K_ID_DATA_COLUMN_GOOGLE_SHEET: "",
        K_ID_GOOGLE_SHEET: "",
        K_TO_SEND_MESSAGE: "",
    }

    manager = BotSettings.objects
    last_record = manager.filter()[0] if manager.filter() else BotSettings()
    values[
        K_ID_DATA_COLUMN_GOOGLE_SHEET
    ] = last_record.id_data_column_google_sheet
    values[K_ID_GOOGLE_SHEET] = last_record.id_google_sheet
    values[K_TO_SEND_MESSAGE] = last_record.to_send_message

    return modelform_factory(
        model=BotSettings, form=BotSettingsForm, widgets=widgets_map
    )
