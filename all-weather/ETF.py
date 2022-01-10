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
      price_df = ETFUtils.utils_get_price(code=self.code,page=100,source=src)
      price_df.to_csv(self.path,encoding='utf-8')

    self.price_df = price_df

  def get_chart(self):
    #assert self.price_df != None,"price_df is None"
    ETFUtils.plot_candle_chart(self.price_df)

  def get_price(self, date:str):
    price_df = self.price_df
    price = 0
    if not price_df.loc[price_df['Date'] == date].empty:
      price = price_df.loc[price_df['Date'] == date]['Close'].to_list()[0]
    else:
      next_date = datetime.datetime.strptime(date,"%Y-%m-%d")
      for retry in range(14):
        next_date = next_date + datetime.timedelta(days=1)
        cond_df = price_df.loc[price_df['Date'] == next_date.strftime('%Y-%m-%d')]
        if not cond_df.empty:
          price = cond_df['Close'].to_list()[0]
          break
    assert price!=0 ,"%s : %s , %s"%(self.name, self.code ,date)
    
    ret = round(price,2)
    return ret



"""
  LOCAL
"""
if __name__ == '__main__':
  ticker = 'SPY'
  spy = ETF(name=ticker, code=ticker, index=ticker, src='YAHOO')
  price = spy.get_price(date='2020-01-10')
  print(price)

  ticker = '137610'
  spy = ETF(name=ticker, code=ticker, index=ticker, src='NAVER')
  price = spy.get_price(date='2020-01-10')
  print(price)