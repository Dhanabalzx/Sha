import streamlit as st
import yfinance as yf
import pandas as pd

# Supertrend calculation fix with NaN handling
def calculate_supertrend(df, period=7, multiplier=3):
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    # ATR calculation (simple approximation)
    atr = df['High'].rolling(window=period).max() - df['Low'].rolling(window=period).min()
    atr = atr.rolling(window=period).mean()
    
    hl2 = (high + low) / 2
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)

    supertrend = [True] * len(df)

    start_idx = period * 2  # skip initial NaNs for rolling

    for i in range(start_idx, len(df)):
        # Handle NaN values gracefully
        if pd.isna(upperband.iloc[i-1]) or pd.isna(lowerband.iloc[i-1]) or pd.isna(close.iloc[i]):
            supertrend[i] = supertrend[i-1]
            continue

        if close.iloc[i] > upperband.iloc[i-1]:
            supertrend[i] = True
        elif close.iloc[i] < lowerband.iloc[i-1]:
            supertrend[i] = False
        else:
            supertrend[i] = supertrend[i-1]

    # Fill early values with True (or you can decide another default)
    for i in range(start_idx):
        supertrend[i] = True

    return supertrend[-1]

# Calculate PRS2 and PRR2 based on pivot points
def calculate_pivot_points(df):
    high = df['High'].iloc[-2]
    low = df['Low'].iloc[-2]
    close = df['Close'].iloc[-2]

    pivot = (high + low + close) / 3
    R1 = 2 * pivot - low
    S1 = 2 * pivot - high
    R2 = pivot + (high - low)
    S2 = pivot - (high - low)
    return S2, R2

def get_signal(df):
    prs2, prr2 = calculate_pivot_points(df)
    supertrend = calculate_supertrend(df)

    last_close = df['Close'].iloc[-1]

    if last_close <= prs2 and supertrend:
        return "Buy"
    elif last_close >= prr2 and not supertrend:
        return "Sell"
    else:
        return "Hold"

def main():
    st.title("NSE 100 Stocks Screener: PRS2/PRR2 + Supertrend Strategy")

    # Load list of NSE 100 stocks - minimal list example; replace with full list or dynamic source
    stocks = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "KOTAKBANK.NS", "HINDUNILVR.NS", "SBIN.NS", "AXISBANK.NS", "LT.NS"
    ]

    selected_stocks = st.multiselect("Select Stocks to Screen", stocks, default=stocks[:5])

    buy_list = []
    sell_list = []
    hold_list = []

    for stock in selected_stocks:
        df = yf.download(stock, period="15d", interval="1d")  # 15 days for pivot + supertrend calculation
        if df.empty or len(df) < 10:
            st.warning(f"No sufficient data for {stock}")
            continue

        signal = get_signal(df)
        if signal == "Buy":
            buy_list.append(stock)
        elif signal == "Sell":
            sell_list.append(stock)
        else:
            hold_list.append(stock)

    st.subheader("Buy Signals")
    st.write(buy_list if buy_list else "No Buy Signals")

    st.subheader("Sell Signals")
    st.write(sell_list if sell_list else "No Sell Signals")

    st.subheader("Hold Signals")
    st.write(hold_list if hold_list else "No Hold Signals")

if __name__ == "__main__":
    main()
