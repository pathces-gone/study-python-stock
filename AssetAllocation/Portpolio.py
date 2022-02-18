from re import X
import yaml
import os, datetime, requests
import numpy as np
import ETFUtils
from ETF import ETF
import pandas as pd
import copy

import matplotlib.pyplot as plt
import seaborn as sns
import platform
import FinanceDataReader as fdr #pip3 install --user finance-datareader

class Portpolio(object):
  """ Return Portpolio
    Portpolio Node (ETF chain)
  """
  def __init__(self, name:str, is_usd_krw_need:bool=True ):
    self.name = name
    self.sources = None
    self.items = None

    if is_usd_krw_need:
      usd_krw_path = os.path.join('fsdata','usd_krw.csv')
      if os.path.exists(usd_krw_path):
        self.usd_krw = pd.read_csv(usd_krw_path)
      else:
        if not os.path.exists('fsdata'):
          os.mkdir('fsdata')
        self.usd_krw = fdr.DataReader('USD/KRW')
        self.usd_krw = self.usd_krw.reset_index()
        self.usd_krw = ETFUtils.append_missing_trading_date(self.usd_krw)
        self.usd_krw.to_csv(usd_krw_path,encoding='utf-8', index=False)

  @staticmethod
  def get_yaml(index:str,yaml_path:str='yaml')->list:
    yaml_file_path = os.path.join(os.path.dirname(__file__),yaml_path)
    with open(os.path.join(yaml_file_path, '%s.yaml'%index)) as f:
      conf = yaml.load(f, Loader=yaml.FullLoader)
    return conf

  def get_etf(self):
    """ Return
      [items, ratio]
    """
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
          sp, sr = Portpolio(name=sub_label['etf'][1:]).get_etf()
          sr = [(sub_label['ratio']/100)*s for s in sr]
          sub_portpolio.append(sp)
          sub_ratios.append(sr)

          #sub_portpolio = sp
          #sub_ratios = sr
          continue
        etf_code   = np.append(etf_code, sub_label['etf'])  
        etf_name   = np.append(etf_name, sub_label['comment'])
        ratios = np.append(ratios,sub_label['ratio'])
        sources = np.append(sources,sub_label['source'])
        cmds = np.append(cmds, i)

    items = []
    for i,etf in enumerate(etf_code):
      tmp = list(yaml[name].keys())
      items.append( ETF(name=etf_name[i], code=etf_code[i], index= tmp[cmds[i]],src=sources[i]))
          
    def flatten(t):
      return [item for sublist in t for item in sublist]

    items = [*items, *flatten(sub_portpolio)]
    ratios = [*ratios, *flatten(sub_ratios)]
    assert np.sum(ratios) <= 100, ""

    self.items = items
    self.sources = sources
  
    return [items, ratios]

  def get_correlation(self, start_date, end_date):
    """ Return
      Correation Dataframe
    """
    if platform.system() == 'Darwin':
      plt.rc('font', family='AppleGothic')
      plt.rcParams['axes.unicode_minus'] = False
    else:
      plt.rcParams["font.family"] = 'NanumGothic'

    if self.items == None:
      portpolio,_ = self.get_etf()

    raw_df = pd.DataFrame(portpolio[0].price_df[['Date']].iloc[::-1].reset_index(drop=True))
    for etf in portpolio:
      raw_df[etf.name] = etf.price_df.iloc[::-1].reset_index(drop=True)['Close']
    
    ranging_df = raw_df[(start_date<=raw_df['Date']) & (raw_df['Date']<=end_date)].iloc[::-1].reset_index(drop=True)
    #print(ranging_df)
    corr_df = ranging_df.corr(method='pearson')
    return corr_df

  def get_corr_plot(self, corr_df=None):
    """ Return
      plot()
    """
    assert corr_df.empty ==0 ,'please do get_correlation() first'

    fig, ax = plt.subplots( figsize=(7,7) )


    if 0 :    # 삼각형 마스크를 만든다(위 쪽 삼각형에 True, 아래 삼각형에 False)
      mask = np.zeros_like(corr_df, dtype=np.bool)
      mask[np.triu_indices_from(mask)] = True
    else:
      mask = 0

    sns.heatmap(corr_df, 
                cmap = 'RdYlBu_r', 
                annot = True,
                mask=mask,
                linewidths=.5,
                cbar_kws={"shrink": .5},
                vmin = -1,vmax = 1
              )  
    plt.show()

  def get_usd_krw(self,start_date:str,end_date:str,interval:int=90):
    """ Return 
      usd-krw graph
    """
    df = self.usd_krw.loc[ (self.usd_krw['Date'] >= start_date) & (self.usd_krw['Date'] <= end_date),:]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(df['Date'], df['Close'])
    plt.xticks(np.arange(0, len(df['Date'])+1, interval), rotation=45)
    plt.grid()
    plt.show()
 
"""
  LOCAL
"""
if __name__ == '__main__':
  if 1:
    po = Portpolio('CORR2')
    #start_date, end_date, _ = ['2010-02-05', '2022-01-11','']
    start_date, end_date, _ = ['2018-12-05', '2022-01-17','']
    #start_date, end_date, _ = ['2018-02-05', '2019-01-03', 'kospi양적긴축폭락장']
    corr_df = po.get_correlation(start_date=start_date, end_date=end_date)

    if 1:
      po.get_corr_plot(corr_df)
  else:
    po = Portpolio('MyPortpolio2')
    p,s=po.get_etf()
    for i in p:
      print(i.code)

    #po.get_usd_krw('2013-01-04', '2022-01-04',180)

#    usd = po.usd_krw
    #p = usd.loc[ usd['Date']=='2021-03-05' ,'Close'].to_list()[0]
   # print(p)