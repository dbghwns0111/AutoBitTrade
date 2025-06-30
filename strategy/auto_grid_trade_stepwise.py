# AutoBitTrade/strategy/auto_grid_trade_stepwise.py
# 단계별 1차수씩만 순차적으로 매수하는 반복 전략

import time
import math
from datetime import datetime
from api.api import place_order, get_order_detail
from config.tick_table import TICK_SIZE
from utils.telegram import send_telegram_message


class ActiveLevel:
    def __init__(self, level, buy_price, sell_price, volume):
        self.level = level
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.volume = volume
        self.buy_uuid = None
        self.sell_uuid = None


def run_grid_trade_stepwise(start_price, percent_interval, krw_amount, max_levels, market_code='USDT', sleep_sec=5, stop_condition=None):
    market_code = market_code.upper()
    market = f"KRW-{market_code}"
    tick = TICK_SIZE.get(market)

    if tick is None:
        print(f"❌ 호가단위가 정의되지 않은 종목입니다: {market}")
        return

    print(f"📊 최대 {max_levels}개 차수를 순차 실행합니다.")
    current_level = 1

    while current_level <= max_levels:
        if stop_condition and stop_condition():
            print("🛑 전략 중단됨.")
            break

        rate = 1 - (percent_interval / 100) * (current_level - 1)
        buy_price = math.floor((start_price * rate) / tick) * tick
        sell_price = math.floor((buy_price * (1 + percent_interval / 100)) / tick) * tick
        volume = round(krw_amount / buy_price, 8)

        level = ActiveLevel(current_level, buy_price, sell_price, volume)

        # 🛒 매수 주문
        res = place_order(market, 'bid', level.volume, level.buy_price, 'limit')
        uuid = res.get('uuid') or res.get('data', {}).get('uuid')
        if not uuid:
            print(f"❌ 매수 주문 실패: {res}")
            send_telegram_message(f"❌ <b>{market_code}</b> {level.level}차 매수 실패\n{res}")
            break

        level.buy_uuid = uuid
        print(f"🛒 [{level.level}]차 매수 주문 등록: {level.buy_price}원 / {level.volume}개")

        # ⏳ 매수 체결 대기
        while True:
            time.sleep(sleep_sec)
            if stop_condition and stop_condition():
                print("🛑 체결 대기 중 중단됨.")
                return

            detail = get_order_detail(level.buy_uuid)
            data = detail.get('data') or detail
            executed = float(data.get('executed_volume', 0))
            remaining = float(data.get('remaining_volume', 0))

            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if executed > 0 and remaining == 0:
                print(f"✅ [{level.level}]차 매수 체결 완료 🕒 {now}")
                send_telegram_message(
                    f"✅ <b>{market_code}</b> {level.level}차 매수 체결\n📉 {level.buy_price}원\n📦 {level.volume}개\n🕒 {now}")
                break
            else:
                print(f"⏳ 매수 미체결 (체결: {executed}, 잔여: {remaining}) 🕒 {now}")

        # 📤 매도 예약
        res = place_order(market, 'ask', level.volume, level.sell_price, 'limit')
        sell_uuid = res.get('uuid') or res.get('data', {}).get('uuid')
        if sell_uuid:
            level.sell_uuid = sell_uuid
            print(f"📤 [{level.level}]차 매도 예약: {level.sell_price}원")
            send_telegram_message(
                f"📤 <b>{market_code}</b> {level.level}차 매도 예약\n📈 {level.sell_price}원\n📦 {level.volume}개")

        current_level += 1
