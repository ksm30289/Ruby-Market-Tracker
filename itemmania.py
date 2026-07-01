import re
import requests
from bs4 import BeautifulSoup

from config import ITEMMANIA_URL


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


def parse_won(text: str):
    if not text:
        return None

    numbers = re.sub(r"[^0-9]", "", text)

    if not numbers:
        return None

    return int(numbers)


def get_itemmania_market():
    """
    아이템매니아 판매 목록에서 1,000 루비당 가격을 수집한다.

    반환:
    {
        "lowest": 17000,
        "average": 17300,
        "count": 42
    }
    """

    print("[Itemmania] 수집 시작")

    try:
        session = requests.Session()

        response = session.get(
            ITEMMANIA_URL,
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        items = soup.select("li.list_item, li.block_item")

        prices = []

        for item in items:
            trade_money = item.select_one(".trade_money")

            if not trade_money:
                continue

            # trade_money 내부 첫 텍스트가 17,000원
            raw_price = ""

            for content in trade_money.contents:
                if isinstance(content, str) and content.strip():
                    raw_price = content.strip()
                    break

            price = parse_won(raw_price)

            if price:
                prices.append(price)

        prices = sorted(prices)

        if not prices:
            print("[Itemmania] 가격 데이터 없음")
            return {
                "lowest": "",
                "average": "",
                "count": 0,
            }

        top10 = prices[:10]

        result = {
            "lowest": prices[0],
            "average": round(sum(top10) / len(top10)),
            "count": len(prices),
        }

        print(
            "[Itemmania] 완료 "
            f"최저={result['lowest']} / "
            f"평균={result['average']} / "
            f"매물수={result['count']}"
        )

        return result

    except Exception as e:
        print(f"[Itemmania] 수집 실패: {e}")

        return {
            "lowest": "",
            "average": "",
            "count": 0,
        }
