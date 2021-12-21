import requests
import pandas as pd
from IPython.display import HTML
from QuantIndex import *
from StockPrice import *
#from DartAPI import *

class Stock:
    def __init__(self, code:str, name:str):
        cls = type(self)
        cls.PRICE_LIVE_UPDATE = False
        cls.USE_COLAB = False
        cls.SOURCE = 'dart' #'naver'

        self.code = code
        self.name = name

        self.qitlb = QuantIndexTable()     # quant index : MMD/SharpIndex/..
        self.sttlb = StatementIndexTable() # statement index : PER/PBR/..

        # 1. Download - data from dart.
        print('1. Get - fs_%s.xlsx  from  dart.'%name)
        self.df_financial_statements = self.get_financial_statements_dataframe()
        
        # 2. Download - price data from krx 
        print('2. Get - price data from krx')
        self.df_price = self.get_price_dataframe()
        
    def get_financial_statements_dataframe(self):
        cls = type(self)
        if cls.SOURCE == 'naver':
            URL = f"https://finance.naver.com/item/main.nhn?code={self.code}"
            r = requests.get(URL)
            df = pd.read_html(r.text)[3]
        else:
            if cls.USE_COLAB:
                path = os.path.join('/content/gdrive/MyDrive','fsdata','fs_%s.xlsx'%(self.name))
            else:
                path = os.path.join(os.path.dirname(__file__),'fsdata','fs_%s.xlsx'%(self.name))
            df = pd.read_excel(path) 
        return df

    def get_price_dataframe(self):
        cls = type(self)
    #    if cls.PRICE_LIVE_UPDATE:
    #      StockPrice(self.name,page=5).get_price()
    #    else:
        return 0

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
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.colheader_justify', 'center')
        pd.set_option('display.precision', 3)

        if self.source == 'naver':
            if cmd == 0:
                display(self.df_financial_statements)
            elif cmd == 1:
                display(self.annual_data)
            elif cmd == 2:
                display(self.quater_data)
            else:
                print()
        else:
            print(self.df_financial_statements)

    # Calculate Quant Indexs
    def get_statements_index(self, index:str):
        assert index in self.sttlb.keys, "%s is not member of StatementsIndexTable."%index

    def get_quant_index(self,index:str):
        assert index in self.qitlb.keys, "%s is not member of QuantIndexTable."%index
        if index == 'mmd':
            self.qitlb.contents[index] = self._mmd()
        if index == 'sharp_ratio':
            self.qitlb.contents[index] = self._sharp_ratio()
        return self.qitlb.contents[index].get_score()

    def _mmd(self):
        return QuantIndex("mmd@min/max-1", lambda x,y: np.abs(x/y-1), [277.37,1145.66])

    def _sharp_ratio(self):
        return QuantIndex("mmd@min/max-1", lambda x,y: np.abs(x/y-1), [277.37,1145.66])




if __name__ == '__main__':
    seoul_auction = Stock(code='0', name='서울옥션')
    seoul_auction.display_df(0)

    if 0:
        seoul_auction_mmd = seoul_auction.get_quant_index("mmd")
        print(seoul_auction_mmd)
        seoul_auction_sharp_ratio = seoul_auction.get_quant_index("sharp_ratio")
        print(seoul_auction_sharp_ratio)
        print(seoul_auction.finance_info.get_df())
    else:
        print((seoul_auction.df_price))