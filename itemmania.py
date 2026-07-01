import re
import requests

from config import (
    ITEMMANIA_AVERAGE_TOP_N,
)


URL = "https://www.itemmania.com/sell/ajax_list.php"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.itemmania.com/sell/list.html?search_game=4817",
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


PRICE_PATTERN = re.compile(
    r"([\d,]+)원"
)


def parse_price(text):

    if not text:
        return None

    match = PRICE_PATTERN.search(text)

    if not match:
        return None

    return int(
        match.group(1)
        .replace(",", "")
    )


def get_itemmania_market():

    print("=" * 60)
    print("[Itemmania] JSON 수집 시작")

    try:

        response = requests.post(
            URL,
            headers=HEADERS,
            data=PAYLOAD,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

    except Exception as e:

        print(f"[Itemmania] API 호출 실패 : {e}")

        return {
            "lowest": "",
            "average": "",
            "count": 0,
            "total_quantity": 0,
            "prices": [],
        }

    prices = []

    total_quantity = 0

    trade_count = 0

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

        trade_count += 1

    prices.sort()

    if not prices:

        print("[Itemmania] 판매중 매물이 없습니다.")

        return {
            "lowest": "",
            "average": "",
            "count": 0,
            "total_quantity": 0,
            "prices": [],
        }

    top_prices = prices[:ITEMMANIA_AVERAGE_TOP_N]

    average = round(
        sum(top_prices)
        / len(top_prices)
    )

    result = {

        "lowest": prices[0],

        "average": average,

        "count": trade_count,

        "total_quantity": total_quantity,

        "prices": prices,

    }

    print()

    print(f"판매중 매물 : {trade_count}")
    print(f"최저가 : {result['lowest']:,}원")
    print(f"평균가 : {result['average']:,}원")
    print(f"총 공급량 : {total_quantity:,}")

    print("=" * 60)

    return result


if __name__ == "__main__":

    result = get_itemmania_market()

    print()

    print(result)
