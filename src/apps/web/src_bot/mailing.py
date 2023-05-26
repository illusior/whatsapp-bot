import os

from ..forms import BotSettingsForm
from .common.green_api import *
from .common.logging.logger import *
from .common.messages import *
from .common.validators.PhoneValidator import *
from .google.GoogleSheetSource import GoogleSheetSource
from logger.server_logger import SERVER_LOGGER

from .AbstractSource import (
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
        NotEmptySourceDecorator(
            GoogleSheetSource(
                id_google_sheet,
                range=f"{id_data_column_google_sheet}:{id_data_column_google_sheet}",
                api_version="v4",
            )
        )
    )

    if not google_spreadsheets:
        err_msg = f"Unable to access spreadsheet with `{id_google_sheet}` id. Make sure you have access to it"
        BOT_LOGGER.log(
            level=BOT_LOGGER.INFO,
            msg=err_msg,
            extra={
                BotLogModel.K_INITIATOR: "Bot",
                BotLogModel.K_ACTION_TYPE: "Access Google's Spreadsheets",
            },
        )
        SERVER_LOGGER.log(
            level=SERVER_LOGGER.ERROR,
            msg=err_msg
        )
        raise RuntimeError(err_msg)

    for phone_number in google_spreadsheets:
        was_error = False
        err = None

        try:
            phone_number = validate_phone(phone_number)
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

        if was_error:
            SERVER_LOGGER.log(
                SERVER_LOGGER.ERROR,
                f"'Failed to send message to {log_number}. 'Reason: {err}",
            )
        else:
            SERVER_LOGGER.log(
                SERVER_LOGGER.INFO,
                f"Send message to {log_number}",
            )
