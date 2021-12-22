# DataFrame
from pandas.core.frame import DataFrame
import requests
import pandas as pd
from IPython.display import HTML

# Plot
import datetime
from mplfinance.original_flavor import candlestick2_ohlc
import matplotlib.pyplot as plt

# DIY
from StockPrice import *

class Stock:
    def __init__(self, code:str, name:str):
        cls = type(self)
        cls.PRICE_LIVE_UPDATE = False
        cls.USE_COLAB = False
        cls.SOURCE = 'dart' #'naver'
        if cls.USE_COLAB:
            cls.FSDATA_PATH  = os.path.join('/content/gdrive/MyDrive','fsdata')
        else:
            cls.FSDATA_PATH  = os.path.join(os.path.dirname(__file__),'fsdata')

        self.code = code
        self.name = name

        # 1. Download - data from dart.
        print('1. Get - fs_%s.xlsx  from  dart.'%name)
        self.df_financial_statements = self.get_financial_statements_dataframe()
        
        # 2. Download - price data from krx 
        print('2. Get - price data from krx')
        self.df_price = self.get_price_dataframe()

    def get_listed_corp_dataframe(self):
        cls = type(self)
        if cls.PRICE_LIVE_UPDATE:
          StockPrice(self.name,page=5).download_all_listed_corporation_as_csv()
        file_ = os.path.join(cls.FSDATA_PATH,'listed_corporation.csv')
        df = pd.read_csv(file_)
        return df

    def get_financial_statements_dataframe(self):
        cls = type(self)
        if cls.SOURCE == 'naver':
            URL = f"https://finance.naver.com/item/main.nhn?code={self.code}"
            r = requests.get(URL)
            df = pd.read_html(r.text)[3]
        else:
            file_ = os.path.join(cls.FSDATA_PATH,'fs_%s.xlsx'%(self.name))
            df = pd.read_excel(file_) 
        return df

    def get_price_dataframe(self):
        df = StockPrice(self.name,page=5).get_price(live=False)
        return df

    def set_index(self):
        cls = type(self)
        if cls.SOURCE == 'naver':
            df = self.df_financial_statements()
            df.set_index(df.columns[0], inplace=True)
            df.index.rename('주요재무정보', inplace=True)
            df.columns = df.columns.droplevel(2)
            self.annual_data = pd.DataFrame(df).xs('최근 연간 실적', axis=1)
            self.quater_data = pd.DataFrame(df).xs('최근 분기 실적', axis=1)
            self.df_financial_statements = df

    def display_df(self, cmd):
        cls = type(self)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.colheader_justify', 'center')
        pd.set_option('display.precision', 3)

        if cls.SOURCE == 'naver':
            if cmd == 0:
                print(self.df_financial_statements)
            elif cmd == 1:
                print(self.annual_data)
            elif cmd == 2:
                print(self.quater_data)
            else:
                print()
        else:
            print(self.df_financial_statements)

    def plot(self):
      df = self.df_price
      fig = plt.figure(figsize=(20,5))
      ax = fig.add_subplot(1,1,1)
      candlestick2_ohlc(ax, df['open'],df['high'],df['low'], df['close'], width=0.5, colorup='r', colordown='b')
      plt.show()

if __name__ == '__main__':
    seoul_auction = Stock(code='0', name='서울옥션')
    #seoul_auction.plot()