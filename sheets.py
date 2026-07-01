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
    OpenTalk 프로젝트

    수정 컬럼

    A 날짜
    B 수집시간
    F 오픈톡 평균
    G 오픈톡 최저
    H 오픈톡 최고
    I 거래건수
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

        # A 날짜
        worksheet.update_acell(
            f"B{target_row}",
            row[1],
        )

        # F~K만 수정
        worksheet.update(
            f"G{target_row}:L{target_row}",
            [[
                row[6],
                row[7],
                row[8],
                row[9],
                row[10],
                row[11],
            ]],
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
