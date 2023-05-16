from source.AbstractSource import AbstractUniqueSource

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from common.google.api import GoogleSheetsAuthData, make_credentials


class GoogleSheetSource(AbstractUniqueSource[str]):
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
            print(err)

    def set_range(self, range: str) -> None:
        result = (
            self.__ss_service.values()
            .get(spreadsheetId=self.__spreadsheet_id, range=range)
            .execute()
        )
        self.__values = result.get("values", [])
        self.__iter = iter(self.__values)
        self._reset()

    def __iter__(self):
        return self

    def __next__(self):
        result = next(self.__iter)[0]
        while self._has_value(result):
            result = next(self.__iter)[0]
        self._hold(result)

        return result


__all__ = ["GoogleSheetSource"]
