import gspread

from google.oauth2.service_account import Credentials

from config import GOOGLE_CREDENTIALS


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


credentials = Credentials.from_service_account_info(
    GOOGLE_CREDENTIALS,
    scopes=SCOPES
)

gc = gspread.authorize(credentials)
