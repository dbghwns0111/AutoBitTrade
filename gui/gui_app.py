# AutoBitTrade/gui/gui_app.py

import os
import sys
import customtkinter as ctk
import threading
import time
from tkinter import messagebox

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy.auto_trade import run_auto_trade
from utils.telegram import send_telegram_message
from utils.price import get_current_price
from api.api import cancel_all_orders

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

stop_flag = False
def stop_condition():
    return stop_flag

def update_multi_prices(labels):
    while True:
        for coin, label in labels.items():
            price = get_current_price(coin)
            if price:
                now = time.strftime('%H:%M:%S')
                label.configure(text=f"{coin}: {price:,.0f} KRW  ⏱ {now}")
        time.sleep(3)

def start_strategy():
    def run():
        global stop_flag
        stop_flag = False
        try:
            market = entry_market.get().strip().upper()
            start_price = float(entry_price.get())
            krw_amount = float(entry_amount.get())
            max_levels = int(entry_rounds.get())
            buy_gap = float(entry_buy_gap.get())
            sell_gap = float(entry_sell_gap.get())
            buy_mode_val = buy_mode.get()
            sell_mode_val = sell_mode.get()

            send_telegram_message(
                f"🚀 전략 시작: {market} / 시작가 {start_price}원 / 매수 {buy_gap}{'%' if buy_mode_val=='percent' else '원'} / "
                f"매도 {sell_gap}{'%' if sell_mode_val=='percent' else '원'} / {krw_amount} KRW")

            run_auto_trade(
                start_price=start_price,
                krw_amount=krw_amount,
                max_levels=max_levels,
                market_code=market,
                buy_gap=buy_gap,
                buy_mode=buy_mode_val,
                sell_gap=sell_gap,
                sell_mode=sell_mode_val,
                stop_condition=stop_condition,
                sleep_sec=5
            )

            if stop_flag:
                messagebox.showwarning("전략 중단됨", "사용자에 의해 전략이 중단되었습니다.")
            else:
                messagebox.showinfo("전략 종료", "전략이 완료되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"전략 실행 중 오류 발생:\n{e}")
    threading.Thread(target=run, daemon=True).start()

def stop_strategy():
    global stop_flag
    stop_flag = True
    market = entry_market.get().strip().upper()
    full_market = f"KRW-{market}"
    try:
        cancel_all_orders(full_market)
        send_telegram_message(f"🛑 {market} 전략 중단 및 주문 전체 취소 완료")
    except Exception as e:
        send_telegram_message(f"⚠️ 주문 취소 오류: {e}")

# 앱 UI 구성
app = ctk.CTk()
app.title("AutoBitTrade - customtkinter 버전")
app.geometry("800x800")

# 시세 표시
label_btc = ctk.CTkLabel(app, text="BTC: - KRW", font=ctk.CTkFont(size=14, weight="bold"))
label_usdt = ctk.CTkLabel(app, text="USDT: - KRW", font=ctk.CTkFont(size=14, weight="bold"))
label_xrp = ctk.CTkLabel(app, text="XRP: - KRW", font=ctk.CTkFont(size=14, weight="bold"))
label_btc.grid(row=0, column=0, padx=10, pady=10, sticky='w')
label_usdt.grid(row=0, column=1, padx=10, pady=10, sticky='w')
label_xrp.grid(row=0, column=2, padx=10, pady=10, sticky='w')

# 기본 입력
labels = ["코인 코드 (예: USDT)", "시작 매수가 (원)", "회차당 매수 금액 (원)", "최대 매수 차수"]
entries = []
for i, label in enumerate(labels):
    ctk.CTkLabel(app, text=label).grid(row=i+1, column=0, padx=10, pady=6, sticky="w")
    entry = ctk.CTkEntry(app, width=200)
    entry.grid(row=i+1, column=1, columnspan=2, padx=5, pady=6, sticky="w")
    entries.append(entry)

entry_market, entry_price, entry_amount, entry_rounds = entries
entry_market.insert(0, 'USDT')

# 매수 간격
buy_mode = ctk.StringVar(value="percent")
ctk.CTkLabel(app, text="📉 매수 간격 단위").grid(row=5, column=0, padx=10, pady=6, sticky="w")
ctk.CTkRadioButton(app, text="퍼센트", variable=buy_mode, value="percent").grid(row=5, column=1, sticky="w")
ctk.CTkRadioButton(app, text="금액(원)", variable=buy_mode, value="price").grid(row=5, column=2, sticky="w")
ctk.CTkLabel(app, text="매수 간격 값").grid(row=6, column=0, padx=10, pady=6, sticky="w")
entry_buy_gap = ctk.CTkEntry(app, width=200)
entry_buy_gap.grid(row=6, column=1, columnspan=2, padx=5, pady=6, sticky="w")

# 매도 간격
sell_mode = ctk.StringVar(value="percent")
ctk.CTkLabel(app, text="📈 매도 간격 단위").grid(row=7, column=0, padx=10, pady=6, sticky="w")
ctk.CTkRadioButton(app, text="퍼센트", variable=sell_mode, value="percent").grid(row=7, column=1, sticky="w")
ctk.CTkRadioButton(app, text="금액(원)", variable=sell_mode, value="price").grid(row=7, column=2, sticky="w")
ctk.CTkLabel(app, text="매도 간격 값").grid(row=8, column=0, padx=10, pady=6, sticky="w")
entry_sell_gap = ctk.CTkEntry(app, width=200)
entry_sell_gap.grid(row=8, column=1, columnspan=2, padx=5, pady=6, sticky="w")

# 실행/중단 버튼
btn_start = ctk.CTkButton(app, text="전략 실행", command=start_strategy, fg_color="#28a745")
btn_stop = ctk.CTkButton(app, text="전략 중단", command=stop_strategy, fg_color="#dc3545")
btn_start.grid(row=9, column=0, columnspan=3, pady=10)
btn_stop.grid(row=10, column=0, columnspan=3, pady=5)

# 로그창
ctk.CTkLabel(app, text="실시간 로그").grid(row=11, column=0, columnspan=3)
log_textbox = ctk.CTkTextbox(app, height=250, width=560)
log_textbox.grid(row=12, column=0, columnspan=3, padx=10, pady=10)

# 로그 리디렉션
class TextRedirector:
    def __init__(self, textbox):
        self.textbox = textbox
    def write(self, text):
        self.textbox.insert("end", text)
        self.textbox.see("end")
    def flush(self): pass

sys.stdout = TextRedirector(log_textbox)

# 시세 쓰레드 시작
threading.Thread(target=update_multi_prices, args=({
    'BTC': label_btc,
    'USDT': label_usdt,
    'XRP': label_xrp,
},), daemon=True).start()

app.mainloop()
