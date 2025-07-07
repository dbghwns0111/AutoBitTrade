# AutoBitTrade/strategy/auto_grid_trade.py
# 반복형 차수 매매 전략 (무한 반복 매수-매도 구조)
# 1차수 매수 체결 → 매도 체결 → 다시 1차수 매수 무한 반복 전략

import time
import math
from datetime import datetime
from api.api import place_order, get_order_detail
from config.tick_table import TICK_SIZE
from utils.telegram import send_telegram_message

# 가격 계산 함수: 퍼센트 또는 고정 금액으로 가격 조정
# mode: 'percent' 또는 'price'
def calculate_price(base_price, gap_value, mode, direction):
    if mode == 'percent':
        rate = (1 + gap_value / 100) if direction == 'up' else (1 - gap_value / 100)
        return round(base_price * rate, 2)
    elif mode == 'price':
        return round(base_price + gap_value, 2) if direction == 'up' else round(base_price - gap_value, 2)
    else:
        raise ValueError("mode는 'percent' 또는 'price' 여야 합니다.")

# 그리드 레벨 클래스: 각 차수의 매수/매도 가격과 수량을 관리
# 레벨(level), 매수 가격(buy_price), 매도 가격(sell_price),
class GridLevel:
    def __init__(self, level, buy_price, sell_price, volume):
        self.level = level
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.volume = volume
        self.buy_uuid = None
        self.sell_uuid = None
        self.buy_filled = False
        self.sell_filled = False

# 자동 매매 실행 함수: 시작 가격, 퍼센트 간격, KRW 금액, 최대 차수 설정
def run_auto_trade(start_price, percent_interval, krw_amount, max_levels, market_code='USDT', sleep_sec=5, stop_condition=None):
    market_code = market_code.upper()
    market = f"KRW-{market_code}"
    tick = TICK_SIZE.get(market)
    if tick is None:
        print(f"❌ 호가단위가 정의되지 않은 종목입니다: {market}")
        return

    levels = []
    for i in range(max_levels):
        rate = 1 - (percent_interval / 100) * i
        buy_price = math.floor(start_price * rate / tick) * tick
        sell_price = math.floor(buy_price * (1 + percent_interval / 100) / tick) * tick
        volume = round(krw_amount / buy_price, 8)
        levels.append(GridLevel(i + 1, buy_price, sell_price, volume))

    print(f"📊 자동 매매 시작: {max_levels}차까지 설정됨.")
    send_telegram_message(f"🚀 자동매매 시작: 최대 {max_levels}차, 간격 {percent_interval}%, 시작가 {start_price}원")

    # ✅ 전략 시작 시 1차 매수만 등록
    place_buy(levels[0], market)

    while True:
        if stop_condition and stop_condition():
            print("🛑 사용자 중단 감지됨. 종료합니다.")
            break

        for level in levels:
            # ✅ 매수 체결 감지
            if level.buy_uuid and not level.buy_filled:
                detail = get_order_detail(level.buy_uuid)
                data = detail.get('data') or detail
                executed = float(data.get('executed_volume', 0))
                remaining = float(data.get('remaining_volume', 0))
                if executed > 0 and remaining == 0:
                    level.buy_filled = True
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"✅ [{level.level}차] 매수 체결 완료: {level.buy_price}원")
                    send_telegram_message(
                        f"✅ <b>{market_code}</b> {level.level}차 매수 체결\n📉 가격: {level.buy_price}원\n📦 수량: {level.volume}\n🕒 {now}")
                    
                    # 📤 매도 주문
                    place_sell(level, market)

                    # 🛒 다음 차수 매수 주문
                    next_idx = level.level
                    if next_idx < len(levels):
                        place_buy(levels[next_idx], market)

            # ✅ 매도 체결 감지
            if level.sell_uuid and not level.sell_filled:
                detail = get_order_detail(level.sell_uuid)
                data = detail.get('data') or detail
                executed = float(data.get('executed_volume', 0))
                remaining = float(data.get('remaining_volume', 0))
                if executed > 0 and remaining == 0:
                    level.sell_filled = True
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"✅ [{level.level}차] 매도 체결 완료: {level.sell_price}원")
                    send_telegram_message(
                        f"✅ <b>{market_code}</b> {level.level}차 매도 체결\n📈 가격: {level.sell_price}원\n📦 수량: {level.volume}\n🕒 {now}")

                    # 🔁 반복 매매를 위해 초기화 후 다시 매수
                    level.buy_uuid = None
                    level.sell_uuid = None
                    level.buy_filled = False
                    level.sell_filled = False
                    place_buy(level, market)

        time.sleep(sleep_sec)

# 주문 등록 함수: 매수 또는 매도 주문을 API를 통해 실행
def place_buy(level, market):
    res = place_order(market, 'bid', level.volume, level.buy_price, 'limit')
    uuid = res.get('uuid') or res.get('data', {}).get('uuid')
    if uuid:
        level.buy_uuid = uuid
        print(f"🛒 [{level.level}차] 매수 주문 등록: {level.buy_price}원 / {level.volume}개")
        send_telegram_message(f"🛒 <b>{market}</b> {level.level}차 매수 주문 등록\n📉 {level.buy_price}원 / 📦 {level.volume}개")
    else:
        print(f"❌ 매수 주문 실패 [{level.level}차]: {res}")

def place_sell(level, market):
    res = place_order(market, 'ask', level.volume, level.sell_price, 'limit')
    uuid = res.get('uuid') or res.get('data', {}).get('uuid')
    if uuid:
        level.sell_uuid = uuid
        print(f"📤 [{level.level}차] 매도 주문 등록: {level.sell_price}원 / {level.volume}개")
        send_telegram_message(f"📤 <b>{market}</b> {level.level}차 매도 주문 등록\n📈 {level.sell_price}원 / {level.volume}개")
    else:
        print(f"❌ 매도 주문 실패 [{level.level}차]: {res}")
