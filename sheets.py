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

    C 아이템매니아 평균
    D 아이템매니아 최고
    E 아이템매니아 최저
    F 아이템매니아 매물수

    G 오픈톡 평균
    H 오픈톡 최저
    I 오픈톡 최고
    J 거래건수

    K 비고
    L 특이사항
    """

    worksheet = get_worksheet()

    date_text = row[0]

    target_row = find_date_row(
        worksheet,
        date_text,
    )

    if target_row:

        # B~L만 수정
        worksheet.update(
            f"B{target_row}:L{target_row}",
            [[
                row[1],   # B
                row[2],   # C
                row[3],   # D
                row[4],   # E
                row[5],   # F
                row[6],   # G
                row[7],   # H
                row[8],   # I
                row[9],   # J
                row[10],  # K
                row[11],  # L
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
