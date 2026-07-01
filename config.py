import os
import json


def required_env(name: str) -> str:
    value = os.getenv(name)

    if not value or not value.strip():
        raise RuntimeError(f"환경변수 누락: {name}")

    return value.strip()


from datetime import datetime

TARGET_DATE = os.getenv("TARGET_DATE", "").strip()


def get_target_date():

    if TARGET_DATE:

        return datetime.strptime(
            TARGET_DATE,
            "%Y-%m-%d",
        ).date()

    return datetime.now().date()

SPREADSHEET_ID = required_env("SPREADSHEET_ID")

KAKAO_FOLDER_ID = required_env("KAKAO_FOLDER_ID")

GOOGLE_SERVICE_ACCOUNT_JSON = required_env("GOOGLE_SERVICE_ACCOUNT_JSON")

SERVICE_ACCOUNT_INFO = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)


SHEET_NAME = os.getenv(
    "SHEET_NAME",
    "루비 시세 DB",
)

TIMEZONE = os.getenv(
    "TIMEZONE",
    "Asia/Seoul",
)

ITEMMANIA_URL = os.getenv(
    "ITEMMANIA_URL",
    "https://www.itemmania.com/sell/list.html?search_game=4817",
)


# 아이템매니아 평균 계산 기준
ITEMMANIA_AVERAGE_TOP_N = int(
    os.getenv("ITEMMANIA_AVERAGE_TOP_N", "10")
)


# 오픈톡 중복 제거 기준: 같은 유저 + 같은 가격 + N분 이내
OPENTALK_DEDUPE_MINUTES = int(
    os.getenv("OPENTALK_DEDUPE_MINUTES", "30")
)


# 오픈톡 시세 이상치 제외 범위
OPENTALK_MIN_PRICE = float(
    os.getenv("OPENTALK_MIN_PRICE", "5")
)

OPENTALK_MAX_PRICE = float(
    os.getenv("OPENTALK_MAX_PRICE", "50")
)
