from turtle import color
import pandas as pd
from Portpolio import Portpolio
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import platform


class DisplayResult(object):
  @staticmethod
  def scatter(ppdf):
    groupa = ppdf.loc[ppdf.index > '2022-01-03', :]
    groupb = ppdf.loc[ppdf.index <= '2022-01-03', :]
    print(len(groupa),len(groupb))
    
    index = ppdf.columns
    plt.scatter(x=groupa[index[0]],y=groupa[index[1]],alpha=0.5,color='r')
    plt.scatter(x=groupb[index[0]],y=groupb[index[1]],alpha=0.1)
    plt.xlabel(index[0])
    plt.ylabel(index[1])
    plt.show()

  @staticmethod
  def correlation_map(ppdf):
    if platform.system() == 'Darwin':
      plt.rc('font', family='AppleGothic')
      plt.rcParams['axes.unicode_minus'] = False
    else:
      plt.rcParams["font.family"] = 'NanumGothic'

    assert ppdf.empty ==0 ,'please do get_correlation()'
    fig, ax = plt.subplots( figsize=(7,7) )
    if 0 :
      mask = np.zeros_like(corr_df, dtype=np.bool)
      mask[np.triu_indices_from(mask)] = True
    else:
      mask = 0

    sns.heatmap(ppdf, cmap = 'RdYlBu_r', annot = True,
                mask=mask,linewidths=.5,cbar_kws={"shrink": .5},
                vmin = -1,vmax = 1)  
    plt.show()




class AnalysisAlgorithm(DisplayResult):
  @staticmethod
  def clustering(ppdf):
    pass

  @staticmethod
  def get_correlation(ppdf):
    ppdf = ppdf.corr(method='pearson')
    return ppdf




class Preprocessing(object):
  @staticmethod
  def make_df(pp:Portpolio, date_range):
    portpolio_df = pd.DataFrame(date_range,columns=['Date'])
    for etf in pp.get_etf()[0]:
      df = etf.price_df
      df.index = pd.to_datetime(df['Date'], format="%Y-%m-%d")
      df = df.reindex(date_range)
      
      if 'Diff' not in df.columns:
        diff = df['Close'].iloc[1:].values - df['Close'].iloc[0:-1].values
        diff = np.insert(diff, 0, 0.0, axis=0)
        df['Diff'] = diff

      portpolio_df[etf.name] = df['Diff'].values
      ret = portpolio_df.dropna(axis=0).set_index('Date')
    return ret

  @staticmethod
  def standardize(df):
    for i, col in enumerate(df.columns):
      val = df[col].values
      mean = np.mean(val)
      std = np.std(val)
      val = (val-mean)/std
      df[col] = val
    #return df.reset_index()
    return df

  @staticmethod
  def normalize(df):
    for col in df.columns:
      val = df[col].values
      max = np.max(df[col].values)
      min = np.min(df[col].values)
      val = (val-min)/(max-min)
      df[col] = val
    #return df.reset_index()
    return df


class PortpolioAnalysis(Preprocessing):
  def __init__(self, pp:Portpolio, start:str, end:str):

    self.pp = pp
    self.date = pd.date_range(start,end)
    self.ppdf = Preprocessing.make_df(pp=self.pp, date_range=self.date)

  def preprocess(self, index:int):
    ppdf = self.ppdf
    if index==0:
      self.ppdf = PortpolioAnalysis.normalize(ppdf)
    elif index==1:
      self.ppdf = PortpolioAnalysis.standardize(ppdf)
    else: 
      pass
    return self.ppdf

  def run(self,colunms, alg_index:int=0):
    #=================================================
    #               (1).Preprocess
    #=================================================
    ppdf = self.preprocess(index=1)
    ppdf = ppdf[colunms]
    
    #=================================================
    #               (2).Analysis
    #=================================================
    if alg_index:
      AnalysisAlgorithm.clustering(ppdf)
    else:
      AnalysisAlgorithm.clustering(ppdf)

    #=================================================
    #               (3).Display
    #=================================================
    DisplayResult.scatter(ppdf)


if __name__ == '__main__':
    start='2010-01-03'
    end='2022-03-10'


    yaml_name = 'Compare/SPY-SH'
    columns = ['SPY', 'SH']
    po = Portpolio(yaml_name)
    pa = PortpolioAnalysis(po, start=start, end=end)
    pa.run(colunms=columns,alg_index=0)


    yaml_name = 'Compare/QQQ-SPY'
    columns = ['QQQ', 'SPY']
    po = Portpolio(yaml_name)
    pa = PortpolioAnalysis(po, start=start, end=end)
    pa.run(colunms=columns,alg_index=0)


    yaml_name = 'Compare/SPY-IYT'
    columns = ['SPY', 'IYT']
    po = Portpolio(yaml_name)
    pa = PortpolioAnalysis(po, start=start, end=end)
    pa.run(colunms=columns,alg_index=0)

