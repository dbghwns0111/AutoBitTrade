# AutoBitTrade/strategy/auto_buy_sell.py
# 매수 → 매도 + 다음 매수 동시 실행 전략 (stop_condition 대응 + 로그 저장 + 텔레그램 연동)

import time
import math
import csv
import os
from datetime import datetime
from api.api import place_order, get_order_detail
from config.tick_table import TICK_SIZE
from utils.telegram import send_telegram_message


def run_buy_then_sell_chain(start_price, percent_interval, krw_amount, max_orders, market_code='USDT', sleep_sec=5, stop_condition=None):
    """
    매수 체결 시 다음 매수 + 매도 전략 (중단 조건 포함)
    :param start_price: 시작 가격 (float)
    :param percent_interval: 간격 퍼센트 (float)
    :param krw_amount: 회차당 매수 금액 (KRW)
    :param max_orders: 최대 매수 차수 (int)
    :param market_code: 종목 (예: USDT)
    :param sleep_sec: 대기 시간
    :param stop_condition: 중단 조건 함수 (기본 None)
    :return: 체결 결과 리스트
    """
    orders = []
    market_code = market_code.upper()
    market = f"KRW-{market_code}"
    tick = TICK_SIZE.get(market)

    if tick is None:
        print(f"❌ [{market}] 종목은 tick_table에 정의되어 있지 않습니다.\n자동매매를 사용하려면 tick_table.py에 해당 종목과 호가 단위를 추가해 주세요.")
        return []

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "autotrade_orders.csv")
    log_exists = os.path.exists(log_path)

    with open(log_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'market', 'round', 'buy_price', 'sell_price', 'volume', 'timestamp'])
        if not log_exists:
            writer.writeheader()

        for i in range(max_orders):
            if stop_condition and stop_condition():
                print("🛑 전략 중단 감지됨, 매수 중단")
                break

            rate = 1 - (percent_interval / 100) * i
            raw_price = start_price * rate
            buy_price = math.floor(raw_price / tick) * tick
            volume = round(krw_amount / buy_price, 8)

            print(f"\n🛒 {i+1}차 매수 주문: {buy_price}원에 {volume}개")
            res = place_order(market, 'bid', volume, buy_price, 'limit')
            uuid = res.get('uuid') or res.get('data', {}).get('uuid')

            if not uuid:
                print(f"❌ 매수 주문 실패: {res}")
                send_telegram_message(f"❌ <b>{market_code}</b> {i+1}/{max_orders}차 매수 주문 실패\n{res}")
                break

            while True:
                time.sleep(sleep_sec)
                if stop_condition and stop_condition():
                    print("🛑 체결 대기 중 중단 감지됨, 종료")
                    return orders

                detail = get_order_detail(uuid)
                data = detail.get('data') or detail
                try:
                    executed = float(data.get('executed_volume', 0))
                    remaining = float(data.get('remaining_volume', 0))
                except Exception:
                    executed = 0
                    remaining = 1

                if executed > 0 and remaining == 0:
                    print(f"✅ {i+1}차 매수 체결 완료")
                    send_telegram_message(
                        f"✅ <b>{market_code}</b> {i+1}/{max_orders}차 매수 체결\n📉 가격: {buy_price}원\n📦 수량: {volume}")
                    break
                else:
                    print(f"⏳ 매수 미체결 (체결: {executed}, 잔여: {remaining})")

            sell_rate = 1 + (percent_interval / 100)
            raw_sell_price = buy_price * sell_rate
            sell_price = math.floor(raw_sell_price / tick) * tick

            print(f"📤 {i+1}차 대응 매도 주문: {sell_price}원에 {volume}개")
            sell_res = place_order(market, 'ask', volume, sell_price, 'limit')
            sell_uuid = sell_res.get('uuid') or sell_res.get('data', {}).get('uuid')

            if sell_uuid:
                send_telegram_message(
                    f"📤 <b>{market_code}</b> {i+1}/{max_orders}차 매도 예약\n📈 가격: {sell_price}원\n📦 수량: {volume}")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow({
                'date': datetime.now().strftime("%Y-%m-%d"),
                'market': market_code,
                'round': i + 1,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'volume': volume,
                'timestamp': timestamp
            })

            orders.append({
                'buy_round': i + 1,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'buy_uuid': uuid,
                'sell_uuid': sell_uuid
            })

    return orders