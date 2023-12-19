import os

from logger.django_logger import DJANGO_LOGGER

COMMANDS = [
    "manage.py collectstatic -c --noinput",
    "manage.py makemigrations",
    "manage.py makemigrations web",
    "manage.py migrate",
    "manage.py runserver 0.0.0.0:8080",
]


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    try:
        from django.core.management import ManagementUtility
    except ImportError:
        ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )

    for command in COMMANDS:
        utility = ManagementUtility(command.split())
        utility.execute()


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        DJANGO_LOGGER.log(DJANGO_LOGGER.ERROR, err)
