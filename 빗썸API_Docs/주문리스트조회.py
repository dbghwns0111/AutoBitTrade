# Python 3
# pip install pyjwt python-dotenv requests

import os
import uuid as uuid_lib
import hashlib
import time
from urllib.parse import urlencode
import requests
import jwt
import json
from dotenv import load_dotenv

# ① .env 파일 로드
load_dotenv()
accessKey = os.getenv("BITHUMB_API_KEY")
secretKey = os.getenv("BITHUMB_API_SECRET")
apiUrl    = "https://api.bithumb.com"

# ② 사용자 입력
market   = input("조회할 마켓 (예: KRW-XRP): ").strip()
limit    = input("페이지당 주문 개수 limit (기본 100): ").strip() or "100"
page     = input("조회할 페이지 번호 page (기본 1): ").strip() or "1"
order_by = input("정렬순서 order_by (asc 또는 desc, 기본 desc): ").strip().lower() or "desc"
uuids_in = input("조회할 주문 UUID들 (쉼표로 구분): ").strip()
uuids    = [u.strip() for u in uuids_in.split(",") if u.strip()]

# ③ 쿼리 문자열 생성 (market, limit, page, order_by + uuids[])
base_params = {"market": market, "limit": limit, "page": page, "order_by": order_by}
base_q = urlencode(base_params)
uuid_q = "&".join(f"uuids[]={u}" for u in uuids)
query  = base_q + (f"&{uuid_q}" if uuid_q else "")

# ④ query_hash 생성
h = hashlib.sha512()
h.update(query.encode("utf-8"))
query_hash = h.hexdigest()

# ⑤ JWT 페이로드 및 토큰 생성
payload = {
    "access_key":     accessKey,
    "nonce":          str(uuid_lib.uuid4()),
    "timestamp":      round(time.time() * 1000),
    "query_hash":     query_hash,
    "query_hash_alg": "SHA512",
}
jwt_token = jwt.encode(payload, secretKey, algorithm="HS256")
auth_header = f"Bearer {jwt_token}"

# ⑥ 헤더 구성
headers = {
    "Authorization": auth_header
}

# ⑦ API 호출
try:
    url      = f"{apiUrl}/v1/orders?{query}"
    resp     = requests.get(url, headers=headers)
    data_all = resp.json()
    print("HTTP 상태코드:", resp.status_code)

    if data_all.get("status") != "0000":
        print(f"❌ 조회 실패 (status {data_all.get('status')}): {data_all.get('message')}")
        exit(1)

    orders = data_all.get("data", {}).get("order_list", [])

    # ⑧ 리스트 조회 결과 예쁘게 출력
    print("\n=== 주문 리스트 조회 결과 ===")
    for idx, order in enumerate(orders, start=1):
        print(f"\n▶ 주문 #{idx} (UUID: {order.get('uuid')})")
        fields = [
            ("주문 종류",          order.get("side")),            
            ("통화",               f"{order.get('order_currency')}/{order.get('payment_currency')}"),
            ("주문 수량",          order.get("units")),
            ("체결 수량",          order.get("executed_units")),
            ("미체결 수량",        order.get("remaining_units")),
            ("주문가",             order.get("price")),
            ("평균 체결가",         order.get("average_price")),
            ("수수료",             order.get("paid_fee")),
            ("주문 상태",          order.get("status")),
            ("주문 생성 시각",     order.get("order_date")),
        ]
        # 레이블 폭 계산
        label_width = max(len(label) for label, _ in fields)
        # 항목별 출력
        for label, val in fields:
            print(f"{label.ljust(label_width)} : {val}")

except Exception as err:
    print("예외 발생:", err)
