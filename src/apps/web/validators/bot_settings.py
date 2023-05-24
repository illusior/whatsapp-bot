import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _


class ValidationWarn(ValidationError):
    pass


def validate_message_to_send(msg: str) -> None:
    if len(msg) == 0:
        raise ValidationWarn(
            _("Сообщение останется прежним"), code="err_empty_msg"
        )


SPREADSHEET_ID_REGEX = "[-\w]{25,}"


class GoogleSheets_URL_ID_Validator(URLValidator):
    def __call__(self, value):
        try:
            super().__call__(value)
        except ValidationError as err:
            match = re.search(SPREADSHEET_ID_REGEX, value)
            if not match:
                raise err


def validate_google_spreadsheet_url_as_id(url: str) -> None:
    if len(url) == 0:
        raise ValidationWarn(
            _("Ссылка на Google SpreadSheet's останется прежней"),
            code="err_empty_google_ss_url_as_id",
        )

    validate_url = GoogleSheets_URL_ID_Validator()
    try:
        validate_url(url)
    except ValidationError:
        raise ValidationError(
            _(
                "Ссылка на Google SpreadSheet's не является ни ссылкой, ни ID таблицы"
            ),
            code="err_google_ss_column_index_not_url_or_id",
        )


def validate_google_spreadsheet_column_index(index: str) -> None:
    if len(index) == 0:
        raise ValidationWarn(
            _("Имя колонки с номерами в Google-таблице останется прежним"),
            code="err_empty_google_ss_column_index",
        )
    if not index.isalpha():
        raise ValidationError(
            _(
                "Имя колонки с номерами в Google-таблице не является набором букв"
            ),
            code="err_google_ss_column_index_not_alpha",
        )
