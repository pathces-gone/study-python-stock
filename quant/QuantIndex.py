import numpy as np
import types

from pandas.core.frame import DataFrame
import pandas as pd
import os

from IPython.display import display, HTML
from YamlUtils import *


class QuantIndex:
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
  def get_score(self):
    return self.ret 
  def whoami(self):
    print(self.comment)


class TableUtils:
  @staticmethod
  def get_row(df:DataFrame, key:int)->DataFrame:
    col = df.columns
    ret = df.loc[df[col[0]] == key,:]
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
    indices_eng = df[col[1]].to_dict()
    indices_kor = df[col[2]].to_dict()
    indices = defaultdict(list)
    for k, v in chain(indices_eng.items(), indices_kor.items()):
        indices[k].append(v)
    return indices

  @staticmethod
  def get_key(indices:dict, index:str)->int:
    for key, value in indices.items():
        if index == value[0] or index == value[1]:
            return key - 2

  @staticmethod
  def display_dataframe(df:DataFrame):
    display(HTML(df.to_html())) # Ipynb viewer

class QuantIndexTable:
  contents = {"per":0, "pbr":0, "pcr":0, "psr":0, "gp/a":0, "roa":0, "ev":0, "ebit":0}
  keys = contents.keys()

  @staticmethod
  def make_table(df: DataFrame, index:str)->DataFrame:
    """ Return "index_table"
    
    """
    indices = TableUtils.get_indices(df)
    #column = TableUtils.get_column(df)
    key = TableUtils.get_key(indices=indices, index=index)
    index_table = TableUtils.get_row(df, key=key)
    
    if 0:
      TableUtils.display_dataframe(df)  
    else:
      TableUtils.display_dataframe(index_table)
    return index_table

  @staticmethod
  def get_per(df:DataFrame):
    conf = YamlUtils.get('PER')
    comment = conf['comment']
    index = conf['trailing']['arg2']
    index_table = QuantIndexTable.make_table(df, index)

    eps = index_table['20200101-20201231'].to_list()[0]
    price = 79200
    return QuantIndex(comment, lambda x,y: np.abs(x/y), [eps, price])



if __name__ == '__main__':
  if 0:
    mmd = QuantIndex("mmd@min/max-1", lambda x,y: np.abs(x/y-1), [277.37,1145.66])
    print(mmd.get_score())
  if 1:
    path = os.path.join(os.path.dirname(__file__),'fsdata','fs_삼성전자.xlsx')
    df = pd.read_excel(path, sheet_name='Data_bs')
    #df = pd.read_excel(path, sheet_name='Data_cf')
    #df = pd.read_excel(path, sheet_name='Data_is')
    TableUtils.display_dataframe(df)  


    #per = QuantIndexTable().get_per(df)
    #print(per.get_score())