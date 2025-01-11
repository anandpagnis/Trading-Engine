import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import warnings
from datetime import datetime

# Suppress the FutureWarnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Page config
st.set_page_config(page_title="Stock Comparison Dashboard", layout="wide")
st.title("Stock Comparison Dashboard")

# Load tickers from CSV file
@st.cache_data  # Cache the data loading
def load_tickers():
    try:
        ticks = pd.read_csv('constituents.csv')
        return ticks['Symbol'].tolist()
    except FileNotFoundError:
        return ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']  # Fallback list

symbols = load_tickers()

# Function to fetch data from Yahoo Finance using yfinance
def fetch_data(symbol, interval='1d', period='1y'):
    valid_intervals = ['1m', '2m', '5m', '15m', '30m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    
    # Validate interval and period combinations
    if interval in ['1m', '2m', '5m', '15m', '30m'] and period not in ['1d', '5d', '7d']:
        st.warning(f"Interval {interval} only available for periods up to 7 days. Switching to daily interval.")
        interval = '1d'
    
    try:
        df = yf.download(symbol, interval=interval, period=period, progress=False)
        if df.empty:
            raise ValueError(f"No data found for {symbol}")
        
        # Reset index and handle date column
        df = df.reset_index()
        
        # Keep original column names
        if 'Adj Close' in df.columns:
            df['price'] = df['Adj Close']  # Create a new column for price data
        elif 'Close' in df.columns:
            df['price'] = df['Close']
        
        # Ensure date is datetime
        date_col = 'Date' if 'Date' in df.columns else 'Datetime'
        df['date'] = pd.to_datetime(df[date_col])
        
        return df
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()

# Function to fetch additional metrics
def fetch_additional_metrics(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        metrics = {
            'pe_ratio': info.get('trailingPE', None),
            'dividend_yield': info.get('dividendYield', None),
            'eps': info.get('trailingEps', None),
            'beta': info.get('beta', None)
        }
        
        # Convert None to 0 for numerical comparisons
        return {k: 0 if v is None else v for k, v in metrics.items()}
    except Exception as e:
        st.warning(f"Could not fetch metrics for {symbol}: {str(e)}")
        return {
            'pe_ratio': 0,
            'dividend_yield': 0,
            'eps': 0,
            'beta': 0
        }

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    interval = st.selectbox(
        'Select Time Interval',
        ['1d', '5d', '1wk', '1mo', '3mo'],
        index=0
    )
    
    period = st.selectbox(
        'Select Data Period',
        ['1mo', '3mo', '6mo', '1y', '2y', '5y'],
        index=3
    )

# Initialize metrics dictionaries
metrics1 = None
metrics2 = None

# Main content
try:
    col1, col2 = st.columns(2)
    
    with col1:
        symbol1 = st.selectbox('Select First Stock Symbol', symbols, key='symbol1')
        df1 = fetch_data(symbol1, interval=interval, period=period)
        if not df1.empty:
            metrics1 = fetch_additional_metrics(symbol1)
            st.write("### First Stock Metrics")
            metrics_df1 = pd.DataFrame([metrics1]).T
            metrics_df1.columns = ['Value']
            st.dataframe(metrics_df1)
    
    with col2:
        symbol2 = st.selectbox('Select Second Stock Symbol', symbols, key='symbol2')
        df2 = fetch_data(symbol2, interval=interval, period=period)
        if not df2.empty:
            metrics2 = fetch_additional_metrics(symbol2)
            st.write("### Second Stock Metrics")
            metrics_df2 = pd.DataFrame([metrics2]).T
            metrics_df2.columns = ['Value']
            st.dataframe(metrics_df2)

    # Only proceed with charts if we have both metrics
    if metrics1 and metrics2 and not df1.empty and not df2.empty:
        # Charts section
        st.write("## Charts")
        charts_to_show = st.multiselect(
            "Select charts to display",
            ["Price Trend", "Total Return", "P/E Ratio", "Dividend Yield", "Volatility (Beta)"],
            default=["Price Trend"]
        )

        if "Price Trend" in charts_to_show:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df1['date'],
                y=df1['price'],
                mode='lines',
                name=symbol1,
                line=dict(color='#00ff00')
            ))
            fig.add_trace(go.Scatter(
                x=df2['date'],
                y=df2['price'],
                mode='lines',
                name=symbol2,
                line=dict(color='#0000ff')
            ))
            fig.update_layout(
                title=f"Price Trend Comparison: {symbol1} vs {symbol2}",
                xaxis_title="Date",
                yaxis_title="Price",
                template="plotly_dark",
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)

        if "Total Return" in charts_to_show:
            total_return1 = ((df1['price'].iloc[-1] - df1['price'].iloc[0]) / df1['price'].iloc[0] * 100)
            total_return2 = ((df2['price'].iloc[-1] - df2['price'].iloc[0]) / df2['price'].iloc[0] * 100)

            fig = go.Figure(data=[
                go.Bar(
                    x=[symbol1, symbol2],
                    y=[total_return1, total_return2],
                    marker_color=['#00ff00', '#0000ff']
                )
            ])
            fig.update_layout(
                title="Total Return Comparison",
                yaxis_title="Total Return (%)",
                template="plotly_dark",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        # Metrics comparisons
        metrics_charts = {
            "P/E Ratio": ('pe_ratio', "P/E Ratio"),
            "Dividend Yield": ('dividend_yield', "Dividend Yield (%)"),
            "Volatility (Beta)": ('beta', "Beta")
        }

        for chart_name, (metric_key, ylabel) in metrics_charts.items():
            if chart_name in charts_to_show:
                val1 = metrics1[metric_key]
                val2 = metrics2[metric_key]
                
                # Convert dividend yield to percentage
                if metric_key == 'dividend_yield':
                    val1 = val1 * 100 if val1 else 0
                    val2 = val2 * 100 if val2 else 0
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=[symbol1, symbol2],
                        y=[val1, val2],
                        marker_color=['#00ff00', '#0000ff']
                    )
                ])
                fig.update_layout(
                    title=f"{chart_name} Comparison",
                    yaxis_title=ylabel,
                    template="plotly_dark",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")