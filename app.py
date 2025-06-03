import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

st.title("NSE Predictive Range Watchlist")

@st.cache_data(ttl=86400)
def load_symbols():
    try:
        df = pd.read_csv("nse_top_symbols.csv")
        symbols = df['symbol'].tolist()
        return symbols
    except Exception as e:
        st.error(f"Failed to load symbols CSV: {e}")
        return []

def fetch_daily_data(symbol, start_date, end_date):
    try:
        data = yf.download(symbol, start=start_date, end=end_date, interval="1d", progress=False)
        return data
    except Exception as e:
        st.error(f"Failed to fetch data for {symbol}: {e}")
        return pd.DataFrame()

def calculate_predictive_ranges(df):
    """
    Your predictive range logic based on daily OHLC:
    Assuming your logic is:
    - PRS2 = Close - 0.03*Close (3% below close)
    - PRR2 = Close + 0.03*Close (3% above close)
    - Middle line = Close

    You can replace this logic with your exact formulas.
    """
    df = df.copy()
    df['PRS2'] = df['Close'] * 0.97
    df['PRR2'] = df['Close'] * 1.03
    df['Middle'] = df['Close']
    return df

def check_touches_and_reversals(df, check_date):
    """
    For the given date (check_date), check if:
    - price touched upper line (PRR2) and reversed (closed below PRR2)
    - price touched lower line (PRS2) and reversed (closed above PRS2)
    - price touched middle line and reversed

    We can define "touched" as High >= line or Low <= line
    "Reversed" means price moves back away from line by close price relative position.
    """
    row = df.loc[df.index == check_date]
    if row.empty:
        return None  # no data for this date

    row = row.iloc[0]

    touched_upper = (row['High'] >= row['PRR2']) and (row['Close'] < row['PRR2'])
    touched_lower = (row['Low'] <= row['PRS2']) and (row['Close'] > row['PRS2'])
    touched_middle = ((row['High'] >= row['Middle']) and (row['Close'] < row['Middle'])) or \
                     ((row['Low'] <= row['Middle']) and (row['Close'] > row['Middle']))

    result = []
    if touched_upper:
        result.append('Touched Upper Line and Reversed')
    if touched_lower:
        result.append('Touched Lower Line and Reversed')
    if touched_middle:
        result.append('Touched Middle Line and Reversed')

    if not result:
        return None
    return ', '.join(result)

# Load symbols from CSV
symbols = load_symbols()
if not symbols:
    st.stop()

# User input for date
selected_date = st.date_input("Select date for watchlist", datetime.today())
selected_date_str = selected_date.strftime('%Y-%m-%d')

st.write(f"Generating watchlist for {selected_date_str}...")

# We will fetch data from one day before selected_date to selected_date to ensure data is available
start_date = (selected_date - timedelta(days=5)).strftime('%Y-%m-%d')
end_date = (selected_date + timedelta(days=1)).strftime('%Y-%m-%d')

results = []

progress_bar = st.progress(0)
total = len(symbols)

for idx, symbol in enumerate(symbols):
    data = fetch_daily_data(symbol, start_date, end_date)
    if data.empty or selected_date not in data.index:
        progress_bar.progress((idx + 1) / total)
        continue

    data = calculate_predictive_ranges(data)
    res = check_touches_and_reversals(data, selected_date)
    if res:
        results.append({'Symbol': symbol, 'Signal': res})

    progress_bar.progress((idx + 1) / total)

if results:
    df_results = pd.DataFrame(results)
    st.success(f"Found {len(results)} stocks matching criteria on {selected_date_str}:")
    st.dataframe(df_results)
else:
    st.info(f"No stocks touched and reversed on lines for {selected_date_str}")

