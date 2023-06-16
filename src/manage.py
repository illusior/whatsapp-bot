#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from logger.django_logger import DJANGO_LOGGER


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        err = ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
        DJANGO_LOGGER.log(DJANGO_LOGGER.ERROR, err)
        raise err from exc

    DJANGO_LOGGER.log(
        DJANGO_LOGGER.INFO, f"Start manage.py with argv: {sys.argv}"
    )
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        DJANGO_LOGGER.log(DJANGO_LOGGER.ERROR, err)
