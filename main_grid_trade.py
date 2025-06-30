# AutoBitTrade/main_grid_trade.py
# 무한 반복형 자동매매 전략 실행 (auto_grid_trade.py 기반)

from strategy.auto_grid_trade import run_grid_trade
from utils.telegram import send_telegram_message

if __name__ == '__main__':
    print("📈 무한 반복 매수-매도 전략 실행 시작")

    market_code = input("마켓 코드를 입력하세요 (예: USDT, BTC): ").strip().upper()
    start_price = float(input("시작 기준 가격을 입력하세요 (예: 1430): ").strip())
    percent = float(input("매수/매도 간격 퍼센트 (%)를 입력하세요 (예: 1): ").strip())
    krw_amount = float(input("회차당 매수 금액 (KRW)을 입력하세요 (예: 5000): ").strip())
    max_levels = int(input("매수 레벨 개수를 입력하세요 (예: 3): ").strip())

    send_telegram_message(
        f"🚀 반복형 자동매매 전략 시작\n<b>{market_code}</b> 기준가 {start_price}원\n퍼센트 간격: {percent}%\n회차당 금액: {krw_amount}원\n레벨: {max_levels}")

    run_grid_trade(
        start_price=start_price,
        percent_interval=percent,
        krw_amount=krw_amount,
        max_levels=max_levels,
        market_code=market_code
    )
