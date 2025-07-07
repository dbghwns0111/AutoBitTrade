import requests
import logging
logging.basicConfig(level=logging.INFO)

def get_current_price(market_code='USDT'):
    try:
        url = f"https://api.bithumb.com/public/ticker/{market_code}_KRW"
        res = requests.get(url)
        data = res.json()
        if data['status'] == '0000':
            return float(data['data']['closing_price'])
        else:
            logging.debug(f"시세 API 응답 오류: {data}")
    except Exception as e:
        logging.debug(f"시세 조회 실패: {e}")
