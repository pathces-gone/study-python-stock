from pandas.core.frame import DataFrame
import pandas as pd
import os, types, time
from FnGuide import *
from Manager import DEBUG_QUANT_INDEX_ELAPSED_TIME

class QuantIndex(object):
  def __init__(self, item_name:str):
    if DEBUG_QUANT_INDEX_ELAPSED_TIME:
      start_time = time.time()

    term = 'annual'
    self.contents = dict()
    self.contents["PER"] = QuantIndex.PER(item_name,term)
    self.contents["PBR"] = QuantIndex.PBR(item_name,term)
    self.contents["PCR"] = QuantIndex.PCR(item_name,term)
    self.contents["PSR"] = QuantIndex.PSR(item_name,term)
    self.contents["EV/EBIT"] = [round(ev/ebit,2) for ev,ebit in zip( QuantIndex.EV(item_name,term), QuantIndex.EBITDA(item_name,term))]
    #{"PER":0, "PBR":0, "pcr":0, "psr":0, "gp/a":0, "roa":0, "ev":0, "ebit":0}

    if DEBUG_QUANT_INDEX_ELAPSED_TIME:
      print("QuantIndex Elapsed Time : %.2f"%round(time.time()-start_time,2))

  @staticmethod
  def PER(name:str, term:str):
    pers ,_ = FnGuide.get_data(_name=name, _page=2,_item="PER",_n=4,_term=term)    
    ret = []
    for per in pers:
      if per == 'N/A':
        ret.append(-1)
      else:
        ret.append(float(per.replace(',','')))
    ret.append(FnGuide.get_multiples_prev_quater(name=name,item="PER"))
    return ret
  
  @staticmethod
  def PBR(name:str, term:str):
    pbrs,_ = FnGuide.get_data(_name=name, _page=2,_item="PBR",_n=4,_term=term)
    ret = []
    for pbr in pbrs:
      if pbr == 'N/A':
        ret.append(-1)
      else:
        ret.append(float(pbr.replace(',','')))
    ret.append(FnGuide.get_multiples_prev_quater(name=name,item="PBR"))
    return ret

  @staticmethod
  def EV(name:str, term:str):
    evs,_ = FnGuide.get_data(_name=name, _page=2,_item="EV",_n=4,_term=term)
    ret = []
    for ev in evs:
      if ev == 'N/A':
        ret.append(-1)
      else:
        ret.append(float(ev.replace(',','')))
    ret.append(FnGuide.get_multiples_prev_quater(name=name,item="EV"))
    return ret

  @staticmethod
  def EBITDA(name:str, term:str):
    ebitdas,_ = FnGuide.get_data(_name=name, _page=2,_item="EBITDA",_n=4,_term=term)
    ret = []
    for ebitda in ebitdas:
      if ebitda == 'N/A':
        ret.append(-1)
      else:
        ret.append(float(ebitda.replace(',','')))
    ret.append(FnGuide.get_multiples_prev_quater(name=name,item="EBITDA"))
    return ret

  @staticmethod
  def PCR(name:str, term:str):
    pcrs,_ = FnGuide.get_data(_name=name, _page=2,_item="PCR",_n=4,_term=term)
    ret = []
    for pcr in pcrs:
      if pcr == 'N/A':
        ret.append(-1)
      else:
        ret.append(float(pcr.replace(',','')))
    ret.append(FnGuide.get_multiples_prev_quater(name=name,item="PCR"))
    return ret

  @staticmethod
  def PSR(name:str, term:str):
    psrs,_ = FnGuide.get_data(_name=name, _page=2,_item="PSR",_n=4,_term=term)
    ret = []
    for psr in psrs:
      if psr == 'N/A':
        ret.append(-1)
      else:
        ret.append(float(psr.replace(',','')))
    ret.append(FnGuide.get_multiples_prev_quater(name=name,item="PSR"))
    return ret

if __name__ == '__main__':
  qi = QuantIndex("삼성전자").contents
  print(qi)