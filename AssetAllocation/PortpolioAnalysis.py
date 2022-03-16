import pandas as pd
from Portpolio import Portpolio
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import platform

class PortpolioAnalysis(object):
  def __init__(self, pp:Portpolio, start:str, end:str):
    self.pp = pp
    self.date = pd.date_range(start,end)

  def make_df(self):
    portpolio_df = pd.DataFrame(self.date,columns=['Date'])
    for etf in self.pp.get_etf()[0]:
      df = etf.price_df
      df.index = pd.to_datetime(df['Date'], format="%Y-%m-%d")
      df = df.reindex(self.date)
      portpolio_df[etf.name] = df['Close'].values
    return portpolio_df.dropna(axis=0).set_index('Date')

  def standardize(self, df):
    for col in df.columns:
      val = df[col].values
      mean = np.mean(val)
      std = np.std(val)
      val = (val-mean)/std
      df[col] = val
    #return df.reset_index()
    return df

  def normalize(self, df):
    for col in df.columns:
      val = df[col].values
      max = np.max(df[col].values)
      min = np.min(df[col].values)
      val = (val-min)/(max-min)
      df[col] = val
    #return df.reset_index()
    return df


  def get_correlation(self,df):
    """ Return
      Correation Dataframe
    """
    if platform.system() == 'Darwin':
      plt.rc('font', family='AppleGothic')
      plt.rcParams['axes.unicode_minus'] = False
    else:
      plt.rcParams["font.family"] = 'NanumGothic'

    df = df.corr(method='pearson')
    return df

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

  def correation(self,df):
    col = df.columns
    return np.corrcoef(df[col[0]], df[col[1]])[0,1]

if __name__ == '__main__':
    po = Portpolio('LAA')
    pa = PortpolioAnalysis(po, start='2021-01-03', end='2022-03-10')

    # 1. 전처리
    df = pa.make_df()
    if 1:
      df = pa.standardize(df=df) 
    else:
      df = pa.normalize(df=df)
    print(df)

    # 2. scatter
    if 1:
      index = df.columns
      plt.scatter(x=df[index[0]],y=df[index[2]],alpha=0.5)
      plt.xlabel(index[0])
      plt.ylabel(index[2])
    else:
      index = df.columns
      plt.plot(df[index[0]])
      plt.plot(df[index[2]])

    # 3. corr & corr_plot
    if 1:
      corr_df = pa.get_correlation(df)
      pa.get_corr_plot(corr_df)