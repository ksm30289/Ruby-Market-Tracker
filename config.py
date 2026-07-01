import os
import json

from dotenv import load_dotenv

load_dotenv()


def required_env(name: str):
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"환경변수 누락 : {name}")

    return value


SPREADSHEET_ID = required_env("SPREADSHEET_ID")

GOOGLE_CREDENTIALS = json.loads(
    required_env("GOOGLE_SERVICE_ACCOUNT_JSON")
)

SHEET_NAME = "루비 시세 DB"
