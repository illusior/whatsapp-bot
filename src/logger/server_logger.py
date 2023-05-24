import logging


ROOT_LOGGER_NAME = __name__
ROOT_LOGGER = logging.getLogger(ROOT_LOGGER_NAME)
ROOT_LOGGER.setLevel(logging.NOTSET)

ROOT_LOGGER_HANDLER = logging.FileHandler("server.log")
ROOT_LOGGER_FORMATTER = logging.Formatter("%(created)s %(pathname)s %(message)s")

ROOT_LOGGER_HANDLER.setFormatter(ROOT_LOGGER_FORMATTER)
ROOT_LOGGER.addHandler(ROOT_LOGGER_HANDLER)


__all__ = ["ROOT_LOGGER"]
