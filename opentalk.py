import re
from datetime import datetime, timedelta

from config import (
    OPENTALK_DEDUPE_MINUTES,
    OPENTALK_MIN_PRICE,
    OPENTALK_MAX_PRICE,
    get_target_date,
)


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
    "루비",
    "삽니다",
    "팝니다",
    "판매",
    "구매",
    "매입",
    "정리",
    "ㅅ",
    "ㅍ",
]


def convert_hour(ampm: str, hour: int) -> int:
    if ampm == "오후" and hour != 12:
        return hour + 12

    if ampm == "오전" and hour == 12:
        return 0

    return hour


def is_trade_message(message: str) -> bool:
    if not message:
        return False

    text = message.strip()

    if "1:" in text or "1：" in text:
        return True

    return any(keyword in text for keyword in TRADE_KEYWORDS)


def extract_price(message: str):
    if not message:
        return None

    text = message.strip()

    for pattern in PRICE_PATTERNS:
        match = pattern.search(text)

        if not match:
            continue

        price = float(match.group(1))

        if OPENTALK_MIN_PRICE <= price <= OPENTALK_MAX_PRICE:
            return price

    return None


def parse_chat_line(line: str):
    line = line.strip()

    if not line:
        return None

    match = CHAT_PATTERN.match(line)

    if not match:
        return None

    year, month, day, ampm, hour, minute, speaker, message = match.groups()

    hour = convert_hour(
        ampm,
        int(hour),
    )

    dt = datetime(
        int(year),
        int(month),
        int(day),
        hour,
        int(minute),
    )

    return {
        "datetime": dt,
        "speaker": speaker.strip(),
        "message": message.strip(),
    }


def parse_opentalk_prices(text):

    target_date = get_target_date()

    rows = []

    total_messages = 0
    target_messages = 0

    if not text:
        return rows

    for line in text.splitlines():

        parsed = parse_chat_line(line)

        if not parsed:
            continue

        total_messages += 1

        if parsed["datetime"].date() != target_date:
            continue

        target_messages += 1

        message = parsed["message"]

        if not is_trade_message(message):
            continue

        price = extract_price(message)

        if price is None:
            continue

        rows.append({
            "datetime": parsed["datetime"],
            "speaker": parsed["speaker"],
            "message": message,
            "price": price,
        })

    print()
    print(f"대상 날짜 : {target_date}")
    print(f"전체 메시지 : {total_messages:,}")
    print(f"대상 날짜 메시지 : {target_messages:,}")
    print(f"거래글 : {len(rows):,}")

    return rows


def dedupe_prices(rows):
    rows = sorted(
        rows,
        key=lambda row: row["datetime"],
    )

    deduped = []
    last_seen = {}

    for row in rows:
        key = (
            row["speaker"],
            row["price"],
        )

        prev_dt = last_seen.get(key)

        if (
            prev_dt
            and row["datetime"] - prev_dt <= timedelta(
                minutes=OPENTALK_DEDUPE_MINUTES
            )
        ):
            continue

        deduped.append(row)
        last_seen[key] = row["datetime"]

    return deduped


def get_opentalk_market(text: str, filename: str = ""):
    print("=" * 60)
    print("[OpenTalk] 시세 분석 시작")

    if filename:
        print(f"[OpenTalk] 파일명 : {filename}")

    try:
        rows = parse_opentalk_prices(text)
        rows = dedupe_prices(rows)

        prices = [
            row["price"]
            for row in rows
        ]

        if not prices:
            print("[OpenTalk] 시세 데이터 없음")

            return {
                "average": "",
                "lowest": "",
                "highest": "",
                "count": 0,
                "rows": [],
            }

        result = {
            "average": round(sum(prices) / len(prices), 2),
            "lowest": min(prices),
            "highest": max(prices),
            "count": len(prices),
            "rows": rows,
        }

        print(f"거래글수 : {result['count']}")
        print(f"평균 : {result['average']}")
        print(f"최저 : {result['lowest']}")
        print(f"최고 : {result['highest']}")
        print("=" * 60)

        return result

    except Exception as e:
        print(f"[OpenTalk] 분석 실패 : {e}")

        return {
            "average": "",
            "lowest": "",
            "highest": "",
            "count": 0,
            "rows": [],
        }
