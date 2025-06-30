# AutoBitTrade/strategy/auto_buy_sell.py (리팩토링 버전)
# 매수 → 매도 + 다음 매수 동시 실행 전략 (ActiveLevel 구조 기반)

import time
import math
import csv
import os
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


def run_buy_then_sell_chain(start_price, percent_interval, krw_amount, max_orders,
                            market_code='USDT', sleep_sec=5, stop_condition=None):
    market_code = market_code.upper()
    market = f"KRW-{market_code}"
    tick = TICK_SIZE.get(market)

    if tick is None:
        print(f"❌ [{market}] 종목은 tick_table에 정의되어 있지 않습니다.")
        return []

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "autotrade_orders.csv")
    log_exists = os.path.exists(log_path)

    levels = []
    for i in range(max_orders):
        rate = 1 - (percent_interval / 100) * i
        buy_price = math.floor((start_price * rate) / tick) * tick
        sell_price = math.floor((buy_price * (1 + percent_interval / 100)) / tick) * tick
        volume = round(krw_amount / buy_price, 8)
        levels.append(ActiveLevel(i + 1, buy_price, sell_price, volume))

    results = []

    with open(log_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'market', 'round', 'buy_price',
                                               'sell_price', 'volume', 'timestamp'])
        if not log_exists:
            writer.writeheader()

        for level in levels:
            if stop_condition and stop_condition():
                print("🛑 전략 중단 감지됨, 매수 중단")
                break

            print(f"🛒 {level.level}차 매수 주문: {level.buy_price}원에 {level.volume}개")
            res = place_order(market, 'bid', level.volume, level.buy_price, 'limit')
            level.buy_uuid = res.get('uuid') or res.get('data', {}).get('uuid')

            if not level.buy_uuid:  
                print(f"❌ 매수 주문 실패: {res}")
                send_telegram_message(f"❌ <b>{market_code}</b> {level.level}/{max_orders}차 매수 실패  {res}🕒{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                break

            while True:
                time.sleep(sleep_sec)
                if stop_condition and stop_condition():
                    print("🛑 체결 대기 중 중단 감지됨, 종료")
                    return results

                detail = get_order_detail(level.buy_uuid)
                data = detail.get('data') or detail
                try:
                    executed = float(data.get('executed_volume', 0))
                    remaining = float(data.get('remaining_volume', 0))
                except Exception:
                    executed = 0
                    remaining = 1

                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if executed > 0 and remaining == 0:
                    print(f"✅ {level.level}차 매수 체결 완료 🕒 {now}")
                    send_telegram_message(f"✅ <b>{market_code}</b> {level.level}/{max_orders}차 매수 체결 {level.buy_price}원📦 {level.volume}개🕒 {now}")
                    break
                else:
                    print(f"⏳ 매수 미체결 (체결: {executed}, 잔여: {remaining}) 🕒 {now}")

            print(f"📤 {level.level}차 대응 매도 주문: {level.sell_price}원에 {level.volume}개")
            res = place_order(market, 'ask', level.volume, level.sell_price, 'limit')
            level.sell_uuid = res.get('uuid') or res.get('data', {}).get('uuid')

            if level.sell_uuid:
                send_telegram_message(f"📤 <b>{market_code}</b> {level.level}/{max_orders}차 매도 예약 {level.sell_price}원📦 {level.volume}개")

            writer.writerow({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'market': market_code,
                'round': level.level,
                'buy_price': level.buy_price,
                'sell_price': level.sell_price,
                'volume': level.volume,
                'timestamp': now
            })

            results.append({
                'buy_round': level.level,
                'buy_price': level.buy_price,
                'sell_price': level.sell_price,
                'buy_uuid': level.buy_uuid,
                'sell_uuid': level.sell_uuid
            })

    return results
