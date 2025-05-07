# Python 3
# pip install pyjwt python-dotenv requests

import os
import uuid
import hashlib
import time
from urllib.parse import urlencode
import requests
import jwt
from dotenv import load_dotenv

# ① .env 파일 로드
load_dotenv()
accessKey = os.getenv("BITHUMB_API_KEY")
secretKey = os.getenv("BITHUMB_API_SECRET")
apiUrl    = 'https://api.bithumb.com'

# ② 사용자로부터 취소할 주문 UUID 입력
order_uuid = input("취소할 주문의 UUID를 입력하세요: ").strip()

# ③ API 파라미터 준비
param = {'uuid': order_uuid}

# ④ query_hash 생성
query = urlencode(param).encode()
h = hashlib.sha512()
h.update(query)
query_hash = h.hexdigest()

# ⑤ JWT 페이로드 생성
payload = {
    'access_key':     accessKey,
    'nonce':          str(uuid.uuid4()),
    'timestamp':      round(time.time() * 1000),
    'query_hash':     query_hash,
    'query_hash_alg': 'SHA512',
}

# ⑥ JWT 토큰 인코딩 (HS256)
jwt_token = jwt.encode(payload, secretKey, algorithm="HS256")
authorization_token = f"Bearer {jwt_token}"

# ⑦ 헤더 구성
headers = {
    'Authorization': authorization_token
}

# ⑧ 주문취소 API 호출
try:
    response = requests.delete(
        f"{apiUrl}/v1/order",
        params=param,
        headers=headers
    )
    result = response.json()
    status = result.get('status')
    message = result.get('message')

    # ⑨ 성공/실패 메시지 출력
    if status == '0000':
        print(f"✅ 주문 {order_uuid} 가 정상적으로 취소되었습니다.")
    else:
        print(f"❌ 주문 취소 실패 (status {status}): {message}")

except Exception as err:
    print("예외 발생:", err)
