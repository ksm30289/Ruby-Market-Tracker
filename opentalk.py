import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

from config import OPENTALK_TXT_PATH


CHAT_PATTERN = re.compile(
    r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.\s*"
    r"(오전|오후)?\s*(\d{1,2}):(\d{2}),\s*"
    r"(.*?)\s*:\s*(.*)"
)

PRICE_PATTERNS = [
    re.compile(r"\b1\s*[:：]\s*(\d{1,2}(?:\.\d+)?)\b"),
    re.compile(r"\b(\d{1,2}(?:\.\d+)?)\s*원\b"),
]

TRADE_KEYWORDS = [
    "삽니다",
    "팝니다",
    "판매",
    "구매",
    "매입",
    "정리",
    "루비",
    "ㅅ",
    "ㅍ",
]


def convert_hour(ampm: str, hour: int) -> int:
    if ampm == "오후" and hour != 12:
        return hour + 12

    if ampm == "오전" and hour == 12:
        return 0

    return hour


def extract_price(message: str):
    text = message.strip()

    for pattern in PRICE_PATTERNS:
        match = pattern.search(text)

        if not match:
            continue

        price = float(match.group(1))

        # 루비 시세 기준 이상치 방지
        if 5 <= price <= 50:
            return price

    return None


def is_trade_message(message: str) -> bool:
    if "1:" in message or "1：" in message:
        return True

    return any(keyword in message for keyword in TRADE_KEYWORDS)


def read_text_file(path: str) -> str:
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]

    for encoding in encodings:
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def parse_opentalk_prices(path: str):
    if not os.path.exists(path):
        print(f"[OpenTalk] 파일 없음: {path}")
        return []

    text = read_text_file(path)

    rows = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        match = CHAT_PATTERN.match(line)

        if not match:
            continue

        year, month, day, ampm, hour, minute, speaker, message = match.groups()

        hour = convert_hour(ampm, int(hour))

        dt = datetime(
            int(year),
            int(month),
            int(day),
            hour,
            int(minute),
        )

        if not is_trade_message(message):
            continue

        price = extract_price(message)

        if price is None:
            continue

        rows.append(
            {
                "datetime": dt,
                "speaker": speaker.strip(),
                "message": message.strip(),
                "price": price,
            }
        )

    return rows


def dedupe_prices(rows, minutes: int = 30):
    """
    같은 유저 + 같은 가격 + 30분 이내 반복 광고는 1건으로 처리.
    """

    rows = sorted(rows, key=lambda x: x["datetime"])

    last_seen = {}

    deduped = []

    for row in rows:
        key = (
            row["speaker"],
            row["price"],
        )

        prev_dt = last_seen.get(key)

        if prev_dt and row["datetime"] - prev_dt <= timedelta(minutes=minutes):
            continue

        deduped.append(row)
        last_seen[key] = row["datetime"]

    return deduped


def get_opentalk_market():
    """
    카카오톡 오픈톡 txt에서 루비 거래 시세를 추출한다.

    반환:
    {
        "average": 17.2,
        "lowest": 17.0,
        "highest": 17.5,
        "count": 58
    }
    """

    print("[OpenTalk] 수집 시작")

    try:
        rows = parse_opentalk_prices(OPENTALK_TXT_PATH)
        rows = dedupe_prices(rows)

        prices = [row["price"] for row in rows]

        if not prices:
            print("[OpenTalk] 시세 데이터 없음")
            return {
                "average": "",
                "lowest": "",
                "highest": "",
                "count": 0,
            }

        result = {
            "average": round(sum(prices) / len(prices), 2),
            "lowest": min(prices),
            "highest": max(prices),
            "count": len(prices),
        }

        print(
            "[OpenTalk] 완료 "
            f"평균={result['average']} / "
            f"최저={result['lowest']} / "
            f"최고={result['highest']} / "
            f"거래글수={result['count']}"
        )

        return result

    except Exception as e:
        print(f"[OpenTalk] 수집 실패: {e}")

        return {
            "average": "",
            "lowest": "",
            "highest": "",
            "count": 0,
        }
