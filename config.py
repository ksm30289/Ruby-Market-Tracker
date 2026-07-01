import os
import json
from dotenv import load_dotenv

load_dotenv()


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value or not value.strip():
        raise RuntimeError(f"환경변수 누락: {name}")
    return value.strip()


SPREADSHEET_ID = required_env("SPREADSHEET_ID")
GOOGLE_SERVICE_ACCOUNT_JSON = required_env("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_CREDENTIALS = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)

SHEET_NAME = os.getenv("SHEET_NAME", "루비 시세 DB")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Seoul")

ITEMMANIA_URL = os.getenv(
    "ITEMMANIA_URL",
    "https://www.itemmania.com/sell/list.html?search_game=4817",
)

OPENTALK_TXT_PATH = os.getenv("OPENTALK_TXT_PATH", "./data/opentalk.txt")
