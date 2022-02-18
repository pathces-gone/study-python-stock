import yaml, os, datetime, requests
import numpy as np
import ETFUtils
import pandas as pd


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
      price_df = ETFUtils.utils_get_price(code=self.code,page=500,source=src)
      price_df.to_csv(self.path,encoding='utf-8')

    self.price_df = price_df

  def get_mavg(self, criteria:str, window:int):
    """ Return Dataframe
      criteria = 'Low', 'High', 'Open', 'Close', 'Value'
    """
    price_low = self.price_df.loc[:,criteria]
    mavg  = price_low.rolling(window=window).mean()
    return mavg

  def get_price(self, date):
    '''
      Input: datetime
      Ouput: [price, is_valid]
        * is_valid: Trade date? True or False
    '''
    price_df = self.price_df
    price = price_df.loc[price_df['Date'] == date,'Close'].values[0]
    valid = price_df.loc[price_df['Date'] == date,'Trade'].values[0]

    ret = round(price,2)
    return ret, valid

"""
  LOCAL
"""
if __name__ == '__main__':
  ticker = 'SPY'
  spy = ETF(name=ticker, code=ticker, index=ticker, src='YAHOO')
  price, valid = spy.get_price(date='2022-01-03')
  print(price, valid)
  #spy.get_inflection(start_date='2021-06-18',end_date='2022-01-18')