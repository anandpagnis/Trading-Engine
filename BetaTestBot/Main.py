import yfinance as yf
import pandas as pd
import time
import matplotlib.pyplot as plt
import numpy as np
import Actions as act 

# Parameters
symbol = "AAPL"
window_size = 60  # Moving Average window
trade_limit = 10  # Limit on active trades
trade_count = 0  # Initialize trade count
portfolio = []  # Keep track of active trades

# Fetch stock data from Yahoo Finance
def fetch_stock_data(symbol):
    years = 15
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.DateOffset(years=years)
    df = yf.download(symbol, start=start_date, end=end_date)
    print(df)
    
    return df

# Calculate Moving Average
def calculate_moving_average(df, window_size):
    df["SMA"] = df["Close"].rolling(window=window_size).mean()
    print(df["SMA"])
    return df

# Determine buy/sell signal based on SMA strategy
def determine_trade_signal(df):
    if len(df) < window_size:
        return None 
    recent_close = df.iloc[-1]["Close"]
    recent_sma = df.iloc[-1]["SMA"]
    if pd.isna(recent_sma): 
        return "None"
    if recent_close > recent_sma:
        return "BUY"
    elif recent_close < recent_sma:
        return "SELL"
    else:
        return "None"

def trading_bot(symbol, window_size, trade_limit):
    global trade_count, portfolio
    df = fetch_stock_data(symbol)
    df = calculate_moving_average(df, window_size)

    while True:
        act.auto_get_stock(symbol)
        df = fetch_stock_data(symbol)  
        df = calculate_moving_average(df, window_size)
        print("calculated...")
        signal = determine_trade_signal(df)
        print(f"Signal: {signal}")

        if signal == "BUY" and trade_count < trade_limit:
            act.exec_trade(symbol)
            print(f"{symbol} bought")
            portfolio.append(symbol)
            trade_count += 1

        elif signal == "SELL" and symbol in portfolio:
            act.sell_trade(symbol)
            print(f"{symbol} sold")
            portfolio.remove(symbol)
            trade_count -= 1

        else:
            print("No trade executed or trade limit reached.")

        print(f"Active Trades: {portfolio}")
        time.sleep(20)  # Wait before the next trade

# Run the bot
trading_bot(symbol, window_size, trade_limit)
