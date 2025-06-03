import streamlit as st
import pandas as pd
import datetime
from nsepython import *
from nsepython.server import nsefetch
import yfinance as yf

st.set_page_config(layout="wide")
st.title("📊 Bank Nifty Daily Watchlist - PRR2/PRS2 Strategy")

# Load static list of NSE top 500 stocks
symbol_df = pd.read_csv("nse_top_500_symbols.csv")
symbols = symbol_df["Symbol"].tolist()

# User date selection
date_selected = st.date_input("Select a date to analyze", datetime.date.today())

# Parameters for PRS2 and PRR2 calculation
PR_MULTIPLIER = 0.618  # Can be made user-configurable later

# Lists to capture results
touched_upper = []
touched_lower = []
touched_middle_reversed = []

progress_bar = st.progress(0)
status_text = st.empty()

for i, symbol in enumerate(symbols):
    try:
        data = yf.download(f"{symbol}.NS", period="30d", interval="1d")
        if data.empty or date_selected.strftime('%Y-%m-%d') not in data.index.strftime('%Y-%m-%d'):
            continue

        row = data.loc[date_selected.strftime('%Y-%m-%d')]

        high = row['High']
        low = row['Low']
        close = row['Close']
        open_price = row['Open']

        pr_high = high + (high - low) * PR_MULTIPLIER
        pr_low = low - (high - low) * PR_MULTIPLIER
        middle = (pr_high + pr_low) / 2

        # Check your strategy conditions
        if high >= pr_high:
            touched_upper.append(symbol)
        elif low <= pr_low:
            touched_lower.append(symbol)
        elif (open_price < middle and close > middle) or (open_price > middle and close < middle):
            touched_middle_reversed.append(symbol)

    except Exception as e:
        continue
    progress_bar.progress((i + 1) / len(symbols))
    status_text.text(f"Processing {i+1}/{len(symbols)}: {symbol}")

progress_bar.empty()
status_text.empty()

st.subheader(f"Results for {date_selected.strftime('%d-%m-%Y')}")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📈 Touched Upper Line")
    st.write(touched_upper if touched_upper else "None")

with col2:
    st.markdown("### 📉 Touched Lower Line")
    st.write(touched_lower if touched_lower else "None")

with col3:
    st.markdown("### 🔄 Middle Line Reversal")
    st.write(touched_middle_reversed if touched_middle_reversed else "None")

st.success("Analysis complete. You may change the date to rerun.")
