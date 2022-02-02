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

  def get_chart(self, start_date:str, end_date:str):
    #print(self.price_df)
    df = self.price_df.loc[
              (self.price_df['Date'] >= start_date) & (self.price_df['Date'] <= end_date)
              ,:]
    #print(df)
    ETFUtils.plot_candle_chart(df)

  def get_price(self, date:str):
    price_df = self.price_df
    price = 0
    next_date = datetime.datetime.strptime(date,"%Y-%m-%d")
    if not price_df.loc[price_df['Date'] == date].empty:
      price = price_df.loc[price_df['Date'] == date]['Close'].to_list()[0]
    else:
      for retry in range(14):
        next_date = ETFUtils.get_next_date(next_date);
        cond_df = price_df.loc[price_df['Date'] == next_date.strftime('%Y-%m-%d')]
        if not cond_df.empty:
          price = cond_df['Close'].to_list()[0]
          break
    assert price!=0 , "%s : %s , %s"%(self.name, self.code ,next_date)
      
    ret = round(price,2)
    return ret, next_date

"""
  LOCAL
"""
if __name__ == '__main__':
  ticker = 'SPY'
  spy = ETF(name=ticker, code=ticker, index=ticker, src='YAHOO')
  #price = spy.get_price(date='2022-01-03')
  #print(price)
  spy.get_inflection(start_date='2021-06-18',end_date='2022-01-18')