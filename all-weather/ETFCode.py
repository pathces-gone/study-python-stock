import pandas as pd
from pandas.core.series import Series
from bs4 import BeautifulSoup as bs
import datetime
import os

from urllib.request import urlopen, Request
import yaml

class ETFTable(object):
  @staticmethod
  def get_tables():
    url = "https://comp.wisereport.co.kr/ETF/lookup.aspx"
    req = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    html_text = urlopen(req).read()

    soup = bs(html_text, 'lxml')

    tag_indices = soup.find_all(name='td', attrs='c1 center')
    tag_codes   = soup.find_all(name='td', attrs='c2 center')
    tag_names   = soup.find_all(name='td', attrs='c3 txt')
    return [tag_indices, tag_codes, tag_names]

  @staticmethod
  def get_code(etf:str):
    tag_indices, tag_codes, tag_names= ETFTable().get_tables()
    for i, name in enumerate(tag_names):
      #print(name.text, i)
      if name.text.find(etf) != -1:
        print(name.text,tag_codes[i].text)
        #return tag_codes[i].text
    return 0

if __name__ == '__main__':
  etf = ETFTable()
  
  n1 = '200'
  c1 = etf.get_code(etf = n1)
  