import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

path = 'C:/Users/Janet/OneDrive - The University of Chicago/Data_policy/final-project-janet/data'
file_name = 'combined_stock_data.csv'
file_path = os.path.join(path, file_name)
df = pd.read_csv(file_path)



def plot_correlation_heatmap(df, columns):


    # Select the relevant columns
    selected_data = df[columns]

    # Compute the correlation matrix
    correlation_matrix = selected_data.corr()

    # Update column names for readability
    formatted_columns = [col.replace('_', ' ').title() for col in correlation_matrix.columns]
    correlation_matrix.columns = formatted_columns
    correlation_matrix.index = formatted_columns

    # Plot the heatmap
    plt.figure(figsize=(10, 10))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Heatmap of Stock Market Data Correlations')
    plt.xticks(rotation=45)
    plt.yticks(rotation=45)
    plt.show()

plot_correlation_heatmap(df, ['stock_open', 'stock_high', 'stock_low', 'stock_close', 
                 'stock_adj_close', 'stock_volume', 'dividends', 
                 'stock_market_cap', 'market_adj_close'])

#interpretation of plot
# Liquidity and Market Participation: Larger companies with higher market caps often have a greater number 
# of shares available for trading, which can lead to higher trading volumes due to increased liquidity. 
# More market participants (like institutional investors) are likely to trade these stocks, as they are 
# generally perceived as less risky compared to smaller-cap companies.

# Information Availability: Companies with large market capitalizations often have more visibility and 
# analyst coverage. This increased attention can lead to higher trading volumes as investors react to news,
# earnings reports, and other information.





def plot_stacked_exchange_industry():
    exchange_industry_count = df.groupby(['exchange', 'industry']).size().unstack(fill_value=0)
    exchange_industry_percentage = (exchange_industry_count.div(exchange_industry_count.sum(axis=1), axis=0) * 100).fillna(0)

    # Update industry labels for readability
    exchange_industry_percentage.columns = [col.replace('_', ' ').title() for col in exchange_industry_percentage.columns]

    exchange_industry_percentage.plot(kind='bar', stacked=True, colormap='viridis', figsize=(10, 6))
    
    plt.title('Percentage Distribution of Stocks by Industry within Each Exchange')
    plt.xlabel('Exchange')
    plt.ylabel('Percentage')
    plt.legend(title='Industry', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    plt.show()

plot_stacked_exchange_industry()

# It meet my expectation of the characteristics of each exchange