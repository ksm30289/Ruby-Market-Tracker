import re

import requests
from bs4 import BeautifulSoup

from config import (
    ITEMMANIA_URL,
    ITEMMANIA_AVERAGE_TOP_N,
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,"
        "application/xhtml+xml,"
        "application/xml;q=0.9,"
        "image/avif,"
        "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer": "https://www.itemmania.com/",
}


def parse_price(text: str):

    if not text:
        return None

    numbers = re.sub(r"[^0-9]", "", text)

    if not numbers:
        return None

    return int(numbers)


def extract_trade_price(trade_money):

    if trade_money is None:
        return None

    for node in trade_money.contents:

        if isinstance(node, str):

            text = node.strip()

            if text:
                return parse_price(text)

    return parse_price(trade_money.get_text())


def get_itemmania_market():

    print("=" * 60)
    print("[Itemmania] 시세 수집 시작")

    session = requests.Session()

    try:

        response = session.get(
            ITEMMANIA_URL,
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

    except Exception as e:

        print(f"[Itemmania] 접속 실패 : {e}")

        return {
            "lowest": "",
            "average": "",
            "count": 0,
            "prices": [],
        }

    soup = BeautifulSoup(
        response.text,
        "lxml",
    )

    items = soup.select(
        "li.list_item, li.block_item"
    )

    prices = []

    for item in items:

        trade_money = item.select_one(
            ".trade_money"
        )

        if trade_money is None:
            continue

        price = extract_trade_price(
            trade_money
        )

        if price is None:
            continue

        prices.append(price)

    prices.sort()

    if not prices:

        print("[Itemmania] 가격을 찾지 못했습니다.")

        return {
            "lowest": "",
            "average": "",
            "count": 0,
            "prices": [],
        }

    top_prices = prices[:ITEMMANIA_AVERAGE_TOP_N]

    average = round(
        sum(top_prices)
        / len(top_prices)
    )

    print()

    print(f"매물수 : {len(prices)}")
    print(f"최저가 : {prices[0]:,}원")
    print(f"평균가 : {average:,}원")

    print("=" * 60)

    return {

        "lowest": prices[0],

        "average": average,

        "count": len(prices),

        "prices": prices,

    }


if __name__ == "__main__":

    result = get_itemmania_market()

    print(result)
