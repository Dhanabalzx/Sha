import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Function to calculate PRS2 and PRR2 (Pivot Range Support/Resistance 2)
def calculate_pr_levels(df):
    pivot = (df['High'] + df['Low'] + df['Close']) / 3
    r2 = pivot + (pivot - df['Low']) * 1.5
    s2 = pivot - (df['High'] - pivot) * 1.5
    return s2.iloc[-1], r2.iloc[-1]

# Function to calculate Supertrend
def calculate_supertrend(df, period=7, multiplier=3):
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    atr = df['High'].rolling(window=period).max() - df['Low'].rolling(window=period).min()
    atr = atr.rolling(window=period).mean()
    
    hl2 = (high + low) / 2
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)

    supertrend = [True] * len(df)
    for i in range(1, len(df)):
        if close.iloc[i] > upperband.iloc[i-1]:
            supertrend[i] = True
        elif close.iloc[i] < lowerband.iloc[i-1]:
            supertrend[i] = False
        else:
            supertrend[i] = supertrend[i-1]
    
    return supertrend[-1]  # Return latest supertrend value: True=Uptrend, False=Downtrend

# Function to fetch data from yfinance
@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    try:
        df = yf.download(ticker, period='20d', interval='1d', progress=False)
        if df.empty:
            return None
        return df
    except Exception as e:
        st.error(f"Error downloading data for {ticker}: {e}")
        return None

def main():
    st.title("NSE Stock Screener - PRS2/PRR2 + Supertrend")

    # List of sample NSE stocks (replace with full NSE100 later)
    stock_list = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "KOTAKBANK.NS", "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS"
    ]

    st.write(f"Total stocks in screener: {len(stock_list)}")

    buy_list = []
    sell_list = []

    for stock in stock_list:
        df = get_stock_data(stock)
        if df is None or df.empty:
            st.warning(f"No data for {stock}")
            continue

        # Calculate PRS2 and PRR2
        prs2, prr2 = calculate_pr_levels(df)

        close = df['Close'].iloc[-1]

        # Calculate supertrend (True=Uptrend, False=Downtrend)
        supertrend = calculate_supertrend(df)

        # Debug info (uncomment to see all)
        # st.write(f"{stock}: Close={close:.2f}, PRS2={prs2:.2f}, PRR2={prr2:.2f}, Supertrend={'Up' if supertrend else 'Down'}")

        # Buy condition: Close between PRS2 and PRR2 and supertrend up
        if prs2 < close < prr2 and supertrend:
            buy_list.append(stock)

        # Sell condition: Close between PRS2 and PRR2 and supertrend down
        elif prs2 < close < prr2 and not supertrend:
            sell_list.append(stock)

    # Show summary
    st.success(f"Buy Signals: {len(buy_list)} | Sell Signals: {len(sell_list)}")

    if len(buy_list) == 0 and len(sell_list) == 0:
        st.info("No stocks currently meet Buy/Sell criteria.")

    # Show watchlists
    if buy_list:
        st.subheader("Buy Watchlist")
        for b in buy_list:
            st.write(b)

    if sell_list:
        st.subheader("Sell Watchlist")
        for s in sell_list:
            st.write(s)

if __name__ == "__main__":
    main()
