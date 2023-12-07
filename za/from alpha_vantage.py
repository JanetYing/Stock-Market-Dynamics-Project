import requests
import pandas as pd

def get_earnings_data(api_key, symbol):
    url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()

    # Process the data
    if 'quarterlyEarnings' in data:
        earnings_data = pd.DataFrame(data['quarterlyEarnings'])
        # Filter for 2019 Q4 data
        q4_2019_data = earnings_data[earnings_data['fiscalDateEnding'].str.startswith('2019-12')]
        return q4_2019_data
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data is found

def get_earnings_for_stock_list(api_key, stock_list):
    earnings_data = {}
    for symbol in stock_list:
        earnings_data[symbol] = get_earnings_data(api_key, symbol)
    return earnings_data

api_key = 'T93CUDNTXS8JQUGE'  # Replace with your Alpha Vantage API Key
stock_list = ['AAPL', 'AMZN', 'MSFT', 'GOOGL', 'FB', 'BRK.A', 'JPM','TSLA','PG']  # Stock list without duplicates

earnings_data = get_earnings_for_stock_list(api_key, stock_list)

# Display the data
for symbol, data in earnings_data.items():
    print(f"Earnings data for {symbol} in Q4 2019:")
    print(data)
    print("\n")

