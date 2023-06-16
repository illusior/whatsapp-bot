from apps.web.models import *
from logger.django_logger import BaseLogger

import logging
from django.utils.timezone import now


class DatabaseHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        log = BotLogModel.objects.create(
            datetime_record=now(),
            initiator=record.initiator,
            action_type=record.action_type,
            message=record.msg,
        )
        log.save()


class BotLogger(BaseLogger):
    pass


BOT_LOGGER_NAME = "BotLogger"
BOT_LOGGER = BotLogger(BOT_LOGGER_NAME)
BOT_LOGGER.addHandler(DatabaseHandler())

__all__ = ["BOT_LOGGER", "BotLogModel"]
