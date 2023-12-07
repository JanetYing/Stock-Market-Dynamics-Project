import pandas as pd
import numpy as np
import yfinance as yf
import os
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy.stats import t
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns


import numpy as np

import matplotlib.dates as mdates
# Import the functions from analysis.py

from analysis import (
    calculate_stock_and_market_return,
    estimate_parameters,
    calculate_expected_return,
    calculate_abnormal_return,
    calculate_volume_difference,
)

path = 'C:/Users/Janet/OneDrive - The University of Chicago/Data_policy/final-project-janet'
file_name = 'combined_stock_data.csv'
file_path = os.path.join(path, file_name)
stock_data = pd.read_csv(file_path)

# stock_data = calculate_stock_and_market_return(stock_data)

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
    plt.figure(figsize=(15, 6) if study_type == 'volume' else (10, 6))

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

        # not plot the confidence interval for improving readability, but the significance of 
        #event's impact would reuqire more attention in future analysis
        sns.lineplot(data=mean_data, x=mean_data.index, y='mean', marker='o', label=label)

    plt.axhline(0, color='grey', linestyle='--')
    plt.axvline(0, color='red', lw=1, ls='--')  # Zero now represents the event date
    plt.title(f'Average {("Abnormal Returns" if study_type == "price" else "Volume Difference")} across {group_by.capitalize()} around the CCPA Signing')
    plt.xlabel('Days from CCPA Signing')
    plt.ylabel(f'Average {("Abnormal Return" if study_type == "price" else "Volume Difference")}')
    plt.xticks(rotation=45)
    plt.legend(title=group_by.capitalize())
    plt.tight_layout()
    plt.show()


# Perform Event Study and Plot
stock_data['date'] = pd.to_datetime(stock_data['date'])

# Perform Event Study and Plot
event_date = datetime(2018, 6, 28)
group_by = 'exchange'

# Ensure the 'date' column is of datetime type in your DataFrame
stock_data = calculate_stock_and_market_return(stock_data)

grouped_price_event_data = grouped_event_study(stock_data, 'price', event_date, group_by)
plot_grouped_event_study(grouped_price_event_data, 'price', event_date, group_by)

grouped_volume_event_data = grouped_event_study(stock_data, 'volume', event_date, group_by)
plot_grouped_event_study(grouped_volume_event_data, 'volume', event_date, group_by)



# def event_study(data, study_type, event_date, window_size=10, estimation_window_size=30):
#     """
#     Performs an event study for either stock price or stock volume.
#     """

#     # Convert 'date' column to datetime once for efficiency
#     data['date'] = pd.to_datetime(data['date'])

#     # Define the event and estimation windows
#     start_date = event_date - timedelta(days=window_size)
#     end_date = event_date + timedelta(days=window_size)
#     estimation_start_date = start_date - timedelta(days=estimation_window_size)
#     estimation_end_date = start_date - timedelta(days=1)

#     # Filter data for the event and estimation windows
#     event_window_data = data[(data['date'] >= start_date) & (data['date'] <= end_date)].copy()
#     estimation_window_data = data[(data['date'] >= estimation_start_date) & (data['date'] <= estimation_end_date)].copy()

#     if study_type == 'price':
#         # Check if 'market_return' column exists
#         if 'market_return' not in data.columns:
#             print("Error: 'market_return' column not found in the data.")
#             return None

#         # Perform event study for stock price
#         data = calculate_stock_and_market_return(data)  # Calculate stock and market returns
#         parameters = {ticker: estimate_parameters(ticker, data) for ticker in data['ticker'].unique()}
#         event_window_data = calculate_abnormal_return(event_window_data, parameters)

#     elif study_type == 'volume':
#         # Perform event study for stock volume
#         event_window_data = calculate_volume_difference(event_window_data, estimation_window_data)

#     return event_window_data

# def plot_event_study(event_window_data, study_type, event_date):
#     """
#     Plots the results of an event study for stock volume or stock price.
#     """
#     # Determine the column to use based on study type
#     column = 'volume_difference' if study_type == 'volume' else 'abnormal_return'

#     # Calculate mean and confidence interval
#     grouped_data = event_window_data.groupby('date')[column]
#     mean_data = grouped_data.mean()
#     sem_data = grouped_data.std() / np.sqrt(grouped_data.count())
#     ci = 1.96 * sem_data

#     mean_data = mean_data.to_frame('mean')
#     mean_data['lower_ci'] = mean_data['mean'] - ci
#     mean_data['upper_ci'] = mean_data['mean'] + ci

#     # Plotting
#     plt.figure(figsize=(15, 6) if study_type == 'volume' else (10, 6))
#     plt.fill_between(mean_data.index, mean_data['lower_ci'], mean_data['upper_ci'], color='gray' if study_type == 'volume' else 'blue', alpha=0.3)
#     sns.lineplot(data=mean_data, x=mean_data.index, y='mean', marker='o')

#     plt.axhline(0, color='grey', linestyle='--')
#     plt.axvline(mdates.date2num(event_date), color='red', lw=1, ls='--')  # Event date line
#     plt.title('Average ' + ('Abnormal Returns' if study_type == 'price' else 'Volume Difference') + ' around the Event Date (with 95% CI)')
#     plt.xlabel('Date')
#     plt.ylabel('Average ' + ('Abnormal Return' if study_type == 'price' else 'Volume Difference'))
#     plt.xticks(rotation=45)
#     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
#     plt.gca().xaxis.set_major_locator(mdates.DayLocator())
#     plt.tight_layout()
#     plt.show()


# # Load data
# path = 'C:/Users/Janet/OneDrive - The University of Chicago/Data_policy/final-project-janet'
# file_name = 'combined_stock_data.csv'
# file_path = os.path.join(path, file_name)
# stock_data = pd.read_csv(file_path)

# event_date = datetime(2018, 6, 28)
# group_by = 'industry'

# # Ensure the 'date' column is of datetime type in your DataFrame
# stock_data = calculate_stock_and_market_return(stock_data)
# grouped_price_event_data = event_study(stock_data, 'price', event_date, window_size=10, estimation_window_size=30)
# plot_event_study(grouped_price_event_data, 'price', event_date)

# # Perform event study for stock volume and plot
# grouped_volume_event_data = event_study(stock_data, 'volume', event_date, window_size=10, estimation_window_size=30)
# plot_event_study(grouped_volume_event_data, 'volume', event_date)