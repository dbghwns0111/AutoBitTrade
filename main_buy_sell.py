# bitsplit/main_buy_sell.py
# 매수-매도 연동 자동전략 실행 스크립트 (텔레그램 메시지 포함)

from strategy.auto_buy_sell import run_buy_then_sell_chain
from utils.telegram import send_telegram_message

if __name__ == '__main__':
    print("📈 매수 → 매도 자동전략 실행 시작")

    market_code = input("마켓 코드를 입력하세요 (예: USDT, BTC): ").strip().upper()
    start_price = float(input("시작 매수가를 입력하세요 (예: 1430): ").strip())
    percent = float(input("매수/매도 간격 퍼센트 (%)를 입력하세요 (예: 1): ").strip())
    krw_amount = float(input("회차당 매수 금액 (KRW)을 입력하세요 (예: 5000): ").strip())
    max_orders = int(input("최대 매수 차수를 입력하세요 (예: 3): ").strip())

    # 전략 실행 전 시작 알림
    send_telegram_message(
        f"🚀 자동매매 전략 시작됨\n<b>{market_code}</b> 기준가 {start_price}원\n퍼센트 간격: {percent}%\n회차당 금액: {krw_amount}원\n총 차수: {max_orders}")

    result = run_buy_then_sell_chain(
        start_price=start_price,
        percent_interval=percent,
        krw_amount=krw_amount,
        max_orders=max_orders,
        market_code=market_code
    )

    print("\n📊 전체 주문 처리 결과:")
    for r in result:
        print(f"{r['buy_round']}차 매수 → {r['buy_price']}원, 익절 매도 예약가: {r['sell_price']}원")

    # 전략 종료 알림
    send_telegram_message(f"✅ 자동매매 전략 종료: {market_code} 총 {len(result)}차 매수 완료")
