
import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from datetime import date

st.set_page_config(layout="wide", page_title="AI Stock Dashboard", page_icon="📈")

st.title("📈 AI Stock Dashboard (Simplified)")

# Sidebar for user input
st.sidebar.header("Input Options")
ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL")
start_date = st.sidebar.date_input("Start Date", value=date(2022, 1, 1))
end_date = st.sidebar.date_input("End Date", value=date.today())

# Fetch data
@st.cache_data
def load_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data

if ticker:
    data = load_data(ticker, start_date, end_date)
    if not data.empty:
        st.subheader(f"Stock Price for {ticker} from {start_date} to {end_date}")

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Candlestick'
        ))
        fig.update_layout(title=f"{ticker} Price Chart", xaxis_title="Date", yaxis_title="Price", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data found. Please check the ticker symbol.")
