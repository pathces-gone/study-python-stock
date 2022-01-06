import pandas as pd
from pandas.core.series import Series
from bs4 import BeautifulSoup as bs
import datetime
import os

from urllib.request import urlopen, Request

class ETFTable(object):
  @staticmethod
  def get_tables():
    url = "https://comp.wisereport.co.kr/ETF/lookup.aspx"
    req = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    html_text = urlopen(req).read()

    soup = bs(html_text, 'lxml')

    tag_indices = soup.find_all(name='td', attrs='c1 center')
    tag_codes  = soup.find_all(name='td', attrs='c2 center')
    tag_names  = soup.find_all(name='td', attrs='c3 txt')

    return [tag_indices, tag_codes, tag_names]


if __name__ == '__main__':
  url = "https://comp.wisereport.co.kr/ETF/lookup.aspx"
  req = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
  html_text = urlopen(req).read()

  soup = bs(html_text, 'lxml')

  tag_indices = soup.find_all(name='td', attrs='c1 center')
  print(tag_indices[4].text)

  tag_codes  = soup.find_all(name='td', attrs='c2 center')
  print(tag_codes[4].text)

  tag_names  = soup.find_all(name='td', attrs='c3 txt')
  print(tag_names[4].text)