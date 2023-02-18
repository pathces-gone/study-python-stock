import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf

def get_yf_rawdata(tickers:list):
    yf.pdr_override()
    df_price = pdr.get_data_yahoo(tickers)
    df_price.isnull().sum()
    df_price.dropna(axis=0,inplace=True)
    return df_price

def getFromYF(yf_ticker='SPY', 
              sdate = '2022-07-01',
              edate = '2022-07-10'):

    yf_cols = [yf_ticker]
    cols = yf_cols
    trading_df = pd.DataFrame([], columns=cols)

    for k in yf_cols:
        df_yf = get_yf_rawdata(yf_ticker)
        series = df_yf.loc[ (df_yf.index>=sdate) & (df_yf.index<=edate)]['Close']
        series = series.round(2)
        series.index = list(map(lambda x:str(x).split(' ')[0], series.index))
        trading_df[k] = series
    ret= trading_df.to_dict()
    return ret[yf_ticker]

if __name__ == '__main__':
    getFromYF()