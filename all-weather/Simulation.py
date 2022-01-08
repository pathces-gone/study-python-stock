import yaml
import os, datetime, requests
import numpy as np
import ETFUtils
from ETF import ETF
from Portpolio import Portpolio
import pandas as pd

PRINT_BUY_PORTPOLIO  = True
PRINT_SELL_PORTPOLIO = True

class Simulation(object):
  """ Return Simulation
    Simulation Root node of Portpolio (ETF chain)
  """
  def __init__(self, portpolio:Portpolio, capital:int):
    self.portpolio = portpolio
    self.capital = capital
    self.cash    = capital


    self.avg_price = dict()
    self.hold_qtys = dict()
    self.earn= dict()

    for etf in portpolio.get_etf()[0]:
      self.avg_price[etf.code]  =0 
      self.hold_qtys[etf.code]  =0
      self.earn[etf.code] =0


  def buy(self, etf:ETF, date:str ,qty:int=0):
    """ Return

    """
    last_qty = self.hold_qtys[etf.code]

    add_qty = qty
    curr_price = etf.get_price(date=date)

    if curr_price*add_qty <= self.cash:
      self.hold_qtys[etf.code]  = last_qty + add_qty
      self.avg_price[etf.code] = (self.avg_price[etf.code]*last_qty+curr_price*add_qty)/self.hold_qtys[etf.code]
      self.cash -= curr_price*add_qty
      ret = True
    else:
      ret = False
    return ret


  def sell(self, etf:ETF, date:str ,qty:int=0):
    """ Return

    """
    last_qty = self.hold_qtys[etf.code]
    value    = self.earn[etf.code]

    sell_qty = qty
    curr_price = etf.get_price(date=date)

    if last_qty >= sell_qty:
      self.hold_qtys[etf.code]  = last_qty - sell_qty
      self.earn[etf.code] += (curr_price - self.avg_price[etf.code])*sell_qty
      self.cash += curr_price*sell_qty
      ret = True
    else:
      ret = False
    return ret    



  def print_info(self):
    """ Return

    """
    etfs,_ = self.portpolio.get_etf()
    print('Portpoilo Info - %s'%self.portpolio.name)
    print("%20s | %30s %20s | %10s %10s %10s %10s %10s"%('index','name','code','ratio(%)', 'price', 'qty', 'buy', 'earn'))
    print('-'*140)
    total_buy = 0
    for i,etf in enumerate(etfs):
      qty   = self.hold_qtys[etf.code]
      price  = self.avg_price[etf.code]
      value = qty*price
      ratios = (value/self.capital*100)

      earn = self.earn[etf.code]
      total_buy += value

      print("%20s | %s %20s | %10.2f %10d %10d %10d %10d"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code,ratios, price, qty, value,earn) )
    print('-'*140)
    print('Total:')
    print('\tbudget: %10d\n\t\tbuy: %10d\n\t\tcash: %10d  \n\n'%(self.capital,total_buy,self.cash))
    print('\tcurr/budget=%12d/%12d [%4.2f%%]'%(total_buy+self.cash, self.capital,(total_buy+self.cash)/self.capital*100))



  def buy_portpolio(self, date:str):
    """ Return

    """
    capital = self.capital
    etfs,ratios = self.portpolio.get_etf()
    budgets = np.multiply(ratios,0.01*capital)
    prices  = [etf.get_price(date=date) for etf in etfs]

    qtys = np.array([],np.int32)
    for i,etf in enumerate(etfs):
      qtys = np.append(qtys, int(budgets[i]/prices[i]))

    if PRINT_BUY_PORTPOLIO==True:
      print('\nBuy - %s'%self.portpolio.name)
      print("%20s | %30s %20s | %10s %10s %10s %10s %10s"%('index','name','code','budget','ratio(%)', 'price', 'qty', 'buy'))
      print('-'*140)
      total_buy = 0
      for i,etf in enumerate(etfs):
        self.buy(etf=etf, date=date, qty=qtys[i])
        total_buy += prices[i]*qtys[i] 
        print("%20s | %s %20s | %10d %10.2f %10d %10d %10d"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code,budgets[i],ratios[i],prices[i],qtys[i], prices[i]*qtys[i]) )
      print('-'*140)
      print('Total: %10d\n\n'%total_buy)
    else:
      total_buy = 0
      for i,etf in enumerate(etfs):
        self.buy(etf=etf, date=date, qty=qtys[i])
        total_buy +=  prices[i]*qtys[i]

    return [total_buy, prices, qtys]


  def sell_portpolio(self, date:str,buy_prices:np.ndarray, buy_qtys:np.ndarray):
    """ Return
      
    """
    etfs,ratios = self.portpolio.get_etf()
    prices  = [etf.get_price(date=date) for etf in etfs]

    if PRINT_SELL_PORTPOLIO==True:
      print('\nSell - %s'%self.portpolio.name)
      print("%20s | %30s %20s | %10s %10s %15s %10s %10s %15s"%('index','name','code','buy','ratio(%)', 'sell price', 'qty', 'sell', 'earn ratio(%)'))
      print('-'*160)
      total_sell = 0
      for i,etf in enumerate(etfs):
        self.sell(etf=etf, date=date, qty=buy_qtys[i])
        total_sell +=  prices[i]*buy_qtys[i]
        earn_ratio = (prices[i]-buy_prices[i])/buy_prices[i]*buy_qtys[i]
        print("%20s | %s %20s | %10d %10.2f %15d %10d %10d %15.2f"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code,  buy_prices[i]*buy_qtys[i] ,ratios[i], prices[i], buy_qtys[i], prices[i]*buy_qtys[i], earn_ratio))
      print('-'*160)
      print('Total: %10d\n\n'%total_sell)
    else:
      total_sell = 0
      for i,etf in enumerate(etfs):
        self.sell(etf=etf, date=date, qty=buy_qtys[i])
        total_sell +=  prices[i]*buy_qtys[i]

    return total_sell
  

  def Run(self, start_date:str, end_date:str):
    if 0:
      total_buy, buy_prices, buy_qtys = self.buy_portpolio(date=start_date)
      total_sell = self.sell_portpolio(date=end_date, buy_prices=buy_prices, buy_qtys=buy_qtys)

      earn_ratio = round((total_sell-total_buy)/total_buy*100, 2)
      print("GTAA - %12s to %12s:   buy=%10d, sell=%10d, earn_ratio=%10.2f%%\n"%(start_date,end_date,total_buy,total_sell,earn_ratio))
    else:
      """ Algorithm
        시작시간부터 하루하루 넘어가면서 simulation
        * (지수저가이평 220일선 기준 buy-sell)
      """
      _end_date = datetime.datetime.strptime(end_date,"%Y-%m-%d")

      total_buy, buy_prices, buy_qtys = self.buy_portpolio(date=start_date)

      etfs,ratios = self.portpolio.get_etf()
      self.print_info()

      # make stratgy
      pivot_date = datetime.datetime.strptime(start_date,"%Y-%m-%d")

      while(pivot_date < _end_date):
        """
          Stratgy
        """
        #commend,s_qty = strategy()
        commend,s_qty = ['SELL',10]

        if commend == 'SELL':
          self.sell(etf=etfs[0],date=pivot_date.strftime('%Y-%m-%d'),qty=s_qty)
        elif commend == 'BUY':
          self.buy(etf=etfs[0],date=pivot_date.strftime('%Y-%m-%d'),qty=s_qty)
        else:
          pass

        pivot_date = ETFUtils.get_next_date(pivot_date)

      self.print_info()


if __name__ == '__main__':
  portpolio_name = 'GTAA'
  portpolio = Portpolio(portpolio_name)
  capital = 10_000_000


  start_date  = '2018-11-03'
  end_date = '2019-04-03'
  sim = Simulation(portpolio=portpolio, capital=capital).Run(start_date= start_date, end_date= end_date)
  #sim = Simulation(portpolio=portpolio, capital=capital).print_info()
  

  if 0:
    etfs,_ = portpolio.get_etf()
    print(etfs[0])
    etfs[0].get_chart()