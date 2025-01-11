import yfinance as yf
import pandas as pd
import time
import matplotlib.pyplot as plt
import numpy as np
import Actions as act

# Parameters
symbol = "AAPL"
window_size = 5  # Set to a smaller value for quick calculations
trade_limit = 3  # A smaller trade limit for testing
trade_count = 0  # Start with no trades
portfolio = {"holdings": 0, "symbols": []}  # Initialize portfolio as dictionary
first_run = False  # Flag to track first execution change to true to view bot execution feature for fetching current holding straight from portfolio has not been implemented yet 

def fetch_stock_data(symbol):
    years = 10
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.DateOffset(years=years)
    df = yf.download(symbol, start=start_date, end=end_date)
    return df

def calculate_moving_average(df, window_size):
    df["SMA"] = df["Close"].rolling(window=window_size).mean()
    return df

def determine_trade_signal(df, is_first_run=False):
    print(is_first_run)
    if is_first_run:
        print("First run - executing initial BUY signal")
        return "BUY"

    if len(df) < window_size:
        return None
    
    # Convert Series to scalar values using .iloc[-1].item()
    recent_close = df["Close"].iloc[-1].item() if isinstance(df["Close"].iloc[-1], pd.Series) else df["Close"].iloc[-1]
    recent_sma = df["SMA"].iloc[-1].item() if isinstance(df["SMA"].iloc[-1], pd.Series) else df["SMA"].iloc[-1]
    
    print(f"Recent Close: {recent_close}, Recent SMA: {recent_sma}")
    
    # Check if recent_sma is NaN
    if pd.isna(recent_sma):
        print("SMA is NaN, insufficient data to determine trade signal")
        return "HODL"
        
    # Compare the scalar values
    if recent_close > recent_sma:
        return "BUY"
    elif recent_close < recent_sma:
        return "SELL"
    else:
        return "HODL"

def trading_bot(symbol, window_size, trade_limit):
    global trade_count, portfolio, first_run
    
    while True:
        try:
            act.auto_get_stock(symbol)
            df = fetch_stock_data(symbol)
            df = calculate_moving_average(df, window_size)
            print("calculated...")
            
            # Pass first_run flag to determine_trade_signal
            signal = determine_trade_signal(df, is_first_run=first_run)
            print(f"Signal: {signal}")
            
            # Set first_run to False after first execution
            if first_run:
                first_run = False
            
            if signal == "BUY" and trade_count < trade_limit:
                if portfolio["holdings"] < trade_limit:
                    act.exec_trade(symbol)
                    print(f"{symbol} bought")
                    portfolio["symbols"].append(symbol)
                    portfolio["holdings"] += 1
                    trade_count += 1
                else:
                    print("Trade limit reached, cannot execute BUY")
                    
            elif signal == "SELL" and symbol in portfolio["symbols"]:
                if portfolio["holdings"] > 0:
                    print("Executing SELL trade")
                    act.sell_trade(symbol)
                    print(f"{symbol} sold")
                    portfolio["symbols"].remove(symbol)
                    portfolio["holdings"] -= 1
                else:
                    print("Portfolio empty, cannot execute SELL")
            else:
                print("No trade executed or trade limit reached.")
                
            print(f"Active Trades: {portfolio}")
            time.sleep(20)  # Wait before the next trade
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            time.sleep(20)  # Wait before retrying

# Run the bot
if __name__ == "__main__":
    trading_bot(symbol, window_size, trade_limit)