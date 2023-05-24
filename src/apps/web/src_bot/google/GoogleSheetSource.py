from ..common.google.api import GoogleSheetsAuthData, make_credentials
from ..AbstractSource import AbstractSource

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..common.logging.logger import BOT_LOGGER
from logger.server_logger import ROOT_LOGGER

class GoogleSheetSource(AbstractSource[str]):
    __slots__ = ["__ss_service", "__spreadsheet_id", "__values", "__iter"]

    def __init__(
        self, auth_data: GoogleSheetsAuthData, spreadsheet_id: str, range: str
    ) -> None:
        super(GoogleSheetSource, self).__init__()
        try:
            service = build(
                "sheets", "v4", credentials=make_credentials(auth_data)
            )
            self.__spreadsheet_id = spreadsheet_id
            self.__ss_service = service.spreadsheets()
            self.__iter = None
            self.set_range(range)

        except HttpError as err:
            ROOT_LOGGER.error(err)
            # BOT_LOGGER.write_log()

    def set_range(self, range: str) -> None:
        result = (
            self.__ss_service.values()
            .get(spreadsheetId=self.__spreadsheet_id, range=range)
            .execute()
        )
        self.__values = result.get("values", [])
        self.__iter = iter(self.__values)

    def __iter__(self):
        return self

    def __next__(self):
        result = next(self.__iter)
        result = result[0] if len(result) > 0 else ""

        return result


__all__ = ["GoogleSheetSource"]
