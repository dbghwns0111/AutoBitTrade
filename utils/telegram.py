# bitsplit/utils/telegram.py
# 텔레그램 알림 전송 유틸리티

import os
import requests
from dotenv import load_dotenv

# .env 파일에서 토큰과 채팅 ID 로드
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(message):
    """
    텔레그램 메시지 전송 함수
    :param message: 전송할 문자열 메시지
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"❌ 텔레그램 전송 실패: {response.text}")
    except Exception as e:
        print(f"🚫 텔레그램 요청 중 오류 발생: {e}")
