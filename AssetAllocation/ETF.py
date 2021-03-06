import yaml, os, datetime, requests
import numpy as np
import ETFUtils
import pandas as pd
import datetime

class ETF(object):
  """ Return ETF
    ETF object
  """
  def __init__(self, name:str, code:str, index:str, src:str='NAVER'):
    self.name  = name
    self.code  = code
    self.index = index
    self.src = src
    self.path = os.path.join('fsdata','%s.csv'%self.code)

    if os.path.exists(self.path):
      price_df = pd.read_csv(self.path)
    else:
      price_df = ETFUtils.utils_get_price(code=self.code,page=10,source=src)
      price_df.to_csv(self.path,encoding='utf-8', index=False)
    self.price_df = price_df

  def get_mavg(self, criteria:str, window:int):
    """ Return Dataframe
      criteria = 'Low', 'High', 'Open', 'Close', 'Value'
    """
    price_low = self.price_df.loc[:,criteria]
    mavg  = price_low.rolling(window=window).mean()
    return mavg

  def get_price(self, date:datetime.date):
    '''
      Input: datetime.datetime
      Ouput: [price, is_valid]
        * is_valid: Trade date? True or False
    '''
    price_df = self.price_df
    if type(date) != str:
      date_str = date.strftime('%Y-%m-%d')
    else:
      date_str = date
    price = price_df.loc[price_df['Date'] == date_str,'Close'].values[0]
    valid = price_df.loc[price_df['Date'] == date_str,'Trade'].values[0]
    ret = round(price,2)
    return ret, valid

"""
  LOCAL
"""
if __name__ == '__main__':
  # ticker = 'DIA'
  # spy = ETF(name=ticker, code=ticker, index=ticker, src='YAHOO')
  # price, valid = spy.get_price(date='2022-01-03')
  # print(price, valid)
  # #spy.get_inflection(start_date='2021-06-18',end_date='2022-01-18')


  ticker = 'DGS10'
  spy = ETF(name=ticker, code=ticker, index=ticker, src='FRED')
  price, valid = spy.get_price(date='2022-01-03')
  print(price, valid)