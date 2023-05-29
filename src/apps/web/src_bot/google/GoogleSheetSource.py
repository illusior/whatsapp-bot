from ..AbstractSource import AbstractSource
from ..common.google.api import GoogleApiServiceBuilder
from ..common.logging.logger import BOT_LOGGER, BotLogModel
from logger.server_logger import SERVER_LOGGER


class GoogleSheetSource(AbstractSource[str]):
    __slots__ = ["__ss_service", "__spreadsheet_id", "__values", "__iter"]

    def __init__(self, spreadsheet_id: str, range: str, api_version) -> None:
        super(GoogleSheetSource, self).__init__()
        try:
            service = GoogleApiServiceBuilder.from_oauth_2(
                service_name="sheets", api_version=api_version
            )
            self.__spreadsheet_id = spreadsheet_id
            self.__ss_service = service.spreadsheets()
            self.__iter = None
            self.set_range(range)

        except Exception as err:
            BOT_LOGGER.log(
                BOT_LOGGER.ERROR,
                f"""Unable to get data from Google's Spreadsheets.
                Unable to access table with'{self.__spreadsheet_id}' id.
                Possible solutions: change the Google account, choose another table, change the reading range.
                """,
                extra={
                    BotLogModel.K_INITIATOR: "Bot",
                    BotLogModel.K_ACTION_TYPE: "Build service",
                },
            )
            SERVER_LOGGER.log(SERVER_LOGGER.ERROR, err)

    def set_range(self, range: str) -> None:
        result = (
            self.__ss_service.values()
            .get(spreadsheetId=self.__spreadsheet_id, range=range)
            .execute()
        )
        self.__values = result.get("values", [])
        self.__iter = iter(self.__values)

    def __bool__(self):
        return self.__iter != None

    def __iter__(self):
        return self

    def __next__(self):
        result = next(self.__iter)
        result = result[0] if len(result) > 0 else ""

        return result


__all__ = ["GoogleSheetSource"]
