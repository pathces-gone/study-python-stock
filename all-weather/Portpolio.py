import yaml
import os, datetime, requests
import numpy as np
import ETFUtils
from ETF import ETF
import pandas as pd
import copy

import matplotlib.pyplot as plt
import seaborn as sns



class Portpolio(object):
  """ Return Portpolio
    Portpolio Node (ETF chain)
  """
  def __init__(self, name):
    self.name = name
    self.sources = None
    self.portpolio = None

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
        sources = np.append(sources,sub_label['source'])
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

  def get_correlation(self, start_date, end_date):
    """ Return
      Correation Dataframe
    """
    plt.rcParams["font.family"] = 'NanumGothic'

    if self.portpolio == None:
      portpolio,_ = self.get_etf()

    raw_df = pd.DataFrame(portpolio[0].price_df[['Date']])
    for etf in portpolio:
      raw_df[etf.name] =(etf.price_df['Close'])

    ranging_df = raw_df[(start_date<=raw_df['Date']) & (raw_df['Date']<=end_date)]
    #print(ranging_df)
    corr_df = ranging_df.corr(method='pearson')
    print(corr_df)

    return corr_df

"""
  LOCAL
"""
if __name__ == '__main__':
  po = Portpolio('DANTE')

  #corr_df = po.get_correlation('2008-12-20','2022-01-10')
  #corr_df = po.get_correlation('2019-12-20','2022-01-10')
  corr_df = po.get_correlation('2013-12-20','2019-01-10')


  fig, ax = plt.subplots( figsize=(7,7) )

  # 삼각형 마스크를 만든다(위 쪽 삼각형에 True, 아래 삼각형에 False)
  mask = np.zeros_like(corr_df, dtype=np.bool)
  mask[np.triu_indices_from(mask)] = True

  # 히트맵을 그린다
  sns.heatmap(corr_df, 
              cmap = 'RdYlBu_r', 
              annot = True,   # 실제 값을 표시한다
              mask=mask,      # 표시하지 않을 마스크 부분을 지정한다
              linewidths=.5,  # 경계면 실선으로 구분하기
              cbar_kws={"shrink": .5},# 컬러바 크기 절반으로 줄이기
              vmin = -1,vmax = 1   # 컬러바 범위 -1 ~ 1
            )  
  plt.show()