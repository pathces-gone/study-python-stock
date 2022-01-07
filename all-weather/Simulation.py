import yaml
import os, datetime, requests
import numpy as np
import ETFUtils
import pandas as pd


class ETF(object):
  """ Return ETF
    ETF object
  """
  def __init__(self, name:str, code:str, index:str):
    self.name  =name
    self.code  =code
    self.index =index
    self.path = os.path.join('fsdata','%s.csv'%self.code)

  def get_price(self, date:str):
    if os.path.exists(self.path):
      price_df = pd.read_csv(self.path)
    else:
      price_df = ETFUtils.utils_get_price(code=self.code,page=100)
      price_df.to_csv(self.path,encoding='utf-8')

    price = price_df.loc[price_df['Date'] == date]['Close'].to_list()[0]
    return price


class Portpolio(object):
  """ Return Portpolio
    Portpolio Node (ETF chain)
  """
  def __init__(self, name):
    self.name = name

  @staticmethod
  def get_yaml(index:str)->list:
    yaml_file_path = os.path.join(os.path.dirname(__file__))
    with open(os.path.join(yaml_file_path, '%s.yaml'%index)) as f:
      conf = yaml.load(f, Loader=yaml.FullLoader)
    return conf

  def get_etf(self):
    name = self.name
    yaml = Portpolio.get_yaml(name)

    etf_name = np.array([])
    etf_code = np.array([])
    cmds = np.array([], np.int32)
    ratios = np.array([], np.float32)

    sub_portpolio = []
    sub_ratios = []
    for i,label in enumerate(yaml[name].values()):
      for sub_label in label:
        if sub_label['etf'].find('/') != -1:
          sub_portpolio, sub_ratios = Portpolio(name=sub_label['etf'][1:]).get_etf()
          sub_ratios = [(sub_label['ratio']/100)*sr for sr in sub_ratios]
          continue
        etf_code   = np.append(etf_code, sub_label['etf'])  
        etf_name   = np.append(etf_name, sub_label['comment'])
        ratios = np.append(ratios,sub_label['ratio'])
        cmds = np.append(cmds, i)

    portpolio = []
    for i,etf in enumerate(etf_code):
      tmp = list(yaml[name].keys())
      portpolio.append( ETF(name=etf_name[i], code=etf_code[i], index= tmp[cmds[i]]))
    
    portpolio = [*portpolio, *sub_portpolio]
    ratios = [*ratios, *sub_ratios]
    assert np.sum(ratios) == 100, ""

    return [portpolio, ratios]


class Simulation(object):
  """ Return Simulation
    Simulation Root node of Portpolio (ETF chain)
  """
  def __init__(self, portpolio:Portpolio, capital:int):
    self.portpolio = portpolio
    self.capital = capital

  def buy(self, date:str):
    capital = self.capital
    etfs,ratios = self.portpolio.get_etf()
    budgets = np.multiply(ratios,0.01*capital)
    prices  = [etf.get_price(date=date) for etf in etfs]

    qtys = np.array([],np.int32)
    for i,etf in enumerate(etfs):
      qtys = np.append(qtys, int(budgets[i]/prices[i]))

    print('\nBuy - %s'%self.portpolio.name)
    print("%20s | %30s %20s | %10s %10s %10s %10s %10s"%('index','name','code','budget','ratio(%)', 'price', 'qty', 'buy'))
    print('-'*140)
    total_buy = 0
    for i,etf in enumerate(etfs):
      total_buy +=  prices[i]*qtys[i] 
      print("%20s | %s %20s | %10d %10.2f %10d %10d %10d"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code,budgets[i],ratios[i],prices[i],qtys[i], prices[i]*qtys[i]) )
    
    print('Total: %10d\n\n'%total_buy)
    return [total_buy, prices, qtys]


  def sell(self, date:str,buy_prices:np.ndarray, buy_qtys:np.ndarray):
    etfs,ratios = self.portpolio.get_etf()
    prices  = [etf.get_price(date=date) for etf in etfs]

    print('\nSell - %s'%self.portpolio.name)
    print("%20s | %30s %20s | %10s %10s %10s %10s %10s"%('index','name','code','buy','ratio(%)', 'sell price', 'qty', 'sell'))
    print('-'*140)
    total_sell = 0
    for i,etf in enumerate(etfs):
      total_sell +=  prices[i]*buy_qtys[i] 
      print("%20s | %s %20s | %10d %10.2f %10d %10d %10d"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code,  buy_prices[i]*buy_qtys[i] ,ratios[i],buy_prices[i], buy_qtys[i], prices[i]*buy_qtys[i]))
    
    print('Total: %10d\n\n'%total_sell)
    return total_sell
    


if __name__ == '__main__':
  portpolio_name = 'GTAA'
  capital = 10_000_000

  buy_date  = '2021-10-22'
  sell_date = '2022-01-03'

  sim = Simulation(portpolio=Portpolio(portpolio_name), capital=capital)
  total_buy, buy_prices, buy_qtys = sim.buy(date=buy_date)
  total_sell = sim.sell(date=sell_date, buy_prices=buy_prices, buy_qtys=buy_qtys)
  
  earn_ratio = round((total_sell-total_buy)/total_buy*100, 2)
  print("GTAA - %12s to %12s:   buy=%10d, sell=%10d, earn_ration=%10.2f"%(buy_date,sell_date,total_buy,total_sell,earn_ratio))
  #today = datetime.datetime.now().strftime("%Y%m%d")