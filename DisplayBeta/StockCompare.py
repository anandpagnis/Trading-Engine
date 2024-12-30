import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import warnings
import time

# Global variables
fig = go.Figure()
st.title("Stock Comparison and Financial Metrics")
# Load tickers from CSV file
ticks = pd.read_csv('constituents.csv')
symbols = ticks['Symbol'].tolist()

# Suppress the FutureWarnings temporarily
warnings.simplefilter(action='ignore', category=FutureWarning)



# Function to fetch data from Yahoo Finance using yfinance
def fetch_data(symbol, interval='1d', period='1y'):
    valid_intervals = ['1m', '2m', '5m', '15m', '30m', '1h', '3h', '1d', '5d', '1wk', '1mo', '3mo']
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '5y', '10y']

    if interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m'] and period not in ['1d', '5d']:
        st.warning("Short intervals are only available for up to 7 days of data.")
        interval = '1d'

    if interval not in valid_intervals:
        raise ValueError(f"Invalid interval: {interval}")
    if period not in valid_periods:
        raise ValueError(f"Invalid period: {period}")

    df = yf.download(symbol, interval=interval, period=period)
    if df.empty:
        raise ValueError(f"No data found for {symbol}")

    df = df.reset_index()
    if 'Datetime' in df.columns:
        df.rename(columns={'Datetime': 'date'}, inplace=True)
    elif 'Date' in df.columns:
        df.rename(columns={'Date': 'date'}, inplace=True)

    df['date'] = pd.to_datetime(df['date'])
    df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'}, inplace=True)
    return df


# Select interval and period
interval = st.selectbox('Select Time Interval', ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1d', '5d', '1wk', '1mo', '3mo'])
period = st.selectbox('Select Data Period', ['1d', '5d', '1mo', '3mo', '6mo', '1y', '5y', '10y'])

# Function to update the sidebar
def update_sidebar(df1, df2=None):
    with st.sidebar:
        with st.expander(f"{symbol1} Data"):
            st.write(df1)
        if df2 is not None:
            with st.expander(f"{symbol2} Data"):
                st.write(df2)



# Main workflow
try:
    # First stock selection and data
    symbol1 = st.selectbox('Select First Stock Symbol', symbols)
    df1 = fetch_data(symbol1, interval=interval, period=period)
    update_sidebar(df1)  # Update the sidebar for the first stock

    # Add first stock to the figure
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df1['date'],
        open=df1['open'],
        high=df1['high'],
        low=df1['low'],
        close=df1['close'],
        name=f'{symbol1} Candlestick',
        increasing_line_color='green',
        decreasing_line_color='red'
    ))
    fig.update_layout(
        title=f"{symbol1} Candlestick Chart ({interval}, {period})",
        xaxis_title="Time",
        yaxis_title="Price",
        template="plotly_dark"
    )

    # Option to compare a second stock
    if st.checkbox("Compare with another stock"):
        symbol2 = st.selectbox('Select Second Stock Symbol', symbols)
        if symbol2:
            df2 = fetch_data(symbol2, interval=interval, period=period)
            fig.add_trace(go.Candlestick(
                x=df2['date'],
                open=df2['open'],
                high=df2['high'],
                low=df2['low'],
                close=df2['close'],
                name=f'{symbol2} Candlestick',
                increasing_line_color='blue',
                decreasing_line_color='orange'
            ))
            fig.update_layout(
                title=f"Comparison: {symbol1} vs {symbol2} ({interval}, {period})"
            )
            update_sidebar(df1, df2)  #

    # Display the chart
    st.plotly_chart(fig)

except Exception as e:
    st.error(f"Error: {e}")
