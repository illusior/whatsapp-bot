import os

from ..forms import BotSettingsForm
from .common.green_api import *
from .common.logging.logger import *
from .common.messages import *
from .google.GoogleSheetSource import GoogleSheetSource

from .AbstractSource import (
    OnlyDigitsSourceDecorator,
    UniqueSourceDecorator,
    NotEmptySourceDecorator,
)

from whatsapp_api_client_python.API import GreenApi

from .common.logging.logger import BOT_LOGGER
from ..models import BotLogModel

K_ID_DATA_COLUMN_GOOGLE_SHEET = (
    BotSettingsForm.Meta.K_ID_DATA_COLUMN_GOOGLE_SHEET
)
K_ID_GOOGLE_SHEET = BotSettingsForm.Meta.K_ID_GOOGLE_SHEET
K_TO_SEND_MESSAGE = BotSettingsForm.Meta.K_TO_SEND_MESSAGE


def generalMailing(bot_settings_form_post_data) -> None:
    wa = GreenApi(
        idInstance=os.environ.get("GREEN_API_ID_INSTANCE"),
        apiTokenInstance=os.environ.get("GREEN_API_TOKEN"),
    )

    to_send_message: str = bot_settings_form_post_data[K_TO_SEND_MESSAGE]
    id_data_column_google_sheet: str = bot_settings_form_post_data[
        K_ID_DATA_COLUMN_GOOGLE_SHEET
    ]
    id_google_sheet: str = bot_settings_form_post_data[K_ID_GOOGLE_SHEET]
    google_spreadsheets = UniqueSourceDecorator(
        OnlyDigitsSourceDecorator(
            NotEmptySourceDecorator(
                GoogleSheetSource(
                    id_google_sheet,
                    range=f"{id_data_column_google_sheet}:{id_data_column_google_sheet}",
                    api_version="v4",
                )
            )
        )
    )

    if not google_spreadsheets:
        err_msg = f"Unable to access Google-spreadsheet with `{id_google_sheet}` id. Check if you have access to it from your Google account."
        BOT_LOGGER.log(
            level=BOT_LOGGER.INFO,
            msg=err_msg,
            extra={
                BotLogModel.K_INITIATOR: "Bot",
                BotLogModel.K_ACTION_TYPE: "Access Google's Spreadsheets",
            },
        )
        raise RuntimeError(err_msg)

    for phone_number in google_spreadsheets:
        was_error = False
        err = None

        try:
            chatId = f"{phone_number}{CHAT_ID_MOBILE_DOMAIN}"
            wa.sending.sendMessage(chatId=chatId, message=to_send_message)
        except Exception as err_excpt:
            was_error = True
            err = err_excpt

        log_number = f"{phone_number[:3]}{''.join(['x' for i in range(len(phone_number) - 5)])}{phone_number[-2:]}"
        BOT_LOGGER.log(
            level=BOT_LOGGER.INFO,
            msg=f"Sent message to number {log_number}. {f'Failed. Reason: {err}' if was_error else 'Success'}",
            extra={
                BotLogModel.K_INITIATOR: "Bot",
                BotLogModel.K_ACTION_TYPE: "Send message",
            },
        )
