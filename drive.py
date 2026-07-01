import io

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from config import (
    SERVICE_ACCOUNT_INFO,
    KAKAO_FOLDER_ID,
)


SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_drive_service():
    creds = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES,
    )

    return build(
        "drive",
        "v3",
        credentials=creds,
    )


def list_txt_files():
    """
    구글 드라이브 폴더 내 txt 파일 목록 조회
    """

    service = get_drive_service()

    results = (
        service.files()
        .list(
            q=(
                f"'{KAKAO_FOLDER_ID}' in parents "
                "and trashed=false "
                "and mimeType='text/plain'"
            ),
            fields="files(id,name,modifiedTime)",
            orderBy="modifiedTime desc",
        )
        .execute()
    )

    return results.get("files", [])


def read_txt_file(file_id: str) -> str:
    """
    txt 파일 내용 읽기
    """

    service = get_drive_service()

    request = service.files().get_media(
        fileId=file_id
    )

    file_stream = io.BytesIO()

    downloader = MediaIoBaseDownload(
        file_stream,
        request,
    )

    done = False

    while not done:
        _, done = downloader.next_chunk()

    return (
        file_stream
        .getvalue()
        .decode("utf-8", errors="ignore")
    )


def get_latest_txt():
    """
    가장 최근 수정된 txt 파일 반환

    Returns
    -------
    {
        "id": "...",
        "name": "...",
        "modifiedTime": "...",
        "text": "..."
    }
    """

    files = list_txt_files()

    if not files:
        raise RuntimeError(
            "Google Drive에 txt 파일이 없습니다."
        )

    latest = files[0]

    print(
        f"[Drive] 최신 파일 : "
        f"{latest['name']}"
    )

    text = read_txt_file(
        latest["id"]
    )

    return {
        "id": latest["id"],
        "name": latest["name"],
        "modifiedTime": latest["modifiedTime"],
        "text": text,
    }
