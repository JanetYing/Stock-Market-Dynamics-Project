from shiny import App, render, ui, reactive
import pandas as pd
import seaborn as sns
from datetime import datetime
import matplotlib.pyplot as plt


app_ui = ui.page_fluid(
    ui.row(
        ui.column(4, ui.output_image(id='logo'), style="padding-bottom:0px; margin-bottom:-250px"),
        ui.column(4, 
                  ui.h1('Yingying Cao Homework4'), 
                  ui.hr()),
        ui.column(4, 
                  ui.h1('PPHA 30538 Autumn 2023'),
                  ui.hr())
    ),
    ui.row(
        ui.column(6, 
                  ui.input_select(id='share', 
                                  label='Please select the employment share: ', 
                                  choices=['Military', 'Manufacturing'])),
        ui.column(6, 
                  ui.input_select(id='year', 
                                  label='Choose a year', 
                                  choices=[2005, 2006, 2007]))
    ),
        ui.row(
        ui.column(6, 
                  ui.output_text('text'),
        offset=6)
    ),
    ui.row(
        ui.column(12, 
                  ui.output_plot('sh'), 
                  align='center')
    )
)



def server(input, output, session):
    @reactive.Calc
    def get_data():
        df = pd.read_csv('df_withShare.csv')
        
        return df[df['Year'] == int(input.year())]
    
    @output
    @render.image
    def logo():
        return {
            'src': "my_app/harris_logo.png",
            'width': '300',  
            'height': 'auto'  
        }
        
    @output
    @render.text
    def text():
        text_year = int(input.year())
        if text_year == 2005:
            return "The selected year is a BRAC year"
        else:
            return "The selected year is not a BRAC year"


    @output
    @render.plot
    def sh():
        df = get_data()
        
        share = input.share()
   
        df['share_specific'] = df[share] / df['Total']
        quantile_one_third = df['share_specific'].quantile(1/3)
        quantile_two_thirds = df['share_specific'].quantile(2/3)
        
        df_lowest_quantile = df[(df['share_specific'] <= quantile_one_third) & (df['share_specific'] != 0)]
        df_middle_quantile = df[(df['share_specific'] > quantile_one_third) & (df['share_specific'] <= quantile_two_thirds)]
        df_top_quantile = df[df['share_specific'] > quantile_two_thirds]
        df_zero = df[(df['share_specific'].isnull()) | (df['share_specific'] == 0)]
        
        df_lowest_quantile = df_lowest_quantile.drop('MSA', axis=1).groupby('Date').mean()
        df_middle_quantile = df_middle_quantile.drop('MSA', axis=1).groupby('Date').mean()
        df_top_quantile = df_top_quantile.drop('MSA', axis=1).groupby('Date').mean()
        df_zero = df_zero.drop('MSA', axis=1).groupby('Date').mean()

        fig, ax = plt.subplots(1, 1, figsize=(12,6))
        ax.plot(df_top_quantile.index, df_top_quantile['Unemployment Rate'], 'b-', label='Top')
        ax.plot(df_middle_quantile.index, df_middle_quantile['Unemployment Rate'], 'r-', label='Middle')
        ax.plot(df_lowest_quantile.index, df_lowest_quantile['Unemployment Rate'], 'k-', label='Lowest')
        ax.plot(df_zero.index, df_zero['Unemployment Rate'], 'g-', label='None')
        ax.set_title('Mean Change in MSA Unemployment Rate')
    
        ax.legend(title='Share Quantile')

        return ax

app = App(app_ui, server)

