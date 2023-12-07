import pandas as pd
import seaborn as sns
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import statsmodels.api as sm
import os

path = 'C:/Users/Janet/OneDrive - The University of Chicago/Data_policy/final-project-janet'
file_name = 'combined_stock_data.csv'
file_path = os.path.join(path, file_name)
stock_data = pd.read_csv(file_path)

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


def grouped_event_study(data, study_type, event_date, group_by, window_size=10, estimation_window_size=30):
    start_date = event_date - timedelta(days=window_size)
    end_date = event_date + timedelta(days=window_size)
    estimation_start_date = start_date - timedelta(days=estimation_window_size)
    estimation_end_date = start_date - timedelta(days=1)

    grouped_event_data = {}
    for group in data[group_by].unique():
        group_data = data[(data['date'] >= start_date) & (data['date'] <= end_date) & (data[group_by] == group)].copy()
        group_estimation_data = data[(data['date'] >= estimation_start_date) & (data['date'] <= estimation_end_date) & (data[group_by] == group)].copy()

        if group_data.empty:
            continue

        if study_type == 'price':
            parameters = {ticker: estimate_parameters(ticker, group_data) for ticker in group_data['ticker'].unique()}
            group_data = calculate_abnormal_return(group_data, parameters)

        elif study_type == 'volume':
            group_data = calculate_volume_difference(group_data, group_estimation_data)

        grouped_event_data[group] = group_data

    return grouped_event_data




def plot_grouped_event_study(grouped_data, study_type, event_date, group_by):
    column = 'volume_difference' if study_type == 'volume' else 'abnormal_return'

    # Create figure and axes using plt.subplots()
    fig, ax = plt.subplots(figsize=(15, 6) if study_type == 'volume' else (10, 6))

    # Define sector names for nicer labeling
    sector_names = {'businessConsumer_services': 'Business Consumer Services',
                    'technology': 'Technology'}

    for group, group_data in grouped_data.items():
        # Convert the dates to a number format and find the relative date difference
        group_data['date_num'] = mdates.date2num(pd.to_datetime(group_data['date']))
        event_date_num = mdates.date2num(event_date)
        group_data['days_from_event'] = (group_data['date_num'] - event_date_num).round()

        mean_data = group_data.groupby('days_from_event')[column].mean().to_frame('mean')

        label = sector_names.get(group, group) if group_by == 'sector' else group

        # Plot the data on the axes object
        sns.lineplot(data=mean_data, x=mean_data.index, y='mean', marker='o', label=label, ax=ax)

    ax.axhline(0, color='grey', linestyle='--')
    ax.axvline(0, color='red', lw=1, ls='--')  # Zero now represents the event date
    ax.set_title(f'Average {("Abnormal Returns" if study_type == "price" else "Volume Difference")} across {group_by.capitalize()} around the CCPA Signing')
    ax.set_xlabel('Days from CCPA Signing')
    ax.set_ylabel(f'Average {("Abnormal Return" if study_type == "price" else "Volume Difference")}')
    ax.tick_params(axis='x', rotation=45)
    ax.legend(title=group_by.capitalize())
    plt.tight_layout()

    return ax
# stock_data = pd.read_csv('combined_stock_data.csv')

stock_data['date'] = pd.to_datetime(stock_data['date'])

event_date = datetime(2018, 6, 28)
group_by = 'exchange'
study_type = 'volume'

# Ensure the 'date' column is of datetime type in your DataFrame
stock_data = calculate_stock_and_market_return(stock_data)

grouped_price_event_data = grouped_event_study(stock_data, study_type, event_date, group_by)
plot_grouped_event_study(grouped_price_event_data, study_type, event_date, group_by)


# stock_data['date'] = pd.to_datetime(stock_data['date'])

# # Perform Event Study and Plot
# event_date = datetime(2018, 6, 28)
# group_by = 'exchange'

# # Ensure the 'date' column is of datetime type in your DataFrame
# stock_data = calculate_stock_and_market_return(stock_data)

# grouped_price_event_data = grouped_event_study(stock_data, 'price', event_date, group_by)
# plot_grouped_event_study(grouped_price_event_data, 'price', event_date, group_by)

# grouped_volume_event_data = grouped_event_study(stock_data, 'volume', event_date, group_by)
# plot_grouped_event_study(grouped_volume_event_data, 'volume', event_date, group_by)

