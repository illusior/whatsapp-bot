import os

from logger.server_logger import SERVER_LOGGER

COMMANDS = [
    "manage.py collectstatic",
    "manage.py makemigrations",
    "manage.py makemigrations web",
    "manage.py migrate",
    "manage.py runserver 8080",
]


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_local")

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
        SERVER_LOGGER.log(SERVER_LOGGER.ERROR, err)
