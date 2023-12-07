import pandas as pd
import numpy as np
import statsmodels.api as sm
import numpy as np





# Utility Functions
def calculate_stock_and_market_return(data):
    data['stock_return'] = data.groupby('ticker')['stock_adj_close'].pct_change()
    data['market_return'] = data['market_adj_close'].pct_change()
    return data

def estimate_parameters(ticker, data):
    stock_data = data[data['ticker'] == ticker].dropna()
    if len(stock_data) < 2: 
        return np.nan, np.nan
    
    # Ensure that 'market_return' exists in stock_data
    if 'market_return' not in stock_data.columns:
        raise KeyError("Column 'market_return' not found in stock_data.")

    # Adding a constant to the independent variable for OLS regression
    X = sm.add_constant(stock_data['market_return'])

    model = sm.OLS(stock_data['stock_return'], X).fit()
    return model.params



def calculate_expected_return(row, params):
    alpha, beta = params.get(row['ticker'], (np.nan, np.nan))
    if pd.isna(alpha) or pd.isna(beta):  
        return np.nan
    return alpha + beta * row['market_return']

def calculate_abnormal_return(group_data, parameters):
    group_data['expected_return'] = group_data.apply(lambda row: calculate_expected_return(row, parameters), axis=1)
    group_data['abnormal_return'] = group_data['stock_return'] - group_data['expected_return']
    return group_data

def calculate_volume_difference(group_data, group_estimation_data):
    average_volume_estimation = group_estimation_data.groupby('ticker')['stock_volume'].mean()
    group_data = group_data.join(average_volume_estimation, on='ticker', rsuffix='_avg')
    group_data['volume_difference'] = group_data['stock_volume'] - group_data['stock_volume_avg']
    return group_data
