from datetime import datetime

import pytz

from config import (
    TIMEZONE,
    get_target_date,
)

from drive import get_latest_txt
from opentalk import get_opentalk_market
from sheets import save_market


def build_special_note(opentalk):

    notes = []

    if opentalk["count"] == 0:
        notes.append("오픈톡 시세 없음")

    return " / ".join(notes)


def main():

    print()
    print("=" * 70)
    print(" Ruby OpenTalk Tracker")
    print("=" * 70)
    print()

    timezone = pytz.timezone(TIMEZONE)

    now = datetime.now(timezone)

    target_date = get_target_date()

    print(f"분석 대상 날짜 : {target_date}")
    print()

    print("[1/3] Google Drive 최신 파일")

    latest = get_latest_txt()

    print(
        f"[Drive] {latest['name']}"
    )

    print()

    print("[2/3] 오픈톡 시세 분석")

    opentalk = get_opentalk_market(
        latest["text"],
        latest["name"],
    )

    print()

    print("[3/3] Google Sheets 저장")

    row = [

        # A 날짜
        target_date.strftime("%Y-%m-%d"),

        # B 수집시간
        now.strftime("%H:%M"),

        # C 아이템매니아 최저
        "",

        # D 아이템매니아 평균
        "",

        # E 아이템매니아 매물수
        "",

        # F 오픈톡 평균
        opentalk["average"],

        # G 오픈톡 최저
        opentalk["lowest"],

        # H 오픈톡 최고
        opentalk["highest"],

        # I 거래건수
        opentalk["count"],

        # J 비고
        "",

        # K 특이사항
        build_special_note(opentalk),

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
