# bitsplit/main.py
# 사용자 입력 기반 자동매매 진입점 스크립트

from strategy.autotrade import run_split_buy_strategy

if __name__ == '__main__':
    print("📈 자동매매 전략 실행 시작")

    # 사용자 입력 받기
    market_code = input("마켓 코드를 입력하세요 (예: BTC, USDT): ").strip().upper()
    start_price = float(input("시작 기준 가격을 입력하세요 (예: 1420): ").strip())
    percent_interval = float(input("매수 간격 퍼센트 (%)를 입력하세요 (예: 1): ").strip())
    krw_amount = float(input("회차당 매수 금액 (KRW)을 입력하세요 (예: 5000): ").strip())
    max_orders = int(input("최대 매수 차수를 입력하세요 (예: 5): ").strip())

    # 전략 실행
    results = run_split_buy_strategy(
        start_price=start_price,
        percent_interval=percent_interval,
        krw_amount=krw_amount,
        max_orders=max_orders,
        market_code=market_code
    )

    # 결과 출력
    print("\n🧾 전체 주문 결과:")
    for order in results:
        print(f"{order['round']}차 주문가: {order['price']}원 → 체결수량: {order['executed_volume']}")
