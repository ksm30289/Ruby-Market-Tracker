import gspread
from google.oauth2.service_account import Credentials

from config import (
    SERVICE_ACCOUNT_INFO,
    SPREADSHEET_ID,
    SHEET_NAME,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

_cached_worksheet = None


def get_worksheet():
    global _cached_worksheet

    if _cached_worksheet:
        return _cached_worksheet

    credentials = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(
        SPREADSHEET_ID
    )

    _cached_worksheet = spreadsheet.worksheet(
        SHEET_NAME
    )

    return _cached_worksheet


def find_date_row(worksheet, date_text):
    values = worksheet.col_values(1)

    for index, value in enumerate(values, start=1):
        if value == date_text:
            return index

    return None


def save_market(row):
    worksheet = get_worksheet()

    date_text = row[0]

    target_row = find_date_row(
        worksheet,
        date_text,
    )

    if target_row:
        # B 수집시간만 수정
        worksheet.update_acell(
            f"B{target_row}",
            row[1],
        )

        # G~L 오픈톡 영역만 수정
        worksheet.update(
            f"G{target_row}:L{target_row}",
            [[
                row[6],   # G 오픈톡 평균
                row[7],   # H 오픈톡 최저
                row[8],   # I 오픈톡 최고
                row[9],   # J 오픈톡 거래건수
                row[10],  # K 비고
                row[11],  # L 특이사항
            ]],
            value_input_option="USER_ENTERED",
        )

        print(f"[Sheets] {date_text} 업데이트 완료")

    else:
        worksheet.append_row(
            row,
            value_input_option="USER_ENTERED",
        )

        print(f"[Sheets] {date_text} 추가 완료")
