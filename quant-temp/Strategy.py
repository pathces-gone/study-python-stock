from pandas.core.frame import DataFrame
import pandas as pd
import os
import types
from StockPrice import *
from QuantIndex import *


class KHGSuper(object):
  def __init__(self, portfolio:list):
    self.portfolio = portfolio
    self.scaleup_factor = 100000
    print()

  def get_parameter(self)->dict:
    portfolio = self.portfolio
    sf =  self.scaleup_factor 
    quant_indices = dict()
    for name in portfolio:
      temp = dict()
      for key,value in zip(QuantIndex(name).contents.keys(), QuantIndex(name).contents.values()):
        if key == 'PER':
          temp['1/PER'] = [round(1/per*sf,3) for per in value]
        if key == 'PBR':
          temp['1/PBR'] = [round(1/pbr*sf,3) for pbr in value]
        if key == 'EV/EBIT':
          temp['1/EV/EBIT'] = [round(1/evebit*sf,3) for evebit in value]

      quant_indices[name] = temp
    return quant_indices

if __name__  == '__main__':
  portfolio = ['월덱스', '이녹스첨단소재','해성디에스']
  khgss = KHGSuper(portfolio = portfolio)
  
  ret = khgss.get_parameter()
  for p in portfolio:
    print(p,ret[p])