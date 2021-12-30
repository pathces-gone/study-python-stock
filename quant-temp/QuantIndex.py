from pandas.core.frame import DataFrame
import pandas as pd
import os
import types
from FnGuide import *


class QuantIndex(object):
  def __init__(self, item_name:str):
    term = 'annual'
    self.contents = dict()
    self.contents["PER"] = QuantIndex.PER(item_name,term)
    self.contents["PBR"] = QuantIndex.PBR(item_name,term)
    self.contents["EV/EBIT"] = [round(ev/ebit,2) for ev,ebit in zip( QuantIndex.EV(item_name,term), QuantIndex.EBITDA(item_name,term))]
    
    #{"PER":0, "PBR":0, "pcr":0, "psr":0, "gp/a":0, "roa":0, "ev":0, "ebit":0}

  @staticmethod
  def PER(name:str, term:str):
    ret,_ = FnGuide.get_data(_name=name, _page=2,_item="PER",_n=5,_term=term)
    ret = [ float(per.replace(',','')) for per in ret]
    return ret
  
  @staticmethod
  def PBR(name:str, term:str):
    ret,_ = FnGuide.get_data(_name=name, _page=2,_item="PBR",_n=5,_term=term)
    ret = [ float(pbr.replace(',','')) for pbr in ret]
    return ret

  @staticmethod
  def EV(name:str, term:str):
    ret,_ = FnGuide.get_data(_name=name, _page=2,_item="EV",_n=5,_term=term)
    ret = [ float(ev.replace(',','')) for ev in ret]
    return ret

  @staticmethod
  def EBITDA(name:str, term:str):
    ret,_ = FnGuide.get_data(_name=name, _page=2,_item="EBITDA",_n=5,_term=term)
    ret = [ float(ebitda.replace(',','')) for ebitda in ret]
    return ret

if __name__ == '__main__':
  qi = QuantIndex("이녹스첨단소재").contents
  print(qi)