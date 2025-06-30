# AutoBitTrade/main_stepwise_trade.py
# 단계별 1차수씩만 순차 매매 실행 전략 (auto_grid_trade_stepwise 기반)

from strategy.auto_grid_trade_stepwise import run_grid_trade_stepwise
from utils.telegram import send_telegram_message

if __name__ == '__main__':
    print("📈 단계별 자동매매 전략 실행 시작")

    market_code = input("마켓 코드를 입력하세요 (예: USDT, BTC): ").strip().upper()
    start_price = float(input("시작 기준 가격을 입력하세요 (예: 1430): ").strip())
    percent = float(input("매수/매도 간격 퍼센트 (%)를 입력하세요 (예: 1): ").strip())
    krw_amount = float(input("회차당 매수 금액 (KRW)을 입력하세요 (예: 5000): ").strip())
    max_levels = int(input("최대 매수 차수를 입력하세요 (예: 5): ").strip())

    send_telegram_message(
        f"🚀 단계별 자동매매 전략 시작됨\n<b>{market_code}</b> 기준가 {start_price}원\n퍼센트 간격: {percent}%\n회차당 금액: {krw_amount}원\n총 차수: {max_levels}"
    )

    run_grid_trade_stepwise(
        start_price=start_price,
        percent_interval=percent,
        krw_amount=krw_amount,
        max_levels=max_levels,
        market_code=market_code
    )
