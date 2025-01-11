import yfinance as yf
import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Portfolio Analyzer", layout="wide")
st.title("Portfolio Analyzer")

# Initialize session state for portfolio DataFrame
if 'portfolio_df' not in st.session_state:
    st.session_state.portfolio_df = pd.DataFrame(columns=[
        'Symbol', 'Shares', 'Entry Price', 'Entry Date', 'Current Price', 
        'Position Value', 'Cost Basis', 'Gain/Loss', 'Return %', 'Weight %'
    ])

# Function to fetch current stock data
def update_stock_data(df):
    if df.empty:
        return df
    
    updated_df = df.copy()
    
    try:
        # Fetch current prices for all symbols at once
        symbols = updated_df['Symbol'].unique()
        current_prices = {}
        
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            current_prices[symbol] = ticker.history(period='1d')['Close'].iloc[-1]
        
        # Update DataFrame with new calculations
        updated_df['Current Price'] = updated_df['Symbol'].map(current_prices)
        updated_df['Position Value'] = updated_df['Shares'] * updated_df['Current Price']
        updated_df['Cost Basis'] = updated_df['Shares'] * updated_df['Entry Price']
        updated_df['Gain/Loss'] = updated_df['Position Value'] - updated_df['Cost Basis']
        updated_df['Return %'] = (updated_df['Gain/Loss'] / updated_df['Cost Basis']) * 100
        
        # Calculate portfolio weights
        total_value = updated_df['Position Value'].sum()
        updated_df['Weight %'] = (updated_df['Position Value'] / total_value) * 100
        
        return updated_df
    
    except Exception as e:
        st.error(f"Error updating stock data: {str(e)}")
        return df
    
def load_tickers():
    try:
        ticks = pd.read_csv('constituents.csv')
        return ticks['Symbol'].tolist()
    except FileNotFoundError:
        return ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']  # Fallback list
    
    
symbols=load_tickers()


# Sidebar for adding new positions
st.sidebar.header("Add New Position")
with st.sidebar.form("add_position"):
    symbol = st.selectbox('Select Stock Symbol', symbols, key='symbol1')
    shares = st.number_input("Number of Shares", min_value=1.0,step=1.0)
    entry_price = st.number_input("Entry Price", min_value=0.0)
    entry_date = st.date_input("Entry Date")
    
    submit_button = st.form_submit_button("Add Position")
    if submit_button and symbol and shares and entry_price:
        new_position = pd.DataFrame({
            'Symbol': [symbol],
            'Shares': [shares],
            'Entry Price': [entry_price],
            'Entry Date': [entry_date],
            'Current Price': [0],
            'Position Value': [0],
            'Total': [0],
            'Gain/Loss': [0],
            'Return %': [0],
            'Weight %': [0]
        })
        st.session_state.portfolio_df = pd.concat([st.session_state.portfolio_df, new_position], ignore_index=True)
        st.session_state.portfolio_df = update_stock_data(st.session_state.portfolio_df)

# Update portfolio data
if not st.session_state.portfolio_df.empty:
    st.session_state.portfolio_df = update_stock_data(st.session_state.portfolio_df)

# Display portfolio summary
if not st.session_state.portfolio_df.empty:
    st.header("Portfolio Summary")
    
    # Calculate summary metrics
    total_value = st.session_state.portfolio_df['Position Value'].sum()
    total_cost = st.session_state.portfolio_df['Cost Basis'].sum()
    total_gain = st.session_state.portfolio_df['Gain/Loss'].sum()
    total_return = (total_gain / total_cost) * 100
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Portfolio Value", f"${total_value:,.2f}")
    with col2:
        st.metric("Total Cost Basis", f"${total_cost:,.2f}")
    with col3:
        st.metric("Total Gain/Loss", f"${total_gain:,.2f}")
    with col4:
        st.metric("Total Return", f"{total_return:.2f}%")
    
    # Portfolio Analysis
    st.header("Portfolio Analysis")
    
    # Position details
    st.subheader("Position Details")
    
    # Allow sorting by any column
    sort_column = st.selectbox("Sort by:", st.session_state.portfolio_df.columns)
    sorted_df = st.session_state.portfolio_df.sort_values(by=sort_column, ascending=False)
    
    # Format DataFrame for display
    display_df = sorted_df.style.format({
        'Shares': '{:.2f}',
        'Entry Price': '${:.2f}',
        'Current Price': '${:.2f}',
        'Position Value': '${:.2f}',
        'Cost Basis': '${:.2f}',
        'Gain/Loss': '${:.2f}',
        'Return %': '{:.2f}%',
        'Weight %': '{:.2f}%'
    })
    
    st.dataframe(display_df, use_container_width=True)
    
    # Portfolio Statistics
    st.subheader("Portfolio Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Returns Summary")
        returns_summary = pd.DataFrame({
            'Metric': ['Best Performing', 'Worst Performing', 'Average Return'],
            'Symbol': [
                sorted_df.iloc[sorted_df['Return %'].argmax()]['Symbol'],
                sorted_df.iloc[sorted_df['Return %'].argmin()]['Symbol'],
                'Portfolio Average'
            ],
            'Return %': [
                sorted_df['Return %'].max(),
                sorted_df['Return %'].min(),
                sorted_df['Return %'].mean()
            ]
        })
        st.dataframe(returns_summary.style.format({
            'Return %': '{:.2f}%'
        }))
    
    with col2:
        st.write("Diversification Summary")
        diversification = pd.DataFrame({
            'Metric': ['Number of Positions', 'Largest Position', 'Smallest Position'],
            'Value': [
                len(sorted_df),
                f"{sorted_df.iloc[sorted_df['Weight %'].argmax()]['Symbol']} ({sorted_df['Weight %'].max():.2f}%)",
                f"{sorted_df.iloc[sorted_df['Weight %'].argmin()]['Symbol']} ({sorted_df['Weight %'].min():.2f}%)"
            ]
        })
        st.dataframe(diversification)
    
    # Add delete functionality
    st.subheader("Edit Portfolio")
    position_to_delete = st.selectbox("Select position to delete:", sorted_df['Symbol'])
    if st.button("Delete Selected Position"):
        st.session_state.portfolio_df = st.session_state.portfolio_df[
            st.session_state.portfolio_df['Symbol'] != position_to_delete
        ]
        st.experimental_rerun()

else:
    st.info("Add positions to your portfolio using the sidebar form.")

# Add cache cleanup
if st.button("Clear Portfolio"):
    st.session_state.portfolio_df = pd.DataFrame(columns=[
        'Symbol', 'Shares', 'Entry Price', 'Entry Date', 'Current Price', 
        'Position Value', 'Cost Basis', 'Gain/Loss', 'Return %', 'Weight %'
    ])
    st.experimental_rerun()