from re import S
import numpy as np
import types

from pandas.core.frame import DataFrame
import pandas as pd
import os

from IPython.display import display, HTML
from yamls.YamlUtils import *
from StockPrice import *

import matplotlib.pyplot as plt
from datetime import date


class QuantIndexRun:
  def __init__(self, comment:str, f:types.LambdaType, *params):
    self.comment= comment
    _params = params[0]
    num = len(_params)
    if num == 1:
      ret = f(_params[0])
    elif num == 2:
      ret = f(_params[0],_params[1])
    elif num == 3:
      ret = f(_params[0],_params[1],_params[2])
    else:
      ret = 0
    self.ret = ret

  @property
  def score(self):
    return round(self.ret,2)

  @property
  def whoami(self):
    print(self.comment)






class TableUtils:
  @staticmethod
  def get_row(df:DataFrame, key:int)->DataFrame:
    col = df.columns
    ret = df.loc[key,:].to_frame().T
    return ret
  @staticmethod
  def get_column(df:DataFrame)->DataFrame:
    col = df.columns
    return col

  @staticmethod
  def get_indices(df:DataFrame)->dict:
    from itertools import chain
    from collections import defaultdict
    col = df.columns
    indices_eng = df[col[0]].to_dict()
    indices_kor = df[col[1]].to_dict()
    indices = defaultdict(list)
    for k, v in chain(indices_eng.items(), indices_kor.items()):
        indices[k].append(v)
    return indices

  @staticmethod
  def get_key(indices:dict, index:str)->int:
    for key, value in indices.items():
        if index == value[0] or index == value[1]:
            return key

  @staticmethod
  def display_dataframe(df:DataFrame):
    display(HTML(df.to_html())) # Ipynb viewer






class QuantIndex(object):
  def __init__(self, statements:DataFrame, item_name:str):
    self.contents = {"per":0, "pbr":0, "pcr":0, "psr":0, "gp/a":0, "roa":0, "ev":0, "ebit":0}
    self.keys = self.contents.keys()

    self.statements=statements
    self.item_name = item_name
    self.share_price_table = (StockPrice(item_name=self.item_name, page=5).get_price(live=False))
    self.share_price_table.set_index(self.share_price_table.columns[0], inplace=True)

  @staticmethod
  def make_table(statements: DataFrame, index:str)->DataFrame:
    """ Return "index_table"
    """
    indices = TableUtils.get_indices(statements)
    key = TableUtils.get_key(indices=indices, index=index)
    index_table = TableUtils.get_row(statements, key=key)
    
    if 0:
      TableUtils.display_dataframe(statements)
      #TableUtils.display_dataframe(index_table)
    return index_table


  def plot_index(self, qi_list):
    quarter = self.col
    score = [q.score for q in qi_list]  

    fig = plt.figure(figsize=[20,10])
    plt.plot(quarter,score)
    #plt.scatter(quarter,score)
    #plt.show()

  """ Templete
  def get_(self):
    conf = YamlUtils.get('')
    comment = conf['comment']
    index = conf['']['']
    index_table = QuantIndex.make_table(self.statements, index)

    def target_date():
      return '2021-12-23'

    def contents(target_date):
      return []

    ret = QuantIndexRun(comment, lambda x,y: np.abs(x/y), contents(target_date()))
    return ret
  """

  @property
  def PER(self):
    """ Return "QuantIndexRun"
    """
    conf = YamlUtils.get('PER')
    comment = conf['comment']
    index = conf['trailing']['arg1']

    index_table = QuantIndex.make_table(self.statements, index)

    def target_date():
      ret = self.share_price_table.index[-1]
      return ret

    def contents(target_date:types.FunctionType, quater:str):
      _date = target_date()
      eps = int(index_table[quater].to_list()[0])
      share_price = self.share_price_table.loc[_date,:].to_frame().T
      share_price = int(share_price['Close'])
      return [share_price,eps]

    def cols(statements:DataFrame)->list:
      col = TableUtils.get_column(statements)[7:]
      col = [c for c in col]
      
      ret = []
      for c in col:
        s_yy = c[0:4]
        s_mm = c[4:6]
        s_dd = c[6:8]
        d_yy = c[9:13]
        d_mm = c[13:15]
        d_dd = c[15:17]

        if int(s_yy) < 2015:
          continue
        if s_mm == '01' and d_mm == '03':
          ret.append(c)
        if s_mm == '01' and d_mm == '06':
          ret.append(c)
        if s_mm == '01' and d_mm == '09':
          ret.append(c)
        if s_mm == '01' and d_mm == '12':
          ret.append(c)
      return list(reversed(ret))

    self.col = cols(index_table)
    ret = []
    
    for q in self.col:
      per = QuantIndexRun(comment, lambda x,y: np.abs(x/y), contents(target_date, q))
      ret.append(per)
    return ret



  @property
  def EPS(self):
    """ Return "QuantIndexRun"
    """
    conf = YamlUtils.get('PER')
    comment = conf['comment']
    index = conf['trailing']['arg1']

    index_table = QuantIndex.make_table(self.statements, index)

    def target_date():
      ret = self.share_price_table.index[-1]
      return ret

    def contents(target_date:types.FunctionType, quater:str):
      eps = int(index_table[quater].to_list()[0])
      return [eps, 1]

    def cols(statements:DataFrame)->list:
      col = TableUtils.get_column(statements)[7:]
      col = [c for c in col]
      ret = []
      for c in col:
        s_yy = c[0:4]
        s_mm = c[4:6]
        s_dd = c[6:8]
        d_yy = c[9:13]
        d_mm = c[13:15]
        d_dd = c[15:17]

        if int(s_yy) < 2018:
          continue
        if s_mm == '01' and d_mm == '03':
          ret.append(c)
        if s_mm == '04' and d_mm == '06':
          ret.append(c)
        if s_mm == '07' and d_mm == '09':
          ret.append(c)
        if s_mm == '10' and d_mm == '12':
          ret.append(c)
      return list(reversed(ret))

    self.col = cols(index_table)
    ret = []
    for q in self.col:
      per = QuantIndexRun(comment, lambda x,y: np.abs(x/y), contents(target_date, q))
      ret.append(per)
    return ret

if __name__ == '__main__':
  if 0:
    mmd = QuantIndex("mmd@min/max-1", lambda x,y: np.abs(x/y-1), [277.37,1145.66])
    print(mmd.score)

  if 1:
    item_name = '카카오게임즈'
    path = os.path.join(os.path.dirname(__file__),'fsdata','fs_%s.xlsx'%item_name)
    statements = pd.read_excel(path, sheet_name='Data_cis')
    TableUtils.display_dataframe(statements)

    statements = pd.read_excel(path, sheet_name='Data_cf')
    TableUtils.display_dataframe(statements)

    statements = pd.read_excel(path, sheet_name='Data_bs')
    TableUtils.display_dataframe(statements)

    if 0:
      samsung_electronics = QuantIndex(statements=statements, item_name=item_name)

      pers = samsung_electronics.PER
      #samsung_electronics.plot_index(pers)
      
      eps = samsung_electronics.EPS
      samsung_electronics.plot_index(eps)
      
    #else:
      #QuantIndex.make_table(statements, 'ifrs-full_ProfitLossAttributableToOwnersOfParent')