import pandas as pd
from Portpolio import Portpolio
import numpy as np
import matplotlib.pyplot as plt

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
    return portpolio_df.dropna(axis=0)

  def standardize(self, df):
    df = df.set_index('Date')
    for col in df.columns:
      val = df[col].values
      mean = np.mean(val)
      std = np.std(val)
      val = (val-mean)/std
      df[col] = val
    #return df.reset_index()
    return df

  def normalize(self, df):
    df = df.set_index('Date')
    for col in df.columns:
      val = df[col].values
      max = np.max(df[col].values)
      min = np.min(df[col].values)
      val = (val-min)/(max-min)
      df[col] = val
    #return df.reset_index()
    return df


  def correation(self,df):
    col = df.columns
    return np.corrcoef(df[col[0]], df[col[1]])[0,1]

if __name__ == '__main__':
    po = Portpolio('MyPortpolio')
    pa = PortpolioAnalysis(po, start='2018-01-03', end='2022-03-10')
    df = pa.make_df()
    if 0:
      df = pa.standardize(df=df)
    else:
      df = pa.normalize(df=df)
    print(df)

    index = df.columns
    plt.scatter(x=df[index[0]],y=df[index[1]],alpha=0.5)
    print(pa.correation(df))