from datetime import datetime

import pytz

from config import TIMEZONE

from drive import get_latest_txt
from itemmania import get_itemmania_market
from opentalk import get_opentalk_market
from sheets import save_market


def build_special_note(itemmania, opentalk):

    notes = []

    if itemmania["count"] == 0:
        notes.append("아이템매니아 수집 실패")

    if opentalk["count"] == 0:
        notes.append("오픈톡 시세 없음")

    return " / ".join(notes)


def main():

    print()
    print("=" * 70)
    print(" Ruby Market Tracker")
    print("=" * 70)
    print()

    timezone = pytz.timezone(TIMEZONE)

    now = datetime.now(timezone)

    print("[1/4] 아이템매니아 수집")

    itemmania = get_itemmania_market()

    print()

    print("[2/4] Google Drive 최신 파일")

    latest = get_latest_txt()

    print(
        f"[Drive] {latest['name']}"
    )

    print()

    print("[3/4] 오픈톡 시세 분석")

    opentalk = get_opentalk_market(
        latest["text"],
        latest["name"],
    )

    print()

    print("[4/4] Google Sheets 저장")

    row = [

        # A
        now.strftime("%Y-%m-%d"),

        # B
        now.strftime("%H:%M"),

        # C
        itemmania["lowest"],

        # D
        itemmania["average"],

        # E
        itemmania["count"],

        # F
        opentalk["average"],

        # G
        opentalk["lowest"],

        # H
        opentalk["highest"],

        # I
        opentalk["count"],

        # J
        "",

        # K
        build_special_note(
            itemmania,
            opentalk,
        ),

    ]

    save_market(row)

    print()

    print("=" * 70)
    print(" 저장 완료")
    print("=" * 70)

    print()

    print("날짜 :", row[0])
    print("시간 :", row[1])

    print()

    print("■ Itemmania")
    print(f"최저 : {row[2]}")
    print(f"평균 : {row[3]}")
    print(f"매물 : {row[4]}")

    print()

    print("■ OpenTalk")
    print(f"평균 : {row[5]}")
    print(f"최저 : {row[6]}")
    print(f"최고 : {row[7]}")
    print(f"거래 : {row[8]}")

    print()

    if row[10]:

        print("특이사항")
        print(row[10])

    print()

    print("=" * 70)
    print(" 종료")
    print("=" * 70)


if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        print()

        print("=" * 70)
        print(" 실행 실패")
        print("=" * 70)

        print(e)

        raise
