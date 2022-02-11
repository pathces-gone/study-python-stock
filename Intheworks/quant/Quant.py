import pandas as pd
from pandas.core.series import Series
import os
import numpy as np
import types

from QuantIndex import *
from StockPrice import *
from Stock import *

class QuantEngine(object): 
  qunat_index_table = QuantIndexTable()

  def __init__(self, stock:Stock):
    self.stock = stock
    self.qunat_index_table.make_table(stock.df_financial_statements)

    '''
    # Calculate Quant Indexs
    def get_statements_index(self, index:str):
        assert index in self.sttlb.keys, "%s is not member of StatementsIndexTable."%index

    def get_quant_index(self,index:str):
        assert index in self.qitlb.keys, "%s is not member of QuantIndexTable."%index
        if index == 'mdd':
            self.qitlb.contents[index] = self._mdd()
        if index == 'sharp_ratio':
            self.qitlb.contents[index] = self._sharp_ratio()
        return self.qitlb.contents[index].get_score()

    def _mdd(self):
        return QuantIndex("mdd@min/max-1", lambda x,y: np.abs(x/y-1), [277.37,1145.66])

    def _sharp_ratio(self):
        return QuantIndex("mdd@min/max-1", lambda x,y: np.abs(x/y-1), [277.37,1145.66])
    '''