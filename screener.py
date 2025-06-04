import requests
import time
from datetime import datetime

BOT_TOKEN = '7853206716:AAGMWNSMeNyyS6OjZPujo8nMnqDjWCjo1LY'
CHAT_ID = '771241303'

def get_banknifty():
    # NSE India unofficial API for BankNifty live price
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20BANK"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    session = requests.Session()
    # Get cookies
    session.get("https://www.nseindia.com", headers=headers)
    r = session.get(url, headers=headers)
    data = r.json()
    for item in data['data']:
        if item['symbol'] == "BANKNIFTY":
            ltp = item['lastPrice']
            change = item['pChange']
            return f"{ltp} ({change}%)"
    return "N/A"

def get_sgx_nifty():
    # SGX Nifty from Moneycontrol unofficial API
    url = "https://priceapi.moneycontrol.com/pricefeed/nse/equitycash/BANKNIFTY"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        price = data.get("data", {}).get("pricecurrent", "N/A")
        change = data.get("data", {}).get("changepercent", "N/A")
        return f"{price} ({change}%)"
    return "N/A"

def get_us_futures():
    # Simple placeholder: use Yahoo Finance for ES=F (S&P 500 Futures)
    url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=ES=F, NQ=F"
    r = requests.get(url)
    if r.status_code == 200:
        quotes = r.json().get("quoteResponse", {}).get("result", [])
        es_price, es_change = "N/A", "N/A"
        nq_price, nq_change = "N/A", "N/A"
        for q in quotes:
            if q["symbol"] == "ES=F":
                es_price = q.get("regularMarketPrice", "N/A")
                es_change = q.get("regularMarketChangePercent", "N/A")
            elif q["symbol"] == "NQ=F":
                nq_price = q.get("regularMarketPrice", "N/A")
                nq_change = q.get("regularMarketChangePercent", "N/A")
        return f"S&P {es_price} ({es_change:.2f}%), Nasdaq {nq_price} ({nq_change:.2f}%)"
    return "N/A"

def get_usdinr():
    # USDINR from exchangerate-api.com (free tier)
    url = "https://open.er-api.com/v6/latest/USD"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        rate = data.get("rates", {}).get("INR", "N/A")
        return f"₹{rate:.2f}" if rate != "N/A" else "N/A"
    return "N/A"

def get_crude():
    # Crude price from Yahoo Finance (CL=F)
    url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=CL=F"
    r = requests.get(url)
    if r.status_code == 200:
        q = r.json().get("quoteResponse", {}).get("result", [])
        if q:
            price = q[0].get("regularMarketPrice", "N/A")
            change = q[0].get("regularMarketChangePercent", "N/A")
            return f"${price} ({change:.2f}%)"
    return "N/A"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram send error:", e)

def format_message():
    now = datetime.now().strftime('%H:%M %p')
    banknifty = get_banknifty()
    sgx = get_sgx_nifty()
    us_fut = get_us_futures()
    crude = get_crude()
    usdinr = get_usdinr()
    
    msg = f"""🕒 [{now}] *Market Pulse*
📉 BankNifty: {banknifty}
📊 SGX Nifty: {sgx}
🇺🇸 US Futures: {us_fut}
💹 Crude Oil: {crude} | USDINR: {usdinr}
📍 Support: 48100 | Resistance: 48450
💬 Sentiment: Mildly Bearish"""
    return msg

def main():
    while True:
        message = format_message()
        print(message)  # For local testing logs
        send_telegram_message(message)
        time.sleep(900)  # 15 minutes delay

if __name__ == "__main__":
    main()
