# Import library
import numpy as np
import pandas as pd
import requests
import math
from scipy import stats
import xlsxwriter

#Importando a lista de ações
stocks = pd.read_csv('sp_500_stocks.csv')
from secrets import IEX_CLOUD_API_TOKEN


hqm_columns = [
                'Ticker', 
                'Price', 
                'Number of Shares to Buy', 
                'One-Year Price Return', 
                'One-Year Return Percentile',
                'Six-Month Price Return',
                'Six-Month Return Percentile',
                'Three-Month Price Return',
                'Three-Month Return Percentile',
                'One-Month Price Return',
                'One-Month Return Percentile',
                'HQM Score'
                ]

hqm_dataframe = pd.DataFrame(columns = hqm_columns)

for symbol_string in symbol_strings:
#     print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        hqm_dataframe = hqm_dataframe.append(
                                        pd.Series([symbol, 
                                                   data[symbol]['quote']['latestPrice'],
                                                   'N/A',
                                                   data[symbol]['stats']['year1ChangePercent'],
                                                   'N/A',
                                                   data[symbol]['stats']['month6ChangePercent'],
                                                   'N/A',
                                                   data[symbol]['stats']['month3ChangePercent'],
                                                   'N/A',
                                                   data[symbol]['stats']['month1ChangePercent'],
                                                   'N/A',
                                                   'N/A'
                                                   ], 
                                                  index = hqm_columns), 
                                        ignore_index = True)
        
hqm_dataframe.columns

#CALCULANDO O PERCENTUAL DOS MOMENTOS
#Limpando os valores nulos
mask = hqm_dataframe['One-Year Price Return'].isnull() \
            | hqm_dataframe['Six-Month Price Return'].isnull() \
            | hqm_dataframe['Three-Month Price Return'].isnull() \
            | hqm_dataframe['One-Month Price Return'].isnull()


hqm_dataframe = hqm_dataframe.drop([118, 164, 324, 325])
hqm_dataframe[mask]

time_periods = [
                'One-Year',
                'Six-Month',
                'Three-Month',
                'One-Month'
                ]

for row in hqm_dataframe.index:
    for time_period in time_periods:
        hqm_dataframe.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(hqm_dataframe[f'{time_period} Price Return'], hqm_dataframe.loc[row, f'{time_period} Price Return'])#/100

# Print each percentile score to make sure it was calculated properly
for time_period in time_periods:
    print(hqm_dataframe[f'{time_period} Return Percentile'])
    
    
#HIGH-QUALITY MOMENTUM
from statistics import mean

for row in hqm_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period} Return Percentile'])
    hqm_dataframe.loc[row, 'HQM Score'] = mean(momentum_percentiles)
    
 # filtro dos 50 ativos
hqm_dataframe.sort_values(by = 'HQM Score', ascending = False)
hqm_dataframe = hqm_dataframe[:51]


# Streamlit Interface
portfolio_input = st.number_input()

position_size = float(portfolio_size) / len(hqm_dataframe.index)
for i in range(0, len(hqm_dataframe['Ticker'])-1):
    hqm_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / hqm_dataframe['Price'][i])
hqm_dataframe

