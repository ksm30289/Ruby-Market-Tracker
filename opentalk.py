import re
from datetime import datetime, timedelta

from config import (
    OPENTALK_DEDUPE_MINUTES,
    OPENTALK_MIN_PRICE,
    OPENTALK_MAX_PRICE,
)


CHAT_PATTERN = re.compile(
    r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.\s*"
    r"(오전|오후)?\s*(\d{1,2}):(\d{2}),\s*"
    r"(.*?)\s*:\s*(.*)"
)

# 입장/퇴장 등 사용자 메시지가 아닌 시스템 로그
SYSTEM_PATTERN = re.compile(
    r"^\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.\s*"
    r"(?:오전|오후)?\s*\d{1,2}:\d{2}:"
)

DATE_HEADER_PATTERN = re.compile(
    r"^\d{4}년\s*\d{1,2}월\s*\d{1,2}일"
)

DIRECT_PRICE_PATTERNS = [
    # 1:15 / 1：15 / 1대15
    re.compile(
        r"(?<!\d)1\s*[:：대]\s*(\d{1,2}(?:\.\d+)?)(?!\d)"
    ),

    # 15:1 / 15：1 / 15대1
    re.compile(
        r"(?<!\d)(\d{1,2}(?:\.\d+)?)\s*[:：대]\s*1(?!\d)"
    ),

    # 15원
    re.compile(
        r"(?<!\d)(\d{1,2}(?:\.\d+)?)\s*원(?!\d)"
    ),
]

# "1만룹 15만", "7627루비 11만원" 계산용
QUANTITY_PATTERN = re.compile(
    r"(\d[\d,]*(?:\.\d+)?)\s*(만|천)?\s*"
    r"(?:루비|룹)"
)

TOTAL_MONEY_PATTERN = re.compile(
    r"(\d[\d,]*(?:\.\d+)?)\s*(만|천)?\s*원"
)

# "무료 1만룹 팔아요~ 16" 같은 마지막 단독 가격
TRAILING_PRICE_PATTERN = re.compile(
    r"(?:팝니다|팔아요|판매|삽니다|구매|매입)"
    r"[^\d]{0,15}"
    r"(\d{1,2}(?:\.\d+)?)\s*$"
)

TRADE_KEYWORDS = [
    "루비",
    "룹",
    "삽니다",
    "팝니다",
    "팔아요",
    "판매",
    "구매",
    "매입",
    "정리",
]

IGNORE_MESSAGES = {
    "메시지가 삭제되었습니다.",
}


def convert_hour(ampm: str, hour: int) -> int:
    if ampm == "오후" and hour != 12:
        return hour + 12

    if ampm == "오전" and hour == 12:
        return 0

    return hour


def parse_number(number_text: str, unit: str = ""):
    """
    1만     -> 10000
    15만    -> 150000
    7,627   -> 7627
    2.4만   -> 24000
    """

    try:
        value = float(
            number_text.replace(",", "")
        )
    except (TypeError, ValueError):
        return None

    if unit == "만":
        value *= 10000

    elif unit == "천":
        value *= 1000

    return value


def is_valid_price(price) -> bool:
    if price is None:
        return False

    return (
        OPENTALK_MIN_PRICE
        <= price
        <= OPENTALK_MAX_PRICE
    )


def is_trade_message(message: str) -> bool:
    if not message:
        return False

    text = message.strip()

    if not text:
        return False

    # 비율 표기가 있으면 거래글 후보
    if re.search(
        r"(?<!\d)\d{1,2}(?:\.\d+)?"
        r"\s*[:：대]\s*"
        r"\d{1,2}(?:\.\d+)?(?!\d)",
        text,
    ):
        return True

    return any(
        keyword in text
        for keyword in TRADE_KEYWORDS
    )


def extract_direct_price(text: str):
    for pattern in DIRECT_PRICE_PATTERNS:
        match = pattern.search(text)

        if not match:
            continue

        price = float(match.group(1))

        if is_valid_price(price):
            return price

    return None


def extract_calculated_price(text: str):
    """
    다음 형태를 계산한다.

    1만룹 15만 팝니다
    → 150000 / 10000 = 15

    무료 7627루비 11만원
    → 110000 / 7627 = 14.42
    """

    quantity_match = QUANTITY_PATTERN.search(text)
    money_match = TOTAL_MONEY_PATTERN.search(text)

    if not quantity_match or not money_match:
        return None

    quantity = parse_number(
        quantity_match.group(1),
        quantity_match.group(2) or "",
    )

    total_money = parse_number(
        money_match.group(1),
        money_match.group(2) or "",
    )

    if not quantity or not total_money:
        return None

    if quantity <= 0:
        return None

    price = total_money / quantity

    if not is_valid_price(price):
        return None

    return round(price, 2)


def extract_trailing_price(text: str):
    """
    무료 1만룹 팔아요~ 16
    """

    if not re.search(
        r"(?:루비|룹)",
        text,
    ):
        return None

    match = TRAILING_PRICE_PATTERN.search(text)

    if not match:
        return None

    price = float(match.group(1))

    if is_valid_price(price):
        return price

    return None


def extract_price(message: str):
    if not message:
        return None

    text = " ".join(
        message.split()
    )

    # 1순위: 1:15 / 15:1 / 1대15 등
    price = extract_direct_price(text)

    if price is not None:
        return price

    # 2순위: 루비 수량과 총 금액으로 계산
    price = extract_calculated_price(text)

    if price is not None:
        return price

    # 3순위: 문장 마지막의 단독 숫자
    return extract_trailing_price(text)


def parse_chat_line(line: str):
    line = line.strip()

    if not line:
        return None

    match = CHAT_PATTERN.match(line)

    if not match:
        return None

    (
        year,
        month,
        day,
        ampm,
        hour,
        minute,
        speaker,
        message,
    ) = match.groups()

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


def parse_chat_messages(text: str):
    """
    카카오톡 내보내기에서 여러 줄 메시지를 하나로 결합한다.

    예:
    2026. 7. 16. 19:37, 코맹맹 : 15000 무료루비 시즌/스탠
    14:1 팝니다

    위 두 줄을 하나의 메시지로 처리한다.
    """

    messages = []
    current = None

    if not text:
        return messages

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        parsed = parse_chat_line(line)

        if parsed:
            if current:
                messages.append(current)

            current = parsed
            continue

        # 날짜 제목, 입퇴장 로그, 삭제 안내는 이어 붙이지 않는다.
        if (
            DATE_HEADER_PATTERN.match(line)
            or SYSTEM_PATTERN.match(line)
            or line in IGNORE_MESSAGES
            or line.startswith("Talk_")
            or line.startswith("저장한 날짜")
        ):
            if current:
                messages.append(current)
                current = None

            continue

        # 타임스탬프가 없는 줄은 직전 메시지의 연속 내용
        if current:
            current["message"] += "\n" + line

    if current:
        messages.append(current)

    return messages


def parse_opentalk_prices(text: str):
    rows = []

    messages = parse_chat_messages(text)

    for parsed in messages:
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
    print("=" * 60)
    print("[OpenTalk] 메시지 분석")
    print("=" * 60)
    print(f"전체 메시지 : {len(messages):,}")
    print(f"가격 인식 거래글 : {len(rows):,}")

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
            and row["datetime"] - prev_dt
            <= timedelta(
                minutes=OPENTALK_DEDUPE_MINUTES
            )
        ):
            continue

        deduped.append(row)
        last_seen[key] = row["datetime"]

    return deduped


def get_opentalk_markets(
    text: str,
    filename: str = "",
):
    print("=" * 60)
    print("[OpenTalk] 시세 분석 시작")

    if filename:
        print(f"[OpenTalk] 파일명 : {filename}")

    try:
        rows = parse_opentalk_prices(text)

        before_count = len(rows)

        rows = dedupe_prices(rows)

        print(f"중복 제거 전 : {before_count}")
        print(f"중복 제거 후 : {len(rows)}")

        daily = {}

        for row in rows:
            date_text = row["datetime"].strftime(
                "%Y-%m-%d"
            )

            daily.setdefault(
                date_text,
                [],
            ).append(row)

        result = {}

        print()

        for date_text in sorted(daily):
            date_rows = daily[date_text]

            prices = [
                row["price"]
                for row in date_rows
            ]

            result[date_text] = {
                "average": round(
                    sum(prices) / len(prices),
                    2,
                ),
                "lowest": min(prices),
                "highest": max(prices),
                "count": len(prices),
                "rows": date_rows,
            }

            print(
                f"{date_text} "
                f"평균:{result[date_text]['average']} "
                f"최저:{result[date_text]['lowest']} "
                f"최고:{result[date_text]['highest']} "
                f"거래:{result[date_text]['count']}"
            )

        return result

    except Exception as e:
        print(f"[OpenTalk] 분석 실패 : {e}")
        return {}


# 기존 main.py가 단수형을 사용해도 동작하도록 호환
def get_opentalk_market(
    text: str,
    filename: str = "",
):
    return get_opentalk_markets(
        text,
        filename,
    )
