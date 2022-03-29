import numpy as np
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
import FinanceDataReader as fdr #pip3 install --user finance-datareader
from fredapi import Fred
import datetime, os

class ETFUtiles(object):
  @staticmethod
  def get_price_data(ticker:str, source:str='YAHOO'):
    def get_from_fdr(ticker:str, page=None):
      pass

    def get_from_yahoo(ticker:str, page=None):
      ''' Return
        Input : Date,[ Open, High, Low, Close, Adj Close, Volume]
        Output: [Date,Open, High, Low, Close, Volume, Trade]
      '''
      yf.pdr_override()
      df_price = pdr.get_data_yahoo(ticker)
      df_price = df_price.reset_index()

      df_price['mvg13'] = df_price['Low'].rolling(window=13).mean()
      df_price['mvg55'] = df_price['Low'].rolling(window=55).mean()
      df_price['mvg224'] = df_price['Low'].rolling(window=224).mean()

      #df_price = append_missing_trading_date(df_price)
      return df_price

    def get_from_fred(ticker:str, page=None):
      pass

    if source == 'FDR':
      pasring_func = get_from_fdr
    elif source == 'YAHOO':
      pasring_func = get_from_yahoo
    elif source == 'FRED':
      pasring_func = get_from_yahoo
    else:
      pasring_func = None
    
    assert pasring_func != None, "pasring_func = None"

    ret = pasring_func(ticker=ticker, page=None)
    return  ret

class ETF(ETFUtiles):
  pass



if __name__ == '__main__':
  
  df = ETF().get_price_data('SPY',source='YAHOO')
  print(df)