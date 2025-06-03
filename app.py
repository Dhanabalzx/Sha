import streamlit as st
from nsepython import nsefetch
import pandas as pd
from datetime import datetime, timedelta

st.title("NSE Predictive Range Watchlist")

# Load top 500 symbols once and cache
@st.cache_data(ttl=3600)
def load_symbols():
    eq = nsefetch("equity")  # fetch all equity symbols from NSE (may take time)
    symbols = [item['symbol'] for item in eq['data'][:500]]  # top 500 stocks
    return symbols

symbols = load_symbols()

selected_date = st.date_input("Select Date", datetime.today())

# We want previous trading day for PR calculations
def prev_trading_day(date):
    prev_day = date - timedelta(days=1)
    # For simplicity, assume prev_day is trading day (can enhance with holiday calendar)
    return prev_day

prev_date = prev_trading_day(selected_date)

def fetch_ohlc(symbol, date):
    """Fetch OHLC data for symbol on given date using nsefetch 'historical' endpoint."""
    # Date format for NSE API: 'dd-mm-yyyy'
    date_str = date.strftime("%d-%m-%Y")
    try:
        df = nsefetch(f"historical/{symbol}/{date_str}/{date_str}")
        if 'data' in df and len(df['data']) > 0:
            record = df['data'][0]
            return {
                'open': float(record['openPrice']),
                'high': float(record['dayHigh']),
                'low': float(record['dayLow']),
                'close': float(record['closePrice'])
            }
    except Exception as e:
        pass
    return None

st.info(f"Fetching and calculating for {len(symbols)} stocks, please wait...")

watchlist = []

for symbol in symbols:
    prev_data = fetch_ohlc(symbol, prev_date)
    today_data = fetch_ohlc(symbol, selected_date)
    if prev_data and today_data:
        prev_high = prev_data['high']
        prev_low = prev_data['low']
        prev_close = prev_data['close']
        today_open = today_data['open']
        today_high = today_data['high']
        today_low = today_data['low']
        today_close = today_data['close']

        range_ = prev_high - prev_low
        PRS2 = prev_low - 0.5 * range_
        PRR2 = prev_high + 0.5 * range_
        middle_line = (PRS2 + PRR2) / 2

        # Check touched upper and reversed
        touched_upper_reversed = today_high >= PRR2 and today_close < PRR2

        # Check touched lower and reversed
        touched_lower_reversed = today_low <= PRS2 and today_close > PRS2

        # Check touched middle and reversed (close crossed middle line opposite to open)
        touched_middle = today_high >= middle_line and today_low <= middle_line
        crossed_middle_reversed = False
        if touched_middle:
            if (today_open > middle_line and today_close < middle_line) or (today_open < middle_line and today_close > middle_line):
                crossed_middle_reversed = True

        if touched_upper_reversed or touched_lower_reversed or crossed_middle_reversed:
            watchlist.append({
                "Symbol": symbol,
                "PRS2": round(PRS2, 2),
                "PRR2": round(PRR2, 2),
                "Middle": round(middle_line, 2),
                "Touched Upper & Reversed": touched_upper_reversed,
                "Touched Lower & Reversed": touched_lower_reversed,
                "Touched Middle & Reversed": crossed_middle_reversed,
                "Date": selected_date.strftime("%Y-%m-%d")
            })

if watchlist:
    df_watchlist = pd.DataFrame(watchlist)
    st.write(f"### Watchlist for {selected_date.strftime('%Y-%m-%d')}")
    st.dataframe(df_watchlist)
else:
    st.write("No stocks matched the criteria for the selected date.")

