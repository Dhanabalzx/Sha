import streamlit as st
from nsepython import nsefetch
import yfinance as yf
import pandas as pd
import datetime
from typing import List

st.set_page_config(page_title="NSE Daily PRS2/PRR2 Watchlist", layout="wide")

@st.cache_data(ttl=3600)
def load_symbols() -> List[str]:
    eq = nsefetch("equity")
    if isinstance(eq, dict) and 'data' in eq:
        symbols = [item['symbol'] + ".NS" for item in eq['data'][:500]]  # add ".NS" suffix for yfinance NSE tickers
        return symbols
    else:
        st.error("Failed to fetch symbols or unexpected response structure from NSE API.")
        return []

def calculate_prs_prr(df: pd.DataFrame):
    """
    Calculates PRS2, PRR2, and middle line based on your provided logic.
    Example logic for demonstration - adjust formulas as per your exact specs.
    """
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    # Your predictive range formula (example placeholders)
    prs2 = close + (high - low) * 0.5  # Replace with your exact PRS2 formula
    prr2 = close - (high - low) * 0.5  # Replace with your exact PRR2 formula
    middle = (prs2 + prr2) / 2

    return prs2, prr2, middle

def check_touch_and_reversal(df: pd.DataFrame, prs2: pd.Series, prr2: pd.Series, middle: pd.Series):
    """
    For the selected day, check if the price touched or reversed from PRS2, PRR2, or middle line.
    Returns True/False for each condition.
    """
    # Take last row - the selected day
    day = df.iloc[-1]
    # For reversal, check if price moved towards then away from the line within the day or compared to prior day close
    # This is a simplified example, customize logic as per your exact rules.

    touched_prs2 = day['High'] >= prs2.iloc[-1]
    reversed_prs2 = day['High'] >= prs2.iloc[-1] and day['Close'] < prs2.iloc[-1]

    touched_prr2 = day['Low'] <= prr2.iloc[-1]
    reversed_prr2 = day['Low'] <= prr2.iloc[-1] and day['Close'] > prr2.iloc[-1]

    touched_middle = (day['Low'] <= middle.iloc[-1] <= day['High'])
    reversed_middle = (day['Low'] <= middle.iloc[-1] <= day['High']) and abs(day['Close'] - middle.iloc[-1]) > abs(day['Open'] - middle.iloc[-1])

    return {
        "Touched_PRS2": touched_prs2,
        "Reversed_PRS2": reversed_prs2,
        "Touched_PRR2": touched_prr2,
        "Reversed_PRR2": reversed_prr2,
        "Touched_Middle": touched_middle,
        "Reversed_Middle": reversed_middle
    }

@st.cache_data(ttl=3600)
def fetch_data(symbol: str, start_date: datetime.date, end_date: datetime.date) -> pd.DataFrame:
    df = yf.download(symbol, start=start_date, end=end_date, progress=False)
    return df

def main():
    st.title("NSE Top 500 Stocks Daily PRS2/PRR2 Watchlist")
    
    symbols = load_symbols()
    if not symbols:
        st.stop()

    selected_date = st.date_input("Select Date", datetime.date.today())
    st.write(f"Analyzing for date: {selected_date}")

    start_date = selected_date - datetime.timedelta(days=10)  # buffer days to have data for calculation
    end_date = selected_date + datetime.timedelta(days=1)

    watchlist = []

    with st.spinner(f"Fetching and analyzing data for {len(symbols)} stocks... This may take some minutes."):

        for symbol in symbols:
            df = fetch_data(symbol, start_date, end_date)
            if df.empty or selected_date not in df.index:
                continue

            df = df.loc[:selected_date]  # only data up to selected_date

            prs2, prr2, middle = calculate_prs_prr(df)

            signals = check_touch_and_reversal(df, prs2, prr2, middle)

            if any(signals.values()):
                watchlist.append({
                    "Symbol": symbol.replace(".NS", ""),
                    **signals
                })

    if watchlist:
        df_watchlist = pd.DataFrame(watchlist)
        st.dataframe(df_watchlist)
    else:
        st.info("No stocks touched or reversed at PRS2, PRR2 or middle line on selected date.")

if __name__ == "__main__":
    main()
