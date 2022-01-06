from pandas.core.frame import DataFrame
import pandas as pd
import os
import types
from StockPrice import *
from QuantIndex import *
from Manager import *
from GetGroup import *


class KHGSuper(object):
  """ KHU
  
  
  """
  def __init__(self, portfolio:list):
    self.portfolio = portfolio
    self.scaleup_factor = 1

  def get_parameter(self)->dict:
    portfolio = self.portfolio
    sf =  self.scaleup_factor 
    quant_indices = dict()
    for name in portfolio:
      temp = dict()

      instance_quant_index = QuantIndex(name)

      #print(instance_quant_index.contents)
      for key,value in zip(instance_quant_index.contents.keys(), instance_quant_index.contents.values()):
        if key == 'PER':
          temp['1/PER'] = [round(1/per*sf,3) for per in value]
        if key == 'PBR':
          temp['1/PBR'] = [round(1/pbr*sf,3) for pbr in value]
        if key == 'PCR':
          temp['1/PCR'] = [round(1/pcr*sf,3) for pcr in value]
        if key == 'PSR':
          temp['1/PSR'] = [round(1/psr*sf,3) for psr in value]
          
      quant_indices[name] = temp

    #for p in portfolio: 
    #  print(p,quant_indices[p])
    return quant_indices


  def sort_by_priority(self)->list:
    portfolio = self.portfolio
    quant_indices = self.get_parameter()

    a = [(p,quant_indices[p]['1/PER'][-1]) for p in portfolio]
    b = [(p,quant_indices[p]['1/PBR'][-1]) for p in portfolio]
    c = [(p,quant_indices[p]['1/PCR'][-1]) for p in portfolio]
    d = [(p,quant_indices[p]['1/PSR'][-1]) for p in portfolio]

    a_sort = sorted(a,key=lambda x:-x[1])
    b_sort = sorted(b,key=lambda x:-x[1])
    c_sort = sorted(c,key=lambda x:-x[1])
    d_sort = sorted(d,key=lambda x:-x[1])

    if DEBUG_KHGSS_PRINT:
      print(a_sort)
      print(b_sort)
      print(c_sort)
      print(d_sort)
    
    point = lambda i : len(portfolio)-i
    ret = dict([(p,0) for p in portfolio])
    for i in range(len(portfolio)):
      ret[a_sort[i][0]] += point(i)     
      ret[b_sort[i][0]] += point(i)     
      ret[c_sort[i][0]] += point(i)     
      ret[d_sort[i][0]] += point(i)     
    
    if DEBUG_KHGSS_PRINT:
      print(ret)

    return sorted(ret.items(), key=lambda x:-x[1])

if __name__  == '__main__':
  if 0:
    portfolio = ['월덱스', '이녹스첨단소재','해성디에스','현대모비스','삼성전자','위메이드']
  else:
    portfolio = GetGroup.get('apple-oled')
  khgss = KHGSuper(portfolio = portfolio)
  
  priority = khgss.sort_by_priority()
  print(priority)
