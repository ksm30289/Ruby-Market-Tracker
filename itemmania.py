import re
import time
import requests

from config import (
    ITEMMANIA_AVERAGE_TOP_N,
)

LIST_URL = "https://www.itemmania.com/sell/list.html?search_game=4817"

API_URL = "https://www.itemmania.com/sell/ajax_list.php"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Referer": LIST_URL,
    "Origin": "https://www.itemmania.com",
    "X-Requested-With": "XMLHttpRequest",
}

PAYLOAD = {
    "search_game": "4817",
    "search_server": "",
    "search_faction": "",
    "search_game_text": "언디셈버",
    "search_server_text": "",
    "search_goods": "all",
    "search_word": "",
    "search_type": "",
    "money_listOrder": "",
    "good_listOrder": "",
    "srch_item_depth1": "",
    "srch_item_depth2": "",
    "srch_item_depth3": "",
    "srch_item_depth4": "",
    "order": "2",
    "srch_char_alarm": "",
    "overlap": "",
    "goods_type": "1",
    "trade_state": "1",
    "credit_type": "1",
    "pinit": "1",
}

PRICE_PATTERN = re.compile(r"([\d,]+)원")


def parse_price(text):

    if not text:
        return None

    m = PRICE_PATTERN.search(text)

    if not m:
        return None

    return int(
        m.group(1).replace(",", "")
    )


def request_json():

    session = requests.Session()

    # 세션 쿠키 확보
    session.get(
        LIST_URL,
        headers=HEADERS,
        timeout=20,
    )

    response = session.post(
        API_URL,
        headers=HEADERS,
        data=PAYLOAD,
        timeout=20,
    )

    response.raise_for_status()

    return response.json()


def get_itemmania_market():

    print("=" * 60)
    print("[Itemmania] JSON 수집 시작")

    response_json = None

    for attempt in range(3):

        try:

            response_json = request_json()

            break

        except Exception as e:

            print(
                f"[Itemmania] 재시도 {attempt+1}/3 실패 : {e}"
            )

            time.sleep(2)

    if response_json is None:

        return {
            "lowest": "",
            "average": "",
            "count": 0,
            "total_quantity": 0,
            "prices": [],
        }

    if response_json.get("result") != "SUCCESS":

        print("[Itemmania] API 응답 실패")

        return {
            "lowest": "",
            "average": "",
            "count": 0,
            "total_quantity": 0,
            "prices": [],
        }

    data = response_json["data"]

    prices = []

    total_quantity = 0

    for item in data.get("g", []):

        # 게임머니만
        if item.get("trade_kind") != "3":
            continue

        # 판매중만
        if item.get("trade_state") != "a":
            continue

        price = parse_price(
            item.get("ea_trade_money", "")
        )

        if price is None:
            continue

        prices.append(price)

        try:
            total_quantity += int(
                item.get("trade_quantity", "0")
            )
        except:
            pass

    prices.sort()

    if not prices:

        print("[Itemmania] 판매중 매물 없음")

        return {
            "lowest": "",
            "average": "",
            "count": 0,
            "total_quantity": 0,
            "prices": [],
        }

    top = prices[:ITEMMANIA_AVERAGE_TOP_N]

    average = round(
        sum(top) / len(top)
    )

    result = {

        "lowest": prices[0],

        "average": average,

        "count": len(prices),

        "total_quantity": total_quantity,

        "prices": prices,

    }

    print()

    print(f"판매중 매물 : {result['count']}")
    print(f"최저가 : {result['lowest']:,}원")
    print(f"평균가 : {result['average']:,}원")
    print(f"총 공급량 : {result['total_quantity']:,}")

    print("=" * 60)

    return result


if __name__ == "__main__":

    result = get_itemmania_market()

    print()

    print(result)
