# AutoBitTrade/gui_app.py
# GUI 기반 자동매매 실행기 (tkinter)

import tkinter as tk
from tkinter import messagebox
from strategy.auto_buy_sell import run_buy_then_sell_chain
from utils.telegram import send_telegram_message


def start_strategy():
    try:
        market = entry_market.get().upper()
        start_price = float(entry_price.get())
        percent = float(entry_percent.get())
        krw_amount = float(entry_amount.get())
        max_orders = int(entry_rounds.get())

        send_telegram_message(
            f"🚀 자동매매 전략 시작됨 (GUI)\n<b>{market}</b> 기준가 {start_price}원\n퍼센트 간격: {percent}%\n회차당 금액: {krw_amount}원\n총 차수: {max_orders}"
        )

        result = run_buy_then_sell_chain(
            start_price=start_price,
            percent_interval=percent,
            krw_amount=krw_amount,
            max_orders=max_orders,
            market_code=market
        )

        messagebox.showinfo("전략 종료", f"자동매매 완료! 총 {len(result)}차 실행")

    except Exception as e:
        messagebox.showerror("오류", f"실행 중 오류 발생: {e}")


# GUI 생성
root = tk.Tk()
root.title("AutoBitTrade 자동매매 GUI")
root.geometry("360x320")

# 입력 필드
labels = ["코인 코드 (예: USDT)", "시작 매수가 (원)", "간격 (%)", "회차당 매수 금액 (원)", "최대 매수 차수"]
entries = []

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, padx=10, pady=8, sticky='w')

entry_market = tk.Entry(root); entry_market.insert(0, 'USDT')
entry_price = tk.Entry(root)
entry_percent = tk.Entry(root)
entry_amount = tk.Entry(root)
entry_rounds = tk.Entry(root)

entry_market.grid(row=0, column=1)
entry_price.grid(row=1, column=1)
entry_percent.grid(row=2, column=1)
entry_amount.grid(row=3, column=1)
entry_rounds.grid(row=4, column=1)

# 실행 버튼
start_btn = tk.Button(root, text="전략 실행", command=start_strategy, bg="#28a745", fg="white", width=20)
start_btn.grid(row=6, column=0, columnspan=2, pady=20)

root.mainloop()
