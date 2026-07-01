from datetime import datetime

import pytz

from config import TIMEZONE
from itemmania import get_itemmania_market
from opentalk import get_opentalk_market
from sheets import append_market_row


def build_special_note(itemmania, opentalk):
    notes = []

    if not itemmania.get("count"):
        notes.append("아이템매니아 수집 데이터 없음")

    if not opentalk.get("count"):
        notes.append("오픈톡 수집 데이터 없음")

    return " / ".join(notes)


def main():
    print("===== 루비 시세 수집 시작 =====")

    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)

    itemmania = get_itemmania_market()
    opentalk = get_opentalk_market()

    row = [
        now.strftime("%Y-%m-%d"),          # A 날짜
        now.strftime("%H:%M"),             # B 수집 시간
        itemmania.get("lowest", ""),       # C 아이템매니아 최저
        itemmania.get("average", ""),      # D 아이템매니아 평균
        itemmania.get("count", 0),         # E 아이템매니아 매물수
        opentalk.get("average", ""),       # F 오픈톡 평균
        opentalk.get("lowest", ""),        # G 오픈톡 최저
        opentalk.get("highest", ""),       # H 오픈톡 최고
        opentalk.get("count", 0),          # I 오픈톡 거래글수
        "",                                # J 비고
        build_special_note(itemmania, opentalk),  # K 특이사항
    ]

    print("[Row]", row)

    append_market_row(row)

    print("===== 루비 시세 수집 완료 =====")


if __name__ == "__main__":
    main()
