import os.path
import config
from pprint import pprint
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from logger_file import logger


class Table:

    def __init__(self):
        self.SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
        self.SPREADSHEET_ID = "1zEL9X-8R4IZ04OKdXxcA5CaTr5w4BeyyLbBDbBPKW6A"
        self.credentials = self._refresh_token()
        self.service = build("sheets", "v4", credentials=self.credentials)
        self.list_name = config.data_sheets_list_name

    def _refresh_token(self) -> Credentials:
        creds = None

        if os.path.exists("access_files/token.json"):
            creds = Credentials.from_authorized_user_file("access_files/token.json", self.SCOPE)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "access_files/credentials.json", self.SCOPE)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("access_files/token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def read(self, range_sheets: list = None) -> list:
        """
        :param range_sheets: list ["A14:A17", "B14:B19"]
        :return: values (list)
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
            logger.info(err)

    def write(self, range_sheets: str, values: list):
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
            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.SPREADSHEET_ID, body=body).execute()
            # logger.debug(f"Values writed: {result}")
        except HttpError as err:
            logger.error(err)



# data = [{'range': 'Actual!F2:G2', 'majorDimension': 'ROWS', 'values': [['25.04-1.01.22']]}]
