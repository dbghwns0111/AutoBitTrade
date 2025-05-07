# bitsplit/test_sell.py
# 자동매도 전략 테스트 스크립트

from strategy.autosell import run_split_sell_strategy

if __name__ == '__main__':
    print("📤 자동매도 전략 테스트 시작")

    # 사용자 입력 예시
    market_code = input("매도할 마켓 코드를 입력하세요 (예: USDT, BTC): ").strip().upper()
    avg_price = float(input("기준 매수가를 입력하세요 (예: 1420): ").strip())
    percent = float(input("매도 간격 퍼센트 (%)를 입력하세요 (예: 1): ").strip())
    rounds = int(input("매도 차수를 입력하세요 (예: 3): ").strip())
    unit_volume = float(input("회차당 매도 수량을 입력하세요 (예: 3): ").strip())

    # 회차별 수량 리스트 구성
    volume_list = [unit_volume] * rounds

    # 전략 실행
    result = run_split_sell_strategy(
        average_buy_price=avg_price,
        percent_interval=percent,
        volume_list=volume_list,
        market_code=market_code
    )

    # 결과 출력
    print("\n🧾 매도 주문 결과:")
    for r in result:
        print(f"{r['round']}차 매도가: {r['price']}원 → 체결수량: {r['executed_volume']}")
