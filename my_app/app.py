from shiny import App, render, ui, reactive
import pandas as pd
import seaborn as sns
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


app_ui = ui.page_fluid(
    ui.row(
        ui.column(4, ui.output_image(id='logo'), style="padding-bottom:0px; margin-bottom:-250px"),
        ui.column(4, 
                  ui.h1('Yingying Cao Final Project'), 
                  ui.hr()),
        ui.column(4, 
                  ui.h1('PPHA 30538 Autumn 2023'),
                  ui.hr())
    ),
    # ui.row(
    #     ui.column(4, 
    #               ui.input_select(id='aspect', 
    #                               label='Please select the aspect of event study you want to focus on: ', 
    #                               choices=['Stock Price', 'Market Capitalization','Volume'])),
    #     ui.column(4, 
    #               ui.input_select(id='quantile', 
    #                               label='What percentile of'+ {input.aspect()}+'you want to work on', 
    #                               choices=['top percentil', 'middle percentile', 'low percentile'],
    #                               multiple=True))
    #     ui.column(4, 
    #         ui.input_select(id='subsection', 
    #                         label='How do you want to categorize them?', 
    #                         choices=['industry', 'sector']))
    # ),
        ui.row(
        ui.column(4, 
                  ui.input_select(id='xaxis', 
                                  label='Please select the x ', 
                                  choices=['Industry', 'Exchange'])),
        ui.column(4, 
                  ui.input_select(id='yaxis', 
                                  label='Please select the y', 
                                  choices=['Stock Price', 'Market Capitalization', 'Volume']))
        ),
    #     ui.row(
    #     ui.column(6, 
    #               ui.output_text('text'),
    #     offset=6)
    # ),
    ui.row(
        ui.column(12, 
                  ui.output_plot('sh'), 
                  align='center')
    )
)



def server(input, output, session):
    # @reactive.Calc
    # def get_data():
    #     df = pd.read_csv('combined_stock_data.csv')
        
    #     return df[df['Year'] == int(input.year())]
    
    @output
    @render.image
    def logo():
        return {
            'src': "my_app/harris_logo.png",
            'width': '300',  
            'height': 'auto'  
        }
        
    # @output
    # @render.text
    # def text():
    #     text_year = int(input.year())
    #     if text_year == 2005:
    #         return "The selected year is a BRAC year"
    #     else:
    #         return "The selected year is not a BRAC year"


    @output
    @render.plot
    def sh(log_scale='auto'):

        df = pd.read_csv('combined_stock_data.csv')
        
        x_axis_input = input.xaxis()
        y_axis_input = input.yaxis()

        # Mapping of user-friendly input values to DataFrame column names
        input_to_column = {
            'Stock Price': 'stock_adj_close',
            'Market Capitalization': 'stock_market_cap',
            'Volume': 'stock_volume',
            'Industry': 'industry',
            'Exchange': 'exchange'
        }

        x_axis = input_to_column.get(x_axis_input, x_axis_input)
        y_axis = input_to_column.get(y_axis_input, y_axis_input)
        hue = 'sector' if x_axis_input == 'Industry' else None


        palette_column = hue if x_axis_input == 'Industry' else x_axis
        palette = sns.color_palette("pastel", len(df[palette_column].unique()))
        palette = dict(zip(df[palette_column].unique(), palette))

        
        plt.figure(figsize=(15, 8))
        ax = sns.boxplot(x=x_axis, y=y_axis, hue=hue, data=df, palette=palette, dodge=False,showfliers=False)
        if x_axis_input == 'Industry': # Format the x-axis labels to be more readable
            ax.set_xticklabels([label.get_text().replace('_', ' ').title() for label in ax.get_xticklabels()])
        
        plt.title(f'Box-and-Whisker Plot of {y_axis_input.capitalize()} by {x_axis_input.capitalize()}')
        plt.ylabel(y_axis_input.capitalize())
        plt.xlabel(x_axis_input.capitalize())
        ax.xaxis.grid(False) # unfinished
        ax.yaxis.grid(True)
        plt.xticks(rotation=65)
        
        # Automatically determine y-axis scale for readability
        if log_scale == 'auto':
            if df[y_axis].min() > 0: 
                data_range = np.log10(df[y_axis].max()) - np.log10(df[y_axis].min())
                if data_range > 3:  # Use a log scale if data range is large
                    ax.set_yscale('log')
            else:
                # Add a small constant to zero values if present to use log scale
                df[y_axis] += df[y_axis].eq(0)
                ax.set_yscale('log')
                ax.set_ylim(bottom=1)  # Set the bottom of the y-axis to 1 to avoid negative values
        elif log_scale:
            ax.set_yscale('log')

        if df[y_axis].max() < 10000:
            ax.ticklabel_format(style='plain', axis='y')
            
        if hue:
            plt.legend(title=hue.capitalize())
    
        return ax


app = App(app_ui, server)

