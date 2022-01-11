import yaml
import os, datetime, requests
import numpy as np
import ETFUtils
from ETF import ETF
import pandas as pd
import copy

class Portpolio(object):
  """ Return Portpolio
    Portpolio Node (ETF chain)
  """
  def __init__(self, name):
    self.name = name
    self.etfs = None
    self.ratios = None
    self.sources = None

  @staticmethod
  def get_yaml(index:str)->list:
    yaml_file_path = os.path.join(os.path.dirname(__file__),'yaml')
    with open(os.path.join(yaml_file_path, '%s.yaml'%index)) as f:
      conf = yaml.load(f, Loader=yaml.FullLoader)
    return conf

  def get_etf(self):
    name = self.name
    yaml = Portpolio.get_yaml(name)

    etf_name = np.array([])
    etf_code = np.array([])
    cmds = np.array([], np.int32)
    ratios = np.array([], np.float32)
    sources = np.array([])

    sub_portpolio = []
    sub_ratios = []
    for i,label in enumerate(yaml[name].values()):
      for sub_label in label:
        if sub_label['etf'].find('/') != -1:
          sub_portpolio, sub_ratios = Portpolio(name=sub_label['etf'][1:]).get_etf()
          sub_ratios = [(sub_label['ratio']/100)*sr for sr in sub_ratios]
          continue
        etf_code   = np.append(etf_code, sub_label['etf'])  
        etf_name   = np.append(etf_name, sub_label['comment'])
        ratios = np.append(ratios,sub_label['ratio'])
        sources = np.append(ratios,sub_label['source'])
        cmds = np.append(cmds, i)

    portpolio = []
    for i,etf in enumerate(etf_code):
      tmp = list(yaml[name].keys())
      portpolio.append( ETF(name=etf_name[i], code=etf_code[i], index= tmp[cmds[i]],src=sources[i]))
      
    portpolio = [*portpolio, *sub_portpolio]
    ratios = [*ratios, *sub_ratios]
    assert np.sum(ratios) <= 100, ""

    self.portpolio = portpolio
    self.sources = sources
  
    return [portpolio, ratios]

