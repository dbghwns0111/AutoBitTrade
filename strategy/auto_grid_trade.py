# AutoBitTrade/strategy/auto_grid_trade.py
# 반복형 차수 매매 전략 (무한 반복 매수-매도 구조)

import time
import math
import csv
import os
from datetime import datetime
from api.api import place_order, get_order_detail
from config.tick_table import TICK_SIZE
from utils.telegram import send_telegram_message

# 🔁 각 차수를 상태별로 추적하는 클래스
class ActiveLevel:
    def __init__(self, level, buy_price, sell_price, volume):
        self.level = level                      # 차수 번호 (1, 2, 3...)
        self.buy_price = buy_price              # 해당 차수 매수가
        self.sell_price = sell_price            # 해당 차수 매도가
        self.volume = volume                    # 매수/매도 수량
        self.buy_uuid = None                    # 매수 주문 UUID
        self.sell_uuid = None                   # 매도 주문 UUID
        self.state = 'idle'                     # 현재 상태: idle / buying / selling

# 🧠 전략 메인 실행 함수
def run_grid_trade(start_price, percent_interval, krw_amount, max_levels, market_code='USDT', sleep_sec=5, stop_condition=None):
    market_code = market_code.upper()
    market = f"KRW-{market_code}"
    tick = TICK_SIZE.get(market)

    if tick is None:
        print(f"❌ 호가단위가 정의되지 않은 종목입니다: {market}")
        return

    # 🎯 각 차수별 매수가/매도가/수량 초기 설정
    levels = []
    for i in range(max_levels):
        rate = 1 - (percent_interval / 100) * i
        buy_price = math.floor((start_price * rate) / tick) * tick
        sell_price = math.floor((buy_price * (1 + percent_interval / 100)) / tick) * tick
        volume = round(krw_amount / buy_price, 8)
        levels.append(ActiveLevel(i+1, buy_price, sell_price, volume))

    print(f"📊 총 {max_levels}개 레벨 설정 완료. 전략 시작.")

    # 🌀 전략 실행 루프
    while True:
        if stop_condition and stop_condition():
            print("🛑 중단 조건 감지됨. 전략 종료.")
            break

        for level in levels:

            # 1️⃣ 매수 주문 등록
            if level.state == 'idle':
                res = place_order(market, 'bid', level.volume, level.buy_price, 'limit')
                uuid = res.get('uuid') or res.get('data', {}).get('uuid')
                if uuid:
                    level.buy_uuid = uuid
                    level.state = 'buying'
                    print(f"🛒 [{level.level}]차 매수 주문 등록: {level.buy_price}원 / {level.volume}개")

            # 2️⃣ 매수 체결 확인
            if level.state == 'buying' and level.buy_uuid:
                detail = get_order_detail(level.buy_uuid)
                data = detail.get('data') or detail
                executed = float(data.get('executed_volume', 0))
                remaining = float(data.get('remaining_volume', 0))

                if executed > 0 and remaining == 0:
                    level.state = 'selling'
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"✅ [{level.level}]차 매수 체결 완료: {level.buy_price}원 🕒 {now}")
                    send_telegram_message(f"✅ <b>{market_code}</b> {level.level}차 매수 체결 {level.buy_price}원 / {level.volume}개 🕒 {now}")

                    # 3️⃣ 매도 주문 등록
                    res = place_order(market, 'ask', level.volume, level.sell_price, 'limit')
                    uuid = res.get('uuid') or res.get('data', {}).get('uuid')
                    if uuid:
                        level.sell_uuid = uuid
                        print(f"📤 [{level.level}]차 매도 예약: {level.sell_price}원")

            # 4️⃣ 매도 체결 확인
            if level.state == 'selling' and level.sell_uuid:
                detail = get_order_detail(level.sell_uuid)
                data = detail.get('data') or detail
                executed = float(data.get('executed_volume', 0))
                remaining = float(data.get('remaining_volume', 0))

                if executed > 0 and remaining == 0:
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"💰 [{level.level}]차 매도 체결 완료: {level.sell_price}원 🕒 {now}")
                    send_telegram_message(f"💰 <b>{market_code}</b> {level.level}차 매도 체결 {level.sell_price}원 / {level.volume}개 🕒 {now}")
                    # 상태 초기화 → 반복 진입 가능
                    level.buy_uuid = None
                    level.sell_uuid = None
                    level.state = 'idle'

        time.sleep(sleep_sec)
