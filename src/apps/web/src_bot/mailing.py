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


def generalMailing(post_data) -> None:
    wa = GreenApi(
        idInstance=os.environ.get("GREEN_API_ID_INSTANCE"),
        apiTokenInstance=os.environ.get("GREEN_API_TOKEN"),
    )

    to_send_message = post_data[K_TO_SEND_MESSAGE]
    id_data_column_google_sheet = post_data[K_ID_DATA_COLUMN_GOOGLE_SHEET]
    id_google_sheet = post_data[K_ID_GOOGLE_SHEET]

    google = UniqueSourceDecorator(
        NotEmptySourceDecorator(
            GoogleSheetSource(
                id_google_sheet,
                range=f"{id_data_column_google_sheet}:{id_data_column_google_sheet}",
                api_version="v4",
            )
        )
    )

    for phone_number in google:
        was_error = False
        err = None
        try:
            phone_number = validate_phone(phone_number)
            chatId = f"{phone_number}{CHAT_ID_MOBILE_DOMAIN}"
            wa.sending.sendMessage(chatId=chatId, message=to_send_message)
        except Exception as err_excpt:
            was_error = True
            SERVER_LOGGER.log(SERVER_LOGGER.ERROR, err_excpt)
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

        if not was_error:
            SERVER_LOGGER.log(
                SERVER_LOGGER.INFO, f"Send message to {log_number}"
            )
