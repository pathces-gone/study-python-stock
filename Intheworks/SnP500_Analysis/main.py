from pandas.core.frame import DataFrame
from pandas.core.series import Series
from pandas_datareader import data as pdr
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests

import numpy as np
import matplotlib.pyplot as plt

def get_html_table(url:str):
    headers =  {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
    response = requests.get(url, headers=headers)
    html = bs(response.text, 'lxml')
    html_table = html.select('table') 
    return str(html_table)


def plot_snp_earning_yield():
    def get_snp_earning_yield():
        url = 'https://www.multpl.com/s-p-500-earnings-yield/table/by-month'
        html_table = get_html_table(url)
        df = pd.read_html(html_table, header=0)[0]
        value = np.array([])
        for v in df['Value Value']:
            value = np.append(value, float(v[:v.find('%')]))
        value = pd.DataFrame(value,columns=['Value'])
        date = df['Date']
        df = pd.concat([date,value],axis=1)
        return df

    snp_earning_yield = get_snp_earning_yield()

    start = 0
    end = 100
    snp_earning_yield = snp_earning_yield.iloc[start:end+1]
    plt.figure(figsize=[8,4])
    plt.plot(snp_earning_yield['Date'].iloc[::-1], snp_earning_yield['Value'].iloc[::-1])
    plt.xticks([snp_earning_yield['Date'][start],snp_earning_yield['Date'][(start+end)/2],snp_earning_yield['Date'][end]])
    #plt.yticks(np.arange(1,7,0.5))
    #plt.show()


def plot_snp_dividend_yield():
    def get_snp_dividend_yield():
        url = 'https://www.multpl.com/s-p-500-dividend-yield/table/by-month'
        html_table = get_html_table(url)
        df = pd.read_html(html_table, header=0)[0]
        value = np.array([])
        for v in df['Yield Value']:
            value = np.append(value, float(v[:v.find('%')]))
        value = pd.DataFrame(value,columns=['Value'])
        date = df['Date']
        df = pd.concat([date,value],axis=1)
        return df

    snp_dividend_yield = get_snp_dividend_yield()

    start = 0
    end = 100
    snp_dividend_yield = snp_dividend_yield.iloc[start:end+1]
    plt.figure(figsize=[8,4])
    plt.plot(snp_dividend_yield['Date'].iloc[::-1], snp_dividend_yield['Value'].iloc[::-1])
    plt.xticks([snp_dividend_yield['Date'][start],snp_dividend_yield['Date'][(start+end)/2],snp_dividend_yield['Date'][end]])
    #plt.yticks(np.arange(1,7,0.5))
   #plt.show()



if __name__ == '__main__':
    plot_snp_earning_yield()
    plot_snp_dividend_yield()

    #https://www.multpl.com/s-p-500-earning-yield/table/by-month