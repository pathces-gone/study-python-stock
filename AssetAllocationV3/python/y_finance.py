import pandas as pd
import yfinance as yf
import os
from pandas_datareader import data as pdr


def get_yf_rawdata(tickers:list):
    yf.pdr_override()
    df_price = pdr.get_data_yahoo(tickers)
    df_price.isnull().sum()
    df_price.dropna(axis=0,inplace=True)
    return df_price

def getFromYF(yf_ticker='SPY', 
              sdate = '2022-07-01',
              edate = '2022-07-10'):
    prj_dir = os.path.abspath(os.path.dirname(__file__))
    prj_dir = os.path.join(prj_dir,"..")
    csv_file= "%s_%s_to_%s"%(yf_ticker, sdate, edate) + ".csv"
    csv_path= os.path.join(prj_dir,"csv",csv_file)
    if os.path.exists(csv_path):
        ret = pd.read_csv(csv_path).set_index('Unnamed: 0')
        ret = ret.to_dict()[yf_ticker]
        return ret

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
    trading_df.to_csv(csv_path,encoding='utf-8')

    #     self.usd_krw = fdr.DataReader('USD/KRW')
    # self.usd_krw = self.usd_krw.reset_index()
    # self.usd_krw = ETFUtils.append_missing_trading_date(self.usd_krw)
    # self.usd_krw.to_csv(usd_krw_path,encoding='utf-8', index=False)


    return ret[yf_ticker]

if __name__ == '__main__':
    ret = getFromYF()