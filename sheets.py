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


def get_worksheet():

    credentials = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(
        SPREADSHEET_ID
    )

    return spreadsheet.worksheet(
        SHEET_NAME
    )


def find_date_row(worksheet, date_text):

    values = worksheet.col_values(1)

    for index, value in enumerate(values, start=1):

        if value == date_text:
            return index

    return None


def save_market(row):

    """
    row

    A 날짜
    B 수집시간
    C 아이템매니아 최저
    D 아이템매니아 평균
    E 아이템매니아 매물수
    F 오픈톡 평균
    G 오픈톡 최저
    H 오픈톡 최고
    I 오픈톡 거래글수
    J 비고
    K 특이사항
    """

    worksheet = get_worksheet()

    date_text = row[0]

    target_row = find_date_row(
        worksheet,
        date_text,
    )

    if target_row:

        worksheet.update(
            f"A{target_row}:K{target_row}",
            [row],
            value_input_option="USER_ENTERED",
        )

        print(
            f"[Sheets] {date_text} 업데이트 완료"
        )

    else:

        worksheet.append_row(
            row,
            value_input_option="USER_ENTERED",
        )

        print(
            f"[Sheets] {date_text} 추가 완료"
        )
