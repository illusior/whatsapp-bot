from apps.web.models import *

import datetime
import logging


class DatabaseHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        # super().emit(record)
        log = BotLogModel.objects.create(
            datetime_record=datetime.datetime.now(),
            initiator=record.initiator,
            action_type=record.action_type,
            message=record.msg,
        )
        log.save()


BOT_LOGGER_NAME = "BotLogger"
BOT_LOGGER = logging.getLogger(BOT_LOGGER_NAME)
BOT_LOGGER.setLevel(logging.INFO)
BOT_LOGGER.addHandler(DatabaseHandler())

__all__ = ["BOT_LOGGER"]
