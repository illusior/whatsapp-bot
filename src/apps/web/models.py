from django.db import models
from .validators.bot_settings import *


class BotSettings(models.Model):
    to_send_message = models.TextField(
        "message to send",
        blank=True,
        help_text="message to send",
        validators=[validate_message_to_send],
    )

    id_google_sheet = models.CharField(
        "GoogleSheets ID",
        blank=True,
        max_length=100,
        help_text="GoogleSheets ID",
        validators=[validate_google_spreadsheet_url_as_id],
    )

    id_data_column_google_sheet = models.CharField(
        "Column to read data from",
        blank=True,
        max_length=100,
        help_text="Column to read data from",
        validators=[validate_google_spreadsheet_column_index],
    )


class BotLogModel(models.Model):
    K_DATETIME_RECORD = "datetime_record"
    K_INITIATOR = "initiator"
    K_ACTION_TYPE = "action_type"
    K_MESSAGE = "message"

    datetime_record = models.DateTimeField("Record creation time")

    initiator = models.CharField(
        "Who is the initiator of the action", max_length=100
    )
    action_type = models.CharField("Action type", max_length=100)
    message = models.CharField("Action's description", max_length=1000)

    def __str__(self) -> str:
        return f"[{self.datetime_record}] <{self.initiator}> {{self.action_type}} {self.message}"

__all__ = [
    "BotLogModel",
    "BotSettings"
]