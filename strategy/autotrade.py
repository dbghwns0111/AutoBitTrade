# bitsplit/strategy/autotrade.py
# 호가 단위 외부 설정으로 분리된 지정가 분할 매수 전략 (종목 검증 포함)

import time
import math
from api.api import place_order, get_order_detail
from config.tick_table import TICK_SIZE


def run_split_buy_strategy(start_price, percent_interval, krw_amount, max_orders, market_code='USDT', sleep_sec=5):
    """
    체결 기반 분할 매수 전략 (tick 단위 적용)
    :param start_price: 시작 기준 가격 (float)
    :param percent_interval: 매수 간격 퍼센트 (float)
    :param krw_amount: 회차당 매수 금액 (KRW)
    :param max_orders: 최대 매수 차수 (int)
    :param market_code: 거래 대상 코인 코드 (예: 'BTC', 'USDT')
    :param sleep_sec: 주문 확인 간격 (초)
    :return: 주문 결과 리스트
    """
    orders = []
    market = f"KRW-{market_code.upper()}"

    if market not in TICK_SIZE:
        print(f"❌ [{market}] 종목은 tick_table에 정의되어 있지 않습니다.\n자동매매를 사용하려면 tick_table.py에 해당 종목과 호가 단위를 추가해 주세요.")
        return orders

    tick_size = TICK_SIZE[market]

    for i in range(max_orders):
        rate = 1 - (percent_interval / 100) * i
        raw_price = start_price * rate
        order_price = math.floor(raw_price / tick_size) * tick_size
        volume = round(krw_amount / order_price, 8)

        print(f"\n🛒 {i+1}차 매수 주문: {order_price}원에 {volume}개 매수 (금액: 약 {krw_amount}원)")
        order_res = place_order(
            market=market,
            side='bid',
            volume=volume,
            price=order_price,
            ord_type='limit'
        )

        uuid = order_res.get('uuid') or order_res.get('data', {}).get('uuid')

        if not uuid:
            print(f"❌ 주문 실패 또는 UUID 없음: {order_res}")
            break

        print(f"📨 주문 접수됨 (UUID: {uuid}), 체결 대기 중...")

        while True:
            time.sleep(sleep_sec)
            detail = get_order_detail(uuid)
            data = detail.get('data') or detail

            try:
                executed = float(data.get('executed_volume', 0))
                remaining = float(data.get('remaining_volume', 0))
            except Exception:
                executed = 0
                remaining = 1

            if executed > 0 and remaining == 0:
                print(f"✅ {i+1}차 주문 전량 체결 완료")
                orders.append({
                    'round': i + 1,
                    'price': order_price,
                    'uuid': uuid,
                    'executed_volume': executed,
                    'remaining_volume': remaining
                })
                break
            else:
                print(f"⏳ {i+1}차 주문 미체결 (체결: {executed}, 잔여: {remaining}), 다시 확인 중...")

    return orders
