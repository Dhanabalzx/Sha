import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go

st.set_page_config(page_title="NSE Stock Daily Strategy", layout="wide")

st.title("NSE Stock Daily Strategy Dashboard")
st.markdown("Enter any NSE stock symbol (e.g. RELIANCE.NS, TCS.NS) to see indicators and buy/sell signals based on your strategy.")

ticker = st.text_input("Enter NSE stock symbol (example: RELIANCE.NS)", "RELIANCE.NS")

@st.cache_data(ttl=3600)
def get_data(ticker):
    data = yf.download(ticker, period="1y", interval="1d")
    data.dropna(inplace=True)
    return data

def ATR(df, n=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(n).mean()
    return atr

def supertrend(df, period=10, multiplier=3):
    atr = ATR(df, period)
    hl2 = (df['High'] + df['Low']) / 2
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)

    supertrend = pd.Series(index=df.index)
    direction = pd.Series(index=df.index)

    for i in range(len(df)):
        if i == 0:
            supertrend.iloc[i] = upperband.iloc[i]
            direction.iloc[i] = True
        else:
            prev_supertrend = supertrend.iloc[i-1]
            prev_close = df['Close'].iloc[i-1]

            if df['Close'].iloc[i] > prev_supertrend:
                supertrend.iloc[i] = max(lowerband.iloc[i], prev_supertrend)
                direction.iloc[i] = True
            else:
                supertrend.iloc[i] = min(upperband.iloc[i], prev_supertrend)
                direction.iloc[i] = False
    return supertrend, direction

def RSI(df, period=14):
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def MACD(df, fast=12, slow=26, signal=9):
    exp1 = df['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['Close'].ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def BollingerBands(df, n=20):
    sma = df['Close'].rolling(n).mean()
    std = df['Close'].rolling(n).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return upper_band, lower_band

def calculate_predictive_ranges(df):
    high = df['High']
    low = df['Low']
    close = df['Close']

    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)

    df['PRS2'] = s2
    df['PRR2'] = r2

    return df

data = get_data(ticker)

if data.empty:
    st.error("No data found for this ticker. Please check the symbol and try again.")
    st.stop()

data['ATR'] = ATR(data)
data['Supertrend'], data['ST_direction'] = supertrend(data)
data['RSI'] = RSI(data)
data['MACD'], data['MACD_signal'], data['MACD_hist'] = MACD(data)
data['BB_upper'], data['BB_lower'] = BollingerBands(data)
data = calculate_predictive_ranges(data)

data['Buy_Signal'] = ((data['Close'] > data['PRS2']) & (data['Close'].shift() <= data['PRS2'].shift()))
data['Sell_Signal'] = ((data['Close'] < data['PRR2']) & (data['Close'].shift() >= data['PRR2'].shift()))

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name='OHLC'))

fig.add_trace(go.Scatter(x=data.index, y=data['PRS2'], line=dict(color='green', dash='dot'), name='PRS2 (Support)'))
fig.add_trace(go.Scatter(x=data.index, y=data['PRR2'], line=dict(color='red', dash='dot'), name='PRR2 (Resistance)'))

fig.add_trace(go.Scatter(x=data.index, y=data['Supertrend'], line=dict(color='blue', width=1), name='Supertrend'))

fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], line=dict(color='orange', width=1), name='BB Upper'))
fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], line=dict(color='orange', width=1), name='BB Lower'))

buy_signals = data[data['Buy_Signal']]
fig.add_trace(go.Scatter(
    x=buy_signals.index,
    y=buy_signals['Close'],
    mode='markers',
    marker=dict(symbol='triangle-up', color='green', size=12),
    name='Buy Signal'))

sell_signals = data[data['Sell_Signal']]
fig.add_trace(go.Scatter(
    x=sell_signals.index,
    y=sell_signals['Close'],
    mode='markers',
    marker=dict(symbol='triangle-down', color='red', size=12),
    name='Sell Signal'))

fig.update_layout(
    title=f"{ticker} Daily Chart with Strategy Signals",
    xaxis_title="Date",
    yaxis_title="Price (INR)",
    xaxis_rangeslider_visible=False,
    template='plotly_white'
)

st.plotly_chart(fig, use_container_width=True)

latest = data.iloc[-1]

st.markdown("### Latest Indicators & Signals")
st.write({
    "Date": latest.name.date(),
    "Close Price": round(latest['Close'], 2),
    "ATR": round(latest['ATR'], 2),
    "Supertrend": round(latest['Supertrend'], 2),
    "Supertrend Direction": "Uptrend" if latest['ST_direction'] else "Downtrend",
    "RSI": round(latest['RSI'], 2),
    "MACD": round(latest['MACD'], 4),
    "MACD Signal": round(latest['MACD_signal'], 4),
    "Bollinger Upper": round(latest['BB_upper'], 2),
    "Bollinger Lower": round(latest['BB_lower'], 2),
    "PRS2 (Support)": round(latest['PRS2'], 2),
    "PRR2 (Resistance)": round(latest['PRR2'], 2),
    "Buy Signal": bool(latest['Buy_Signal']),
    "Sell Signal": bool(latest['Sell_Signal']),
})

st.markdown("### Recent Buy/Sell Signals")
recent_signals = data[(data['Buy_Signal'] | data['Sell_Signal'])].tail(5)[
    ['Close', 'Buy_Signal', 'Sell_Signal']]
st.dataframe(recent_signals.style.applymap(lambda x: 'color: green' if x else 'color: red'))

st.markdown("""
---
*This tool is built to demonstrate a daily strategy dashboard using Python and Streamlit, applying multiple technical indicators on NSE stock data fetched via yfinance.*
""")
