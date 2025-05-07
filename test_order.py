# bitsplit/test_order_usdt.py
from api.api import place_order

# USDT 매수 시도
response = place_order(
    market='KRW-USDT',  # 마켓: 테더
    side='bid',         # 매수
    volume='4',         # 4개
    price='1420',       # 1개당 1420원
    ord_type='limit'    # 지정가 주문
)

print("📦 매수 응답 결과:")
print(response)
