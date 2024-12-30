import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import warnings
import time


st.title("Manage your account")
try:
    df = pd.read_csv('userdata.csv')
except FileNotFoundError:
    df = pd.DataFrame(columns=['Date', 'Ticker', 'Purchase Price', 'Quantity', 'Total'])

def add_data():
    date = st.date_input('Date')
    ticker = st.text_input('Ticker')
    purchase_price = st.number_input('Purchase Price')
    quantity = st.number_input('Quantity')
    total = purchase_price * quantity
    if st.button('Add Data'):
        # Append new row with the correct columns
        new_row = {
            'Date': date,
            'Ticker': ticker,
            'Purchase Price': purchase_price,
            'Quantity': quantity,
            'Total': total
        }
        global df
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv('userdata.csv', index=False)  
        st.success('Data added successfully!')


#Main Workflow

def determine_profit():
    df['P/L'] = 0.0 
    tickers = df['Ticker'].unique().tolist()
    data = yf.download(tickers, period='1d', group_by='ticker')
    
    for ticker in tickers:
        current_price = data[ticker]['Close'].iloc[-1]
        purchase_price = df[df['Ticker'] == ticker]['Purchase Price'].values[0]
        quantity = df[df['Ticker'] == ticker]['Quantity'].values[0]
        profit = (current_price - purchase_price) * quantity
        df.loc[df['Ticker'] == ticker, 'P/L'] = profit  # Update the Profit column

    styled_df = df.style.applymap(lambda x: 'color: green' if x > 0 else 'color: grey' if x == 0 else 'color: red', subset=['P/L'])
    st.dataframe(styled_df)
            
add_data()
if df.empty == False:
    print("DataFrame is empty")
    determine_profit()
