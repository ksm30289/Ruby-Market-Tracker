import gspread
from google.oauth2.service_account import Credentials

from config import (
    GOOGLE_CREDENTIALS,
    SPREADSHEET_ID,
    SHEET_NAME,
)


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_worksheet():
    credentials = Credentials.from_service_account_info(
        GOOGLE_CREDENTIALS,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    return spreadsheet.worksheet(SHEET_NAME)


def append_market_row(row):
    worksheet = get_worksheet()

    worksheet.append_row(
        row,
        value_input_option="USER_ENTERED",
    )

    print("[Sheets] 저장 완료")
