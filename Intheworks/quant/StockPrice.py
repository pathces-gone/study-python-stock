import pandas as pd
from pandas.core.series import Series
import requests
from bs4 import BeautifulSoup as bs
import datetime
from mplfinance.original_flavor import candlestick2_ohlc
import matplotlib.pyplot as plt
import os


class UtilsGetFinance(object):
  def __new__(cls, *args, **kwargs):
    if not hasattr(cls, "_instance"):
      cls._instance = super().__new__(cls)
    return cls._instance

  def __init__(self):
    cls = type(self)
    if not hasattr(cls, "_init"):
      cls._init = True

  @classmethod
  def get_url(cls,item_name,code_df): 
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False) 
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code) 
    print("요청 URL = {}".format(url)) 
    return url

  @classmethod
  def get_html_table_symbol(cls,url):
    headers =  {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
    response = requests.get(url, headers=headers)
    html = bs(response.text, 'lxml')
    html_table = html.select('table')
    #len(html_table)
    return str(html_table)

  @classmethod
  def get_report_time(cls):
    return datetime.datetime.now().strftime("%Y%m%d")



class StockPrice:
  def __init__(self, item_name, page:10):
    cls = type(self)
    cls.USE_COLAB = False
    cls.GDRIVE_MOUNTED = False
    cls.code_df = None

    self.item_name = item_name
    self.page = page
  
  @classmethod
  def download_all_listed_corporation_as_csv(cls):
    path = os.path.join(os.path.dirname(__file__), 'listed_corporation.csv')
    print("Download listed_corporation.csv to %s"%path)
    if cls.code_df is None:
      cls.code_df  = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
    cls.code_df.to_csv(path, encoding='utf-8')

  def get_price(self, live: bool):
    cls = type(self)
    # 1: Get event_code from 상장법인목록.xls
    if live:
      cls.code_df  = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
    else:
      if cls.USE_COLAB:
        from google.colab import drive  
        if cls.GDRIVE_MOUNTED == False:
          print("Colab google-drive mounting ...")
          drive.mount('/content/gdrive/')
          cls.GDRIVE_MOUNTED = True
        path = os.path.join('/content/gdrive/MyDrive/fsdata/','listed_corporation.csv')
      else:
        path = os.path.join(os.path.dirname(__file__),'fsdata','listed_corporation.csv')
      cls.code_df = pd.read_csv(path)

    assert cls.code_df.empty==False, "Fail to load code_df." 
    code_df = cls.code_df
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
    code_df = code_df[['회사명', '종목코드']]
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

    # 2. Get stock data from naver finance
    url = UtilsGetFinance.get_url(self.item_name, code_df)

    df = pd.DataFrame()
    for _page in range(1, self.page):
      pg_url = '{url}&page={page}'.format(url=url, page=_page).replace(' ','')
      table = UtilsGetFinance.get_html_table_symbol(pg_url)
      df = df.append(pd.read_html(table, header=0)[0], ignore_index=True)
    df = df.dropna()
    assert df.empty == False, "the requested dataframe is empty."

    # 3. Rename columns
    df = df.rename(columns= {'날짜': 'Date', '종가': 'Close', '전일비': 'Diff', '시가': 'Open', '고가': 'High', '저가': 'Low', '거래량': 'Volume'}) 
    df[['Close', 'Diff', 'Open', 'High', 'Low', 'Volume']] = df[['Close', 'Diff', 'Open', 'High', 'Low', 'Volume']].astype(int) 
    df['Date'] = pd.to_datetime(df['Date']) 
    df = df.sort_values(by=['Date'], ascending=True)
    self.df = df
    return df

  def whoami(self):
    return self.item_name

  def get_page(self):
    return self.page

  def get_df(self):
    return self.df

  def display_df(self):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.colheader_justify', 'center')
    pd.set_option('display.precision', 3)
    print(self.df)

if __name__ == '__main__':
  item = StockPrice('삼성전자',page=5)
  df=item.get_price(False)
  item.display_df()