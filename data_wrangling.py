import pandas as pd
import numpy as np
import yfinance as yf
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os
import json
from scipy.stats import t
from datetime import datetime, timedelta

path = os.path.join(os.getcwd(), 'data')
file_name = 'processed_text.csv'
file_path = os.path.join(os.getcwd(), 'data', file_name)
df = pd.read_csv(file_path)


def set_up():
    event_date = datetime(2018, 6, 28) # date of CCPA being signed
    estimation_window_start = event_date - timedelta(days=365)
    estimation_window_end = event_date - timedelta(days=30)
    event_window_start = event_date - timedelta(days=10)
    event_window_end = event_date + timedelta(days=10)
    stock_list = df['ticker'].unique()
    return estimation_window_start, estimation_window_end,event_window_start,event_window_end,stock_list

estimation_window_start, estimation_window_end,event_window_start,event_window_end,stock_list = set_up()


def data_retriving(use_local_data=False):
    combined_data = pd.DataFrame()

    if use_local_data: #skip download if data already downloaded
        final_data = 'stock_retrieved.csv'
        local_file_path = os.path.join(path, final_data)  
        if os.path.exists(local_file_path):
            return pd.read_csv(local_file_path)
        else:
            print("Local data file not found. Fetching data from the web.")

    for ticker in stock_list:
        try:
            stock = yf.Ticker(ticker)

            historical_data_adj_close = yf.download(ticker, start=estimation_window_start, end=event_window_end) #retrieve dataframe that include adj close column
            if historical_data_adj_close.empty:
                print(f"No data for {ticker} using yf.download for specified dates.")
                continue

            historical_data_dividend = stock.history(start=estimation_window_start, end=event_window_end) #retrieve dataframe that include dividend column
            if historical_data_dividend.empty:
                print(f"No data for {ticker} using stock.history for specified dates.")
                continue

            historical_data_adj_close.index = historical_data_adj_close.index.tz_localize(None)
            historical_data_dividend.index = historical_data_dividend.index.tz_localize(None)

            # Merge the two dataframes on their index since both are indexed by date when retrieved
            historical_data = pd.merge(historical_data_adj_close, historical_data_dividend[['Dividends']], left_index=True, right_index=True, how='left')

            historical_data['ticker'] = ticker

            info = stock.info
            market_cap = info.get('marketCap', 'N/A')
            historical_data['marketCap'] = market_cap

            combined_data = pd.concat([combined_data, historical_data])
            combined_data.to_csv(os.path.join(path, 'stock_retrieved.csv'))
        except Exception as e:
            print(f"Error processing {ticker}: {e}")  
    return combined_data
combined_data = data_retriving(use_local_data=True)


def merge_market_stock(combined_data, use_local_data=False):
    market_index_ticker = '^GSPC'  # S&P 500, market return, used to calculate the expected return for stock price

    market_data = None

    if use_local_data:
        local_market_data_path = os.path.join(path, 'market_data.csv')
        if os.path.exists(local_market_data_path):
            market_data = pd.read_csv(local_market_data_path)
        else:
            print("Local market data file not found. Fetching data from the web.")

    if not use_local_data or market_data is None:
        market_data = yf.download(market_index_ticker, start=estimation_window_start, end=event_window_end)
        
    market_data = yf.download(market_index_ticker, start=estimation_window_start, end=event_window_end)
    market_data = market_data[['Adj Close']].rename(columns={'Adj Close': 'market_adj_close'})
    market_data = market_data.rename_axis('date')
    market_data.to_csv(os.path.join(path, 'market_data.csv'))

    combined_data = combined_data.rename(columns={
        'Adj Close': 'stock_adj_close',
        'Volume': 'stock_volume',
        'Open': 'stock_open',
        'High': 'stock_high',
        'Low': 'stock_low',
        'Close': 'stock_close',
        'Dividends':'dividends',
        'marketCap':'stock_market_cap'
    })

    combined_data = combined_data.rename(columns={'Date': 'date'})
    combined_data['date'] = pd.to_datetime(combined_data['date'])
    combined_data = combined_data.set_index('date')

    merged_data = pd.merge(combined_data, market_data, left_index=True, right_index=True, how='left')
    return merged_data
merged_data = merge_market_stock(combined_data, use_local_data=True)


def merge_with_sp500(merged_data):

    json_file_name = 'sp500_constituents.json'
    json_file_path = os.path.join(path, json_file_name)
    with open(json_file_path, 'r') as file:
        sp500_data = json.load(file)
    sp500_tickers = sp500_data.get("2018/06/20", []) #extract sp500 constitutes list at the most recent date of event_date (2018/6/28)
    merged_data['sp500'] = merged_data['ticker'].apply(lambda x: 1 if x in sp500_tickers else 0)
    return merged_data
merged_data = merge_with_sp500(merged_data)


def merge_text_file():
    #remove all duplicates to make sure df is unique by ticker and also improve validity when doing further analysis 
    df_no_duplicates = df[~df.duplicated('ticker', keep=False)]

    if 'date' not in merged_data.columns:
        merged_data.reset_index(inplace=True)  

    final_data = pd.merge(merged_data, df_no_duplicates, on='ticker', how='left')

    if 'date' in final_data.columns and final_data.index.name != 'date':
        final_data.set_index('date', inplace=True)

    file_name = 'combined_stock_data.csv'
    full_file_path = os.path.join(path, file_name)
    final_data.to_csv(full_file_path)
merge_text_file()