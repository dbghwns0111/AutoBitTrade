# bitsplit/api/api.py
# 빗썸 API와 연동하는 함수 모음

import os
import uuid
import hashlib
import time
import json
from urllib.parse import urlencode
import requests
import jwt
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
accessKey = os.getenv("BITHUMB_API_KEY")
secretKey = os.getenv("BITHUMB_API_SECRET")
apiUrl = 'https://api.bithumb.com'

# 공통: JWT 토큰 생성 함수
def _make_token(query: dict = None):
    payload = {
        'access_key': accessKey,
        'nonce': str(uuid.uuid4()),
        'timestamp': round(time.time() * 1000),
    }

    if query:
        query_string = urlencode(query).encode()
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()
        payload['query_hash'] = query_hash
        payload['query_hash_alg'] = 'SHA512'

    jwt_token = jwt.encode(payload, secretKey, algorithm='HS256')
    return {
        'Authorization': f'Bearer {jwt_token}'
    }

# 자산 조회
def get_balance():
    headers = _make_token()
    resp = requests.get(f"{apiUrl}/v1/accounts", headers=headers)
    return resp.json()

# 주문 가능 정보 조회
def get_order_chance(market='KRW-BTC'):
    query = {"market": market}
    headers = _make_token(query)
    resp = requests.get(f"{apiUrl}/v1/orders/chance", params=query, headers=headers)
    return resp.json()

# 주문 실행 함수 (지정가 또는 시장가)
def place_order(market, side, volume, price, ord_type='limit'):
    body = {
        "market": market,
        "side": side,
        "volume": str(volume),
        "price": str(price),
        "ord_type": ord_type
    }
    headers = _make_token(body)
    headers['Content-Type'] = 'application/json'
    resp = requests.post(f"{apiUrl}/v1/orders", headers=headers, data=json.dumps(body))
    return resp.json()

# 주문 취소
def cancel_order(order_uuid):
    query = {"uuid": order_uuid}
    headers = _make_token(query)
    resp = requests.delete(f"{apiUrl}/v1/order", params=query, headers=headers)
    return resp.json()

# 개별 주문 조회
def get_order_detail(order_uuid):
    query = {"uuid": order_uuid}
    headers = _make_token(query)
    resp = requests.get(f"{apiUrl}/v1/order", params=query, headers=headers)
    return resp.json()

# 주문 리스트 조회

def get_order_list(market='KRW-BTC', limit=100, page=1, order_by='desc', uuids=None):
    query = {
        "market": market,
        "limit": str(limit),
        "page": str(page),
        "order_by": order_by
    }
    if uuids:
        for i, u in enumerate(uuids):
            query[f"uuids[{i}]"] = u

    headers = _make_token(query)
    resp = requests.get(f"{apiUrl}/v1/orders", params=query, headers=headers)
    return resp.json()
