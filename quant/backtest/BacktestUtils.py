import sys
from os import path
print(path.dirname( path.dirname( path.abspath(__file__) ) ))
sys.path.append(path.dirname( path.dirname( path.abspath(__file__) ) ))
from StockPrice import *

from pandas.core.frame import DataFrame

class BacktestUtils(object):
  @staticmethod
  def get_price(item_name='삼성전자', page=10)->DataFrame:
    df = StockPrice(item_name=item_name, page=page).get_price(live=True)
    df.set_index(df.columns[0], inplace=True)
    df.index.rename('', inplace=True)
    return df

if __name__ == '__main__':
  new =BacktestUtils.get_price()
  print(new)