import streamlit as st
from nsepython import nse_eq, nse_fetch
import yfinance as yf
import pandas as pd

st.title("NSE Top 500 Stocks - Basic Dashboard")

# Step 1: Fetch Top 500 NSE symbols
with st.spinner("Fetching NSE top 500 symbols..."):
    eq_data = nse_eq()
    symbols = [item['symbol'] for item in eq_data['data']][:500]

st.write(f"Total stocks fetched: {len(symbols)}")

# Optional: input filter for symbols
search_text = st.text_input("Search symbol or company name (case insensitive):").strip().upper()

# Container for fundamental + price data
stocks_data = []

with st.spinner("Fetching fundamentals and price data... This can take a while..."):
    for symbol in symbols:
        try:
            # Fetch fundamentals from nsepython
            fund_data = nse_fetch(f"quote-equity?symbol={symbol}")

            # Fetch recent price data from yfinance (last close)
            ticker = symbol + ".NS"
            yf_data = yf.Ticker(ticker)
            hist = yf_data.history(period="5d")
            last_close = hist['Close'][-1] if not hist.empty else None
            volume = hist['Volume'][-1] if not hist.empty else None

            # Basic fundamental metrics from nse_fetch response
            market_cap = fund_data.get('marketCap', None)
            pe_ratio = fund_data.get('PE', None)
            name = fund_data.get('companyName', symbol)

            if search_text and search_text not in symbol and search_text not in str(name).upper():
                continue

            stocks_data.append({
                "Symbol": symbol,
                "Name": name,
                "Market Cap": market_cap,
                "PE Ratio": pe_ratio,
                "Last Close": last_close,
                "Volume": volume,
            })
        except Exception as e:
            # Optional: st.write(f"Error fetching data for {symbol}: {e}")
            continue

# Create DataFrame and display
df = pd.DataFrame(stocks_data)
st.dataframe(df)

# TODO: Add button or UI to proceed to Step 2 (technical strategy)

