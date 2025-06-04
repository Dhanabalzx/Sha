import requests
import time
from datetime import datetime

BOT_TOKEN = '7853206716:AAGMWNSMeNyyS6OjZPujo8nMnqDjWCjo1LY'
CHAT_ID = '771241303'


def get_banknifty_data():
    # You can use NSE or TradingView API wrappers (placeholder for now)
    return {
        'banknifty': '48,235 (-0.45%)',
        'sgx_nifty': '-55 pts',
        'us_futures': 'S&P -0.2%, Nasdaq -0.3%',
        'crude': '$78.6',
        'usdinr': '₹83.24',
        'fii': '+₹1200 Cr',
        'dii': '-₹300 Cr',
        'sentiment': 'Mildly Bearish',
        'support': '48100',
        'resistance': '48450'
    }

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
    requests.post(url, data=payload)

def format_message(data):
    now = datetime.now().strftime('%H:%M %p')
    msg = f"""🕒 [{now}] *Market Pulse*
📉 BankNifty: {data['banknifty']}
📊 SGX Nifty: {data['sgx_nifty']}
🇺🇸 US Futures: {data['us_futures']}
💹 Crude: {data['crude']} | USDINR: {data['usdinr']}
📈 FII: {data['fii']} | DII: {data['dii']}
💬 Sentiment: {data['sentiment']}
📍 Support: {data['support']} | Resistance: {data['resistance']}"""
    return msg

def run_bot():
    while True:
        data = get_banknifty_data()
        message = format_message(data)
        send_telegram_message(message)
        time.sleep(900)  # Wait for 15 minutes

if __name__ == "__main__":
    run_bot()
