import os.path
from sys import exit
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import TransportError

import config
from loguru import logger


class Table:

    def __init__(self):
        self.SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
        self.SPREADSHEET_ID = "1zEL9X-8R4IZ04OKdXxcA5CaTr5w4BeyyLbBDbBPKW6A"
        self.credentials = self._get_credentials()
        self.service = build("sheets", "v4", credentials=self.credentials)
        self.list_name = config.data_sheets_list_name

    @staticmethod
    def save_credentials(creds):
        with open("access_files/token.json", "w") as token:
            token.write(creds.to_json())

    def _get_credentials(self) -> Credentials:
        creds = None

        if os.path.exists("access_files/token.json"):
            creds = Credentials.from_authorized_user_file("access_files/token.json", self.SCOPE)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except TransportError as ex:
                    logger.error("No internet connection.")
                    exit(1)
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "access_files/credentials.json", self.SCOPE)
                creds = flow.run_local_server(port=0)
            self.save_credentials(creds)

        return creds

    def read(self, range_sheets: list = None) -> any((list, HttpError, None)):
        """
        :param range_sheets: list, ex: ["A14:A17", "B14:B19"]
        """
        if not range_sheets:
            range_sheets = []

        range_sheets = list(map(lambda x: self.list_name + x, range_sheets))  # concatenate

        try:
            sheet = self.service.spreadsheets()

            result = sheet.values().batchGet(
                spreadsheetId=self.SPREADSHEET_ID, ranges=range_sheets).execute()
            values = result.get('valueRanges', [])

            if not values:
                logger.debug("No data found.")
                return []
            return values
        except HttpError as err:
            self.error_processing(err)

    def error_processing(self, err):
        if err.status_code == 429:
            logger.error("Requests limit exceeded")
            self.write("A26:A27",
                       [[f"Сообщение от {datetime.now() + timedelta(hours=3)}"[:-10]],
                        [f"Requests limit exceeded. Не все данные обновлены. Обратитесь к {config.responsible}"]])
        logger.info(err)

    def write(self, range_sheets: str, values: list) -> None:
        range_sheets = self.list_name + range_sheets
        if not values:
            values = []

        data = [{
            'range': range_sheets,
            'values': values
        }]

        body = {
            'valueInputOption': "USER_ENTERED",
            'data': data
        }

        try:
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.SPREADSHEET_ID, body=body).execute()
        except HttpError as err:
            logger.error(err)
