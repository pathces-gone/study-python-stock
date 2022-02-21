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

def get_next_date(today:datetime,days:int=1)->datetime:
  """ Return
    Next_date
  """
  next_date = today + datetime.timedelta(days=days)
  return next_date

def get_prev_date(today:datetime, days:int)->datetime:
  """ Return
    Prev_date
  """
  prev_date = today - datetime.timedelta(days=days)
  return prev_date



def append_missing_trading_date(df:pd.core.frame.DataFrame):
  ''' Return
    input: 
              Date	Close	Diff	Open	High	Low	Volume
      0	2022-02-07	10610	30	10605	10615	10585	72843
    output:
              Date	Close	Diff	Open	High	Low	Volume	Trade
      0	2022-02-07	10610	30	10605	10615	10585	72843	True
  '''
  idx = pd.date_range(df.loc[:,'Date'].min(),df.loc[:,'Date'].max())
  s = df.set_index('Date')
  s = s.reindex(idx, fill_value=0)

  s['Trade'] = s.apply(lambda x: x['Close'] != 0, axis=1)
  s = s.reset_index().rename(columns={"index": "Date"})

  for i in s.index:
    if s.iloc[i,-1]==False:
      s.iloc[i,1:-1] = s.iloc[i-1,1:-1]
  return s


def utils_get_price(code:str, page:int=2, source:str='NAVER'):
  """ Return
    dataframe
  """
  def get_from_naver(ticker:str, page:int):
    ''' Return
      Dataframe [Date	Close	Diff	Open	High	Low	Volume	Trade]
    '''
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=ticker)
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
    assert df.empty == False, "the requested dataframe is empty."
    df = df.dropna(axis=0)
    
    df = df.rename(columns= {'날짜': 'Date', '종가': 'Close', '전일비': 'Diff', '시가': 'Open', '고가': 'High', '저가': 'Low', '거래량': 'Volume'}) 
    df[['Close', 'Diff', 'Open', 'High', 'Low', 'Volume']] = df[['Close', 'Diff', 'Open', 'High', 'Low', 'Volume']].astype(int) 
    df['Date'] = pd.to_datetime(df['Date']) 

    df['mvg13'] = df['Close'].rolling(window=13).mean()
    df['mvg55'] = df['Close'].rolling(window=55).mean()

    idx = pd.date_range(df.loc[:,'Date'].min(),df.loc[:,'Date'].max())
    df = df.set_index('Date')

    s = df
    s = s.reindex(idx, fill_value=0)

    s['Trade'] = s.apply(lambda x: x['Close'] != 0, axis=1)
    s = s.reset_index().rename(columns={"index": "Date"})

    for i in s.index:
      if s.iloc[i,-1]==False:
        s.iloc[i,:-1] = s.iloc[i-1,:-1] 

    ret = s.sort_values(by=['Date'], ascending=True)
    return ret

  def get_from_yahoo(ticker:str, page=None):
    ''' Return
      Input : Date,[ Open, High, Low, Close, Adj Close, Volume]
      Output: [Date,Open, High, Low, Close, Adj Close, Volume, Trade]
    '''
    yf.pdr_override()
    df_price = pdr.get_data_yahoo(ticker)
    df_price = df_price.reset_index()

    df_price['mvg13'] = df_price['Close'].rolling(window=13).mean()
    df_price['mvg55'] = df_price['Close'].rolling(window=55).mean()

    df_price = append_missing_trading_date(df_price)
    return df_price

  if source == 'NAVER':
    pasring_func = get_from_naver
  elif source == 'YAHOO':
    pasring_func = get_from_yahoo
  else:
    pasring_func = None
  
  assert pasring_func != None, "pasring_func = None"

  ret = pasring_func(ticker=code, page=page)
  return  ret



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
  #print(utils_get_price(code='261240', page=100, source='NAVER'))
  print(utils_get_price(code='SPY', page=10, source='YAHOO').iloc[-30:-1])
  #ret = get_trading_date('SPY')
  #print(ret)
  #ret=ret.loc[('2019-01-03'<=ret) & (ret<'2020-01-03')]
  #print(len(ret))