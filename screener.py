import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

# Parameters
STOCK_LIST = [
    "RELIANCE.NS", "INFY.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "LT.NS", "KOTAKBANK.NS",
    "SBIN.NS", "HINDUNILVR.NS", "ITC.NS", "AXISBANK.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "HCLTECH.NS", "WIPRO.NS", "SUNPHARMA.NS", "ULTRACEMCO.NS", "POWERGRID.NS", "ONGC.NS", "COALINDIA.NS",
    "NTPC.NS", "TITAN.NS", "NESTLEIND.NS", "TECHM.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "ADANIENT.NS",
    "ADANIPORTS.NS", "BPCL.NS", "BHARTIARTL.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS",
    "CIPLA.NS", "DIVISLAB.NS", "DRREDDY.NS", "BRITANNIA.NS", "HDFCLIFE.NS", "ICICIPRULI.NS", "SBILIFE.NS",
    "BAJAJFINSV.NS", "M&M.NS", "GRASIM.NS", "HINDALCO.NS", "VEDL.NS", "AMBUJACEM.NS", "SHREECEM.NS",
    "DABUR.NS", "PIDILITIND.NS", "GODREJCP.NS", "TATACONSUM.NS", "UBL.NS", "COLPAL.NS", "BERGEPAINT.NS",
    "DMART.NS", "LICI.NS", "ZOMATO.NS", "PAYTM.NS", "IRCTC.NS", "BEL.NS", "HAL.NS", "NAUKRI.NS",
    "POLYCAB.NS", "ABB.NS", "LUPIN.NS", "PAGEIND.NS", "INDIGO.NS", "ADANIGREEN.NS", "INDUSINDBK.NS",
    "SRF.NS", "CHOLAFIN.NS", "IDFCFIRSTB.NS", "BANKBARODA.NS", "CANBK.NS", "FEDERALBNK.NS", "PNB.NS",
    "UNIONBANK.NS", "IEX.NS", "MCX.NS", "HAVELLS.NS", "TORNTPHARM.NS", "GLAND.NS", "BOSCHLTD.NS",
    "CONCOR.NS", "BANDHANBNK.NS", "RECLTD.NS", "BHEL.NS", "IOB.NS", "INDIANB.NS", "AUBANK.NS",
    "YESBANK.NS", "RBLBANK.NS", "JINDALSTEL.NS", "TVSMOTOR.NS", "ATGL.NS", "ICICIGI.NS", "MFSL.NS",
    "PFC.NS", "GAIL.NS", "ADANIPOWER.NS"
]

# Supertrend Indicator
def calculate_supertrend(df, period=10, multiplier=3):
    df['ATR'] = df['High'].rolling(window=period).max() - df['Low'].rolling(window=period).min()
    df['Upper Basic'] = (df['High'] + df['Low']) / 2 + multiplier * df['ATR']
    df['Lower Basic'] = (df['High'] + df['Low']) / 2 - multiplier * df['ATR']

    df['Supertrend'] = df['Close']
    for i in range(period, len(df)):
        if df['Close'][i] > df['Upper Basic'][i-1]:
            df.loc[df.index[i], 'Supertrend'] = df['Lower Basic'][i]
        elif df['Close'][i] < df['Lower Basic'][i-1]:
            df.loc[df.index[i], 'Supertrend'] = df['Upper Basic'][i]
        else:
            df.loc[df.index[i], 'Supertrend'] = df['Supertrend'][i-1]
    return df

# PRS2 and PRR2 logic
def calculate_pr_levels(df):
    recent = df.iloc[-1]
    high = recent['High']
    low = recent['Low']
    close = recent['Close']
    prr2 = high + (high - low) * 0.618
    prs2 = low - (high - low) * 0.618
    return prr2, prs2

st.title("📈 NSE 100 Stock Screener - PRS2/PRR2 + Supertrend")
st.caption("Auto-refreshes every 15 minutes. Signals are not financial advice.")

screen_data = []
progress = st.progress(0)

for i, stock in enumerate(STOCK_LIST):
    try:
        df = yf.download(stock, period="5d", interval="15m", progress=False)
        df.dropna(inplace=True)
        df = calculate_supertrend(df)
        prr2, prs2 = calculate_pr_levels(df)
        current = df.iloc[-1]
        signal = ""
        
        # Buy signal: price crosses above PRS2 and above Supertrend
        if current['Close'] > prs2 and current['Close'] > current['Supertrend']:
            signal = "BUY"

        screen_data.append({
            "Symbol": stock.replace(".NS", ""),
            "LTP": round(current['Close'], 2),
            "PRS2": round(prs2, 2),
            "PRR2": round(prr2, 2),
            "Supertrend": round(current['Supertrend'], 2),
            "Signal": signal
        })

    except Exception as e:
        print(f"Error processing {stock}: {e}")

    progress.progress((i+1)/len(STOCK_LIST))

screener_df = pd.DataFrame(screen_data)
screener_df = screener_df[screener_df['Signal'] == 'BUY']

st.success(f"{len(screener_df)} stocks meet PRS2 + Supertrend buy criteria")
st.dataframe(screener_df, use_container_width=True)
