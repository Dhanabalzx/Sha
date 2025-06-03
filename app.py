import streamlit as st
from nsepython import nse_eq, nsefetch
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Function to calculate Bollinger Bands
def bollinger_bands(df, window=20, num_std=2):
    df['MA20'] = df['Close'].rolling(window=window).mean()
    df['STD20'] = df['Close'].rolling(window=window).std()
    df['Upper'] = df['MA20'] + (num_std * df['STD20'])
    df['Lower'] = df['MA20'] - (num_std * df['STD20'])
    return df

# Function to check if price touched bands and reversed
def check_band_touch(df):
    results = []
    for i in range(1, len(df)):
        prev = df.iloc[i-1]
        curr = df.iloc[i]

        # Touched Upper Band and reversed down
        touched_upper = (prev['Close'] <= prev['Upper']) and (curr['Close'] > curr['Upper']) and (curr['Close'] < prev['Close'])

        # Touched Lower Band and reversed up
        touched_lower = (prev['Close'] >= prev['Lower']) and (curr['Close'] < curr['Lower']) and (curr['Close'] > prev['Close'])

        # Touched Middle Band and reversed (crossing MA20)
        touched_middle_up = (prev['Close'] < prev['MA20']) and (curr['Close'] >= curr['MA20'])
        touched_middle_down = (prev['Close'] > prev['MA20']) and (curr['Close'] <= curr['MA20'])

        if touched_upper:
            results.append('Touched Upper and Reversed Down')
        elif touched_lower:
            results.append('Touched Lower and Reversed Up')
        elif touched_middle_up:
            results.append('Touched Middle and Reversed Up')
        elif touched_middle_down:
            results.append('Touched Middle and Reversed Down')
        else:
            results.append(None)
    results.insert(0, None)  # first day no data to compare
    df['Signal'] = results
    return df

st.title("NSE Top 500 Stocks Bollinger Band Watchlist")

# Select date input for analysis
selected_date = st.date_input("Select date to check:", datetime.today())

# Fetch NSE top 500 stocks symbols
with st.spinner('Fetching NSE top 500 symbols...'):
    eq_data = nse_eq()
    symbols = [item['symbol'] for item in eq_data['data']][:500]

st.write(f"Total symbols fetched: {len(symbols)}")

watchlist = []

with st.spinner('Processing stock data, this may take a few minutes...'):
    for symbol in symbols:
        try:
            ticker = symbol + ".NS"  # Yahoo Finance NSE ticker format
            df = yf.download(ticker, period="60d", interval="1d", progress=False)
            if df.empty:
                continue
            
            # Calculate Bollinger Bands
            df = bollinger_bands(df)
            df = check_band_touch(df)

            # Check if selected date in df index
            date_str = selected_date.strftime('%Y-%m-%d')
            if date_str in df.index.strftime('%Y-%m-%d'):
                row = df.loc[date_str]
                if row['Signal'] is not None:
                    watchlist.append({
                        'Symbol': symbol,
                        'Date': date_str,
                        'Signal': row['Signal'],
                        'Close': row['Close'],
                        'Upper': row['Upper'],
                        'Middle': row['MA20'],
                        'Lower': row['Lower']
                    })
        except Exception as e:
            # Optional: print(f"Error with {symbol}: {e}")
            continue

if watchlist:
    df_watchlist = pd.DataFrame(watchlist)
    st.dataframe(df_watchlist)
else:
    st.write("No stocks matched the criteria on the selected date.")

