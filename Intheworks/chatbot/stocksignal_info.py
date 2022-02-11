import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
import six
import datetime
import os

class StocksignalInfo:
  def __init__(self):
    self.url = 'http://www.stocksignals.co.kr:8080/stockguest/0025.php'
    self.item_name = 'investment-fund'

    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    self.file_name = os.path.join(BASE_PATH,'../report/%s-%s.png'%(self.item_name,self.get_report_time()))

    plt.rc('font', family='NanumGothic')
    plt.rcParams['axes.unicode_minus'] = False
    print('init')

  def parse_and_df(self):

    code_df = pd.read_html(self.url, header=0)[8]

    print(self.url)
    webpage = requests.get(self.url)
    soup = BeautifulSoup(webpage.content, "html.parser")

    html_ = str(soup.findAll("td", {"colspan":"11"}))

    df = pd.read_html(html_)[1]
    headers = df.iloc[0]
    headers2 = df.iloc[1]

    df = pd.DataFrame(df.values[2:], columns=headers)
    df.columns = pd.MultiIndex.from_tuples(zip(headers2,df.columns))

    pd.set_option('display.max_rows', 1000)
    pd.set_option('display.width', 1000)
    
    print('parse')
    return df  

  def get_report_time(self):
    return datetime.datetime.now().strftime("%Y%m%d")

  def get_filename(self):
    return self.file_name

  def render_mpl_table(self,data, col_width=3.0, row_height=0.625, font_size=14,
                      header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                      bbox=[0, 0, 1, 1], header_columns=0,
                      ax=None, **kwargs):
    if ax is None:
      size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
      fig, ax = plt.subplots(figsize=size)
      ax.axis('off')

    col = []
    for i in range(len(data.columns)):
      col.append((data.columns[i][0] + '\n' + data.columns[i][1]))

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=col, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
      cell.set_edgecolor(edge_color)
      if k[0] == 0 or k[1] < header_columns:
        cell.set_text_props(weight='bold', color='w')
        cell.set_facecolor(header_color)
      else:
        cell.set_facecolor(row_colors[k[0]%len(row_colors) ])

    print('mpl')
    return ax

  def run(self):
    df = self.parse_and_df()
    self.render_mpl_table(df, header_columns=1, col_width=3.0)
    plt.savefig(self.file_name)
    plt.close()

if __name__ == '__main__':
  item = StocksignalInfo()
  item.run()