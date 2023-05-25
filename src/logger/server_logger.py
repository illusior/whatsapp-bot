import logging
import datetime

from config.settings import BASE_DIR, DEBUG


class BaseLogger(logging.Logger):
    __slots__ = ["_level", "DEBUG", "ERROR", "INFO", "WARN"]

    def __init__(self, name):
        self.DEBUG = logging.DEBUG
        self.ERROR = logging.ERROR
        self.INFO = logging.INFO
        self.WARN = logging.WARN

        self._level = logging.INFO

        super().__init__(name, self._level)


ROOT_LOGGER_NAME = __name__
SERVER_LOGGER = BaseLogger(ROOT_LOGGER_NAME)

FILE_HANDLER_NAME = (
    BASE_DIR
    / f"logs/server_{datetime.datetime.now().strftime('%Y.%m.%d_%H.%M.%S')}.log"
    if not DEBUG
    else BASE_DIR / "logs/server_log_debug.log"
)
ROOT_LOGGER_HANDLER = logging.FileHandler(FILE_HANDLER_NAME)
ROOT_LOGGER_FORMATTER = logging.Formatter(
    "%(asctime)s <%(levelname)s>: %(message)s. At %(pathname)s's line %(lineno)d",
    datefmt="[%Y-%m-%d|%H:%M:%S|%Z%z]",
)

ROOT_LOGGER_HANDLER.setFormatter(ROOT_LOGGER_FORMATTER)
SERVER_LOGGER.addHandler(ROOT_LOGGER_HANDLER)


__all__ = ["SERVER_LOGGER", "BaseLogger"]
