# AutoBitTrade/gui/gui_app.py
# GUI 기반 자동매매 실행기 (중단 버튼 + 실시간 로그창 포함)

import sys
import os

# 루트 경로 추가 (상대 경로 문제 해결)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox, scrolledtext
from api.api import cancel_order
from strategy.auto_buy_sell import run_buy_then_sell_chain
from utils.telegram import send_telegram_message
import threading
import csv

# 중단 플래그
stop_flag = False
active_uuids = []  # 매수/매도 주문 UUID 저장


def start_strategy():
    def run():
        global stop_flag, active_uuids
        stop_flag = False
        active_uuids.clear()

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
                market_code=market,
                sleep_sec=5,
                stop_condition=lambda: stop_flag
            )

            for order in result:
                active_uuids.append(order['buy_uuid'])
                if order['sell_uuid']:
                    active_uuids.append(order['sell_uuid'])

            if stop_flag:
                messagebox.showwarning("전략 중단됨", "자동매매 전략이 사용자에 의해 중단되었습니다.")
            else:
                messagebox.showinfo("전략 종료", f"자동매매 완료! 총 {len(result)}차 실행")

        except Exception as e:
            messagebox.showerror("오류", f"실행 중 오류 발생: {e}")

    threading.Thread(target=run).start()


def stop_strategy():
    global stop_flag
    stop_flag = True
    print("🛑 전략 중단 요청됨...")
    send_telegram_message("🛑 GUI를 통해 자동매매 전략이 중단되었습니다.")

    if active_uuids:
        print("🚫 미체결 주문 취소 중...")
        for uuid in active_uuids:
            try:
                cancel_res = cancel_order(uuid)
                print(f"🧾 주문 취소 요청: {uuid} → {cancel_res.get('status')}")
            except Exception as e:
                print(f"❌ 주문 취소 실패 ({uuid}): {e}")


class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END)

    def flush(self):
        pass


# GUI 생성
root = tk.Tk()
root.title("AutoBitTrade 자동매매 GUI")
root.geometry("460x570")

# 입력 필드
labels = ["코인 코드 (예: USDT)", "시작 매수가 (원)", "간격 (%)", "회차당 매수 금액 (원)", "최대 매수 차수"]

entry_market = tk.Entry(root); entry_market.insert(0, 'USDT')
entry_price = tk.Entry(root)
entry_percent = tk.Entry(root)
entry_amount = tk.Entry(root)
entry_rounds = tk.Entry(root)

entries = [entry_market, entry_price, entry_percent, entry_amount, entry_rounds]

for i, (label, entry) in enumerate(zip(labels, entries)):
    tk.Label(root, text=label).grid(row=i, column=0, padx=10, pady=8, sticky='w')
    entry.grid(row=i, column=1)

# 실행/중단 버튼
start_btn = tk.Button(root, text="전략 실행", command=start_strategy, bg="#28a745", fg="white", width=20)
start_btn.grid(row=6, column=0, columnspan=2, pady=5)

stop_btn = tk.Button(root, text="전략 중단", command=stop_strategy, bg="#dc3545", fg="white", width=20)
stop_btn.grid(row=7, column=0, columnspan=2, pady=5)

# 로그 출력창
tk.Label(root, text="실시간 로그").grid(row=8, column=0, columnspan=2)
log_box = scrolledtext.ScrolledText(root, height=15, width=55, state='normal')
log_box.grid(row=9, column=0, columnspan=2, padx=10, pady=10)
sys.stdout = TextRedirector(log_box)

root.mainloop()
