import unicodedata, requests, time, datetime, os
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.series import Series
from pandas_datareader import data as pdr
from bs4 import BeautifulSoup as bs
import yfinance as yf
from mplfinance.original_flavor import candlestick2_ohlc
import matplotlib.pyplot as plt


def preformat_cjk (string, width, align='<', fill=' '):
  """
    UNICODE - ALIGN
  """
  count = (width - sum(1 + (unicodedata.east_asian_width(c) in "WF")
                        for c in string))
  return {
      '>': lambda s: fill * count + s,
      '<': lambda s: s + fill * count,
      '^': lambda s: fill * (count / 2)
                      + s
                      + fill * (count / 2 + count % 2)
}[align](string)


def plot_candle_chart(price:DataFrame):
  """ Return
    plot()
  """
  fig = plt.figure(figsize=(10,5))
  ax = fig.add_subplot(1,1,1)

  candlestick2_ohlc(ax, price['Open'],price['High'],price['Low'], price['Close'], width=0.5, colorup='r', colordown='b')
  plt.show()


def get_next_date(today:datetime)->datetime:
  """ Return
    Next_date
  """
  next_date = today + datetime.timedelta(days=1)
  return next_date

def get_prev_date(today:datetime, days:int)->datetime:
  """ Return
    Prev_date
  """
  prev_date = today - datetime.timedelta(days=days)
  return prev_date


def utils_get_price(code:str, page:int=2, source:str='NAVER'):
  """ Return
    dataframe
  """
  if source == 'NAVER':
    #start_time = time.time()
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    def get_html_table(url:str):
      headers =  {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
      response = requests.get(url, headers=headers)
      html = bs(response.text, 'lxml')
      html_table = html.select('table') 
      return str(html_table)

    df = pd.DataFrame()
    for _page in range(1, page):
      pg_url = '{url}&page={page}'.format(url=url, page=_page).replace(' ','')
      html_table = get_html_table(pg_url)
      df = pd.concat([df,pd.read_html(html_table, header=0)[0]],axis=0,ignore_index=True)
    print(df)
    df = df.dropna(axis=0)
    print(df)
    assert df.empty == False, "the requested dataframe is empty."

    df = df.rename(columns= {'날짜': 'Date', '종가': 'Close', '전일비': 'Diff', '시가': 'Open', '고가': 'High', '저가': 'Low', '거래량': 'Volume'}) 
    df[['Close', 'Diff', 'Open', 'High', 'Low', 'Volume']] = df[['Close', 'Diff', 'Open', 'High', 'Low', 'Volume']].astype(int) 
    df['Date'] = pd.to_datetime(df['Date']) 
    ret = df.sort_values(by=['Date'], ascending=True)
    return ret
  else:
    ticker=code
    yf.pdr_override()
    df_price = pdr.get_data_yahoo(ticker) # [Date, Open, High, Low, Close, Adj Close, Volume]
    ret = df_price.reset_index()
    return ret



def get_trading_date(ticker:str):
  path = os.path.join('fsdata',ticker+'.csv')
  if os.path.exists(path):
    price_df = pd.read_csv(path)
    return price_df['Date']
  else:
    return None

"""
  LOCAL
"""
if __name__ == '__main__':
  utils_get_price(code='261240', page=10, source='NAVER')
  #ret = get_trading_date('SPY')
  #print(ret)
  #ret=ret.loc[('2019-01-03'<=ret) & (ret<'2020-01-03')]
  #print(len(ret))