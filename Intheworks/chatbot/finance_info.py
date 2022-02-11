import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

import datetime
from mplfinance.original_flavor import candlestick2_ohlc
import matplotlib.pyplot as plt

import os

# =========================================== #
#                    Utils                    #
# =========================================== #
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}

def get_url(item_name, code_df): 
  code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False) 
  url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code) 
  print("요청 URL = {}".format(url)) 
  return url

def get_html_table_symbol(url):
  response = requests.get(url, headers=headers)
  html = bs(response.text, 'lxml')
  html_table = html.select('table')
  len(html_table)
  return str(html_table)

def get_report_time():
  return datetime.datetime.now().strftime("%Y%m%d")

def get_stochastic(df, n=5, m=3, t=3):
  df = pd.DataFrame(df)
  ndays_high = df.high.rolling(window=n, min_periods=1).max()
  ndays_low = df.low.rolling(window=n, min_periods=1).min()

  # Fast%K
  kdj_k = ((df.close - ndays_low)/(ndays_high-ndays_low))*100 #n=15
  # Fast%D
  kdj_d = kdj_k.ewm(span=m).mean() #m=5
  # Slow%D
  kdj_j = kdj_d.ewm(span=t).mean() #t=3
  
  df = df.assign(kdj_k=kdj_k, kdj_d=kdj_d, kdj_j=kdj_j).dropna()
  return df

# =========================================== #
#             class FinanceInfo               #
# =========================================== #
class FinanceInfo:
  def __init__(self, item_name, page:10):
    self.item_name = item_name
    self.page = page

    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    self.file_name = os.path.join(BASE_PATH,'../report/%s-%s.png'%(self.item_name,get_report_time()))

    # 1: Get event_code from 상장법인목록.xls
    code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
    code_df = code_df[['회사명', '종목코드']]
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

    # 2. Get stock data from naver finance
    url = get_url(self.item_name, code_df)

    df = pd.DataFrame()
    for _page in range(1, self.page):
      pg_url = '{url}&page={page}'.format(url=url, page=_page)
      table = get_html_table_symbol(pg_url)
      df = df.append(pd.read_html(table, header=0)[0], ignore_index=True)
    df = df.dropna()

    # 3. Rename columns
    df = df.rename(columns= {'날짜': 'date', '종가': 'close', '전일비': 'diff', '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'}) 
    df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int) 
    df['date'] = pd.to_datetime(df['date']) 
    df = df.sort_values(by=['date'], ascending=True)

    self.df = df

  def whoami(self):
    return self.item_name

  def get_page(self):
    return self.page

  def get_df(self):
    return self.df

  def get_filename(self):
    return self.file_name

  def get_stochastic(self):
    df = get_stochastic(self.df)

    fig = plt.figure(figsize=(20,20))
    ax1 = fig.add_subplot(5,1,1)
    ax2 = fig.add_subplot(5,1,2)
    ax3 = fig.add_subplot(5,1,3)
    ax4 = fig.add_subplot(5,1,4)
    ax5 = fig.add_subplot(5,1,5)

    ax4.plot(df.date, df['kdj_j'], 'r',label='Slow%D')
    ax3.plot(df.date, df['kdj_d'], 'g',label='Slow%K')
    ax2.plot(df.date, df['kdj_k'], 'b',label='Fast%K')

    ax5.plot (df.date, df['kdj_d'], 'g',label='Fast%D (Slow%K)')
    ax5.plot(df.date, df['kdj_j'] , 'r',label='Slow%D')

    candlestick2_ohlc(ax1, df['open'],df['high'],df['low'], df['close'], width=0.5, colorup='r', colordown='b')

    ax4.legend()
    ax3.legend()
    ax2.legend()

    plt.axhline(20)
    plt.axhline(80)

    plt.savefig(self.file_name)
    plt.close(fig)
    #return fig

if __name__ == '__main__':
  item = FinanceInfo('KG ETS',page=10)
  item.get_stochastic()