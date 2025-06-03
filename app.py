# app.py
import streamlit as st
import pandas as pd
from nsepython import *
from datetime import datetime

st.set_page_config(page_title="NSE Watchlist Screener", layout="wide")

st.title("📊 NSE Watchlist Screener - PRS2 / PRR2 Logic")

# Date input
selected_date = st.date_input("Select Date", datetime.today()).strftime('%d-%m-%Y')

st.info(f"Fetching data for {selected_date}...")

# Get list of NSE stocks
def get_all_nse_stocks():
    data = nse_eq()
    return list(data['data']['data'].keys())

# Fetch daily OHLC for stock
def fetch_ohlc(stock_symbol):
    try:
        df = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={stock_symbol}&section=trade_info")
        candles = df['priceInfo']
        open_ = candles['open']
        high = candles['intraDayHighLow']['max']
        low = candles['intraDayHighLow']['min']
        close = candles['lastPrice']
        return open_, high, low, close
    except:
        return None

# Screening logic
def screen_stock(symbol):
    try:
        o, h, l, c = fetch_ohlc(symbol)
        prs2 = round(o - (h - l), 2)
        prr2 = round(o + (h - l), 2)
        mid = round((prs2 + prr2) / 2, 2)

        upper = h >= prr2
        lower = l <= prs2
        mid_reversal = l <= mid <= h and c != mid

        return symbol, upper, lower, mid_reversal
    except:
        return None

# Load all stocks
symbols = nse_eq()["data"]
touched_upper = []
touched_lower = []
midline_reversal = []

for item in symbols:
    symbol = item["symbol"]
    result = screen_stock(symbol)
    if result:
        sym, upper, lower, mid_rev = result
        if upper:
            touched_upper.append(sym)
        if lower:
            touched_lower.append(sym)
        if mid_rev:
            midline_reversal.append(sym)

# Display results
st.subheader("📈 Touched PRR2 (Upper Line)")
st.write(touched_upper)

st.subheader("📉 Touched PRS2 (Lower Line)")
st.write(touched_lower)

st.subheader("🔁 Touched Midline and Reversed")
st.write(midline_reversal)

