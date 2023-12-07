import pandas as pd
import yfinance as yf
import os
import json
from datetime import datetime, timedelta

# Paths
path = 'C:/Users/Janet/OneDrive - The University of Chicago/Data_policy/final-project-janet'
data_path = r'C:\Users\Janet\OneDrive - The University of Chicago\Data_policy\final-project-janet\data'
cache_directory = os.path.join(path, 'cache')
file_name = 'processed_text.csv'
file_path = os.path.join(path, data_path)
os.makedirs(cache_directory, exist_ok=True)  # Create cache directory if it doesn't exist
df = pd.read_csv(file_path)

def initialize_dates():
    event_date = datetime(2018, 6, 28)  # date of CCPA being signed
    estimation_window_start = event_date - timedelta(days=365)
    estimation_window_end = event_date - timedelta(days=30)
    event_window_start = event_date - timedelta(days=10)
    event_window_end = event_date + timedelta(days=10)
    return estimation_window_start, estimation_window_end, event_window_start, event_window_end

def check_cached_data(ticker, start_date, end_date):
    """
    Check if the data for a given ticker is available in the cache.
    """
    cache_file_path = os.path.join(cache_directory, f'{ticker}.csv')
    if os.path.exists(cache_file_path):
        cached_data = pd.read_csv(cache_file_path, index_col='Date', parse_dates=True)
        if cached_data.index.min() <= start_date and cached_data.index.max() >= end_date:
            return cached_data
    return None

def fetch_stock_data(ticker, start_date, end_date):
    """
    Fetch stock data, using cached data if available.
    """
    cached_data = check_cached_data(ticker, start_date, end_date)
    if cached_data is not None:
        return cached_data

    try:
        stock = yf.Ticker(ticker)
        adj_close_data = yf.download(ticker, start=start_date, end=end_date)
        dividend_data = stock.history(start=start_date, end=end_date)

        # Save downloaded data to cache
        adj_close_data.to_csv(os.path.join(cache_directory, f'{ticker}.csv'))

        return adj_close_data, dividend_data, stock
    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return None, None, None

def process_stock_data(ticker, adj_close_data, dividend_data, stock):
    if adj_close_data.empty or dividend_data.empty:
        return None

    adj_close_data.index = adj_close_data.index.tz_localize(None)
    dividend_data.index = dividend_data.index.tz_localize(None)
    historical_data = pd.merge(adj_close_data, dividend_data[['Dividends']], left_index=True, right_index=True, how='left')
    historical_data['ticker'] = ticker
    market_cap = stock.info.get('marketCap', 'N/A')
    historical_data['marketCap'] = market_cap
    return historical_data

def rename_and_merge_dataframes(combined_data, market_data):
    combined_data = combined_data.rename(columns={
        'Adj Close': 'stock_adj_close',
        'Volume': 'stock_volume',
        'Open': 'stock_open',
        'High': 'stock_high',
        'Low': 'stock_low',
        'Close': 'stock_close',
        'Dividends': 'dividends',
        'marketCap': 'stock_market_cap'
    }).rename_axis('date')
    market_data = market_data.rename_axis('date')
    return pd.merge(combined_data, market_data, left_index=True, right_index=True, how='left')

def load_sp500_data():
    json_file_name = 'sp500_constituents.json'
    json_file_path = os.path.join(sp500_path, json_file_name)
    with open(json_file_path, 'r') as file:
        sp500_data = json.load(file)
    return sp500_data.get("2018/06/20", [])

def main(df):
    estimation_start, estimation_end, event_start, event_end = initialize_dates()
    stock_list = df['ticker'].unique()
    combined_data = pd.DataFrame()

    for ticker in stock_list:
        adj_close_data, dividend_data, stock = fetch_stock_data(ticker, estimation_start, event_end)
        historical_data = process_stock_data(ticker, adj_close_data, dividend_data, stock)
        if historical_data is not None:
            combined_data = pd.concat([combined_data, historical_data])

    market_index_ticker = '^GSPC'
    market_data = yf.download(market_index_ticker, start=estimation_start, end=event_end)[['Adj Close']].rename(columns={'Adj Close': 'market_adj_close'})
    merged_data = rename_and_merge_dataframes(combined_data, market_data)

    sp500_tickers = load_sp500_data()
    merged_data['sp500'] = merged_data['ticker'].apply(lambda x: 1 if x in sp500_tickers else 0)

    df_no_duplicates = df[~df.duplicated('ticker', keep=False)]
    merged_data.reset_index(inplace=True)
    final_data = pd.merge(merged_data, df_no_duplicates, on='ticker', how='left')
    final_data.set_index('date', inplace=True)

    # Save final data to the specified path
    output_file_path = os.path.join(data_path, 'combined_stock_data.csv')
    final_data.to_csv(output_file_path, index=False)
    return final_data

final_data = main(df)
