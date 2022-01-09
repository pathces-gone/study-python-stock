import yaml
import os, datetime, requests
import numpy as np
import ETFUtils
from ETF import ETF
from Portpolio import Portpolio
import pandas as pd
import Strategy


PRINT_BUY_PORTPOLIO  = False
PRINT_SELL_PORTPOLIO = False

class Simulation(object):
  """ Return Simulation
    Simulation Root node of Portpolio (ETF chain)
  """
  def __init__(self, portpolio:Portpolio, capital:int):
    self.portpolio = portpolio

    self.budgets = capital
    self.capital = capital
    self.cash    = capital

    # ETFs Data
    self.max_ratios = dict()
    self.curr_ratios = dict()
    self.max_qty = dict()
    self.avg_price = dict()
    self.hold_qtys = dict()
    self.earn= dict()

    for etf in portpolio.get_etf()[0]:
      self.avg_price[etf.code]  =0 
      self.hold_qtys[etf.code]  =0
      self.earn[etf.code] =0


  def buy(self, etf:ETF, date:str, percent:float):
    """ Return

    """
    last_qty = self.hold_qtys[etf.code]
    curr_price = etf.get_price(date=date)

    buy_percent = (self.max_ratios[etf.code]*(percent/100))
    buy_qty = int(buy_percent*self.capital/100 / curr_price)


    over = (self.avg_price[etf.code]*self.hold_qtys[etf.code] + buy_qty*curr_price)/(self.capital)*100

    if (curr_price*buy_qty <= self.cash):
      if (over <= self.max_ratios[etf.code]):
        self.hold_qtys[etf.code]  = last_qty + buy_qty
        self.avg_price[etf.code] = (self.avg_price[etf.code]*last_qty+curr_price*buy_qty)/self.hold_qtys[etf.code] if self.hold_qtys[etf.code] else 0
        self.cash -= curr_price*buy_qty
        ret = True
      else:
        ret=False
    else:
      ret = False

    #self.curr_ratios[etf.code] = self.avg_price[etf.code]*self.hold_qtys[etf.code]/self.capital*100
    return ret


  def sell(self, etf:ETF, date:str, percent:float):
    """ Return

    """
    last_qty = self.hold_qtys[etf.code]
    value    = self.earn[etf.code]

    curr_price = etf.get_price(date=date)
    sell_qty = self.hold_qtys[etf.code]*(percent/100)
    
    if last_qty >= sell_qty:
      self.hold_qtys[etf.code]  = last_qty - sell_qty
      self.earn[etf.code] += (curr_price - self.avg_price[etf.code])*sell_qty
      self.cash += curr_price*sell_qty
      #self.capital = self.cash + self.avg_price[etf.code]*self.hold_qtys[etf.code]
      ret = True
    else:
      ret = False

    return ret    



  def print_info(self):
    """ Return

    """
    etfs,_ = self.portpolio.get_etf()
    print('Portpoilo Info - %s'%self.portpolio.name)
    print("%20s | %30s %20s | %10s %10s %10s %10s %10s %10s"%('index','name','code', 'max(%)','ratio(%)', 'price', 'qty', 'buy', 'earn'))
    print('-'*150)
    total_buy = 0
    for i,etf in enumerate(etfs):
      qty   = self.hold_qtys[etf.code]
      max_ratio = self.max_ratios[etf.code]
      price  = self.avg_price[etf.code]
      value = qty*price
      ratios = self.curr_ratios[etf.code]
      earn = self.earn[etf.code]
      total_buy += value

      print("%20s | %s %20s | %10.2f %10.2f %10d %10d %10d %10d"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code,max_ratio,ratios, price, qty, value,earn) )
    print('-'*150)
    print('Total:')
    print('\tbudget: %10d\n\t\tbuy: %10d\n\t\tcash: %10d  \n\n'%(self.budgets,total_buy,self.cash))
    print('\tcurr/budget=%12d/%12d [%4.2f%%]'%(total_buy+self.cash, self.budgets,(total_buy+self.cash)/self.budgets*100))
    print('\n\n')


  def buy_portpolio(self, date:str):
    """ Return

    """
    capital = self.capital
    etfs,ratios = self.portpolio.get_etf()
    budgets = np.multiply(ratios,0.01*capital)
    prices  = [etf.get_price(date=date) for etf in etfs]

    qtys = np.array([],np.int32)
    for i,etf in enumerate(etfs):
      self.max_ratios[etf.code] = ratios[i]
      self.curr_ratios[etf.code]= ratios[i]
      qtys = np.append(qtys, int(budgets[i]/prices[i]))

    if PRINT_BUY_PORTPOLIO==True:
      print('\nBuy - %s'%self.portpolio.name)
      print("%20s | %30s %20s | %10s %10s %10s %10s %10s"%('index','name','code','budget','ratio(%)', 'price', 'qty', 'buy'))
      print('-'*140)
      total_buy = 0
      for i,etf in enumerate(etfs):
        self.buy(etf=etf, date=date, percent=100)
        total_buy += prices[i]*qtys[i] 
        print("%20s | %s %20s | %10d %10.2f %10d %10d %10d"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code,budgets[i],ratios[i],prices[i],qtys[i], prices[i]*qtys[i]) )
      print('-'*140)
      print('Total: %10d\n\n'%total_buy)
    else:
      total_buy = 0
      for i,etf in enumerate(etfs):
        self.buy(etf=etf, date=date, percent=100)
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
        self.sell(etf=etf, date=date, percent=100)
        total_sell +=  prices[i]*buy_qtys[i]
        earn_ratio = (prices[i]-buy_prices[i])/buy_prices[i]*buy_qtys[i]
        print("%20s | %s %20s | %10d %10.2f %15d %10d %10d %15.2f"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code,  buy_prices[i]*buy_qtys[i] ,ratios[i], prices[i], buy_qtys[i], prices[i]*buy_qtys[i], earn_ratio))
      print('-'*160)
      print('Total: %10d\n\n'%total_sell)
    else:
      total_sell = 0
      for i,etf in enumerate(etfs):
        self.sell(etf=etf, date=date, percent=100)
        total_sell +=  prices[i]*buy_qtys[i]

    return total_sell
  

  def Run(self, start_date:str, end_date:str, what:str):
    """ Algorithm
      시작시간부터 하루하루 넘어가면서 simulation
    """
    _end_date = datetime.datetime.strptime(end_date,"%Y-%m-%d")

    total_buy, buy_prices, buy_qtys = self.buy_portpolio(date=start_date)

    etfs,ratios = self.portpolio.get_etf()
    self.print_info()

    pivot_date = datetime.datetime.strptime(start_date,"%Y-%m-%d")
    while(pivot_date < _end_date):
      """
        Stratgy
      """
      res_buy=0
      for i,etf in enumerate(etfs):
        if what == 'dual_momentum':
          commend,s_qty = Strategy.Strategy.dual_momentum(etf=etfs[i],date=pivot_date)
        elif what == 'abs_momentum':
          commend,s_qty = Strategy.Strategy.abs_momentum(etf=etfs[i],date=pivot_date)
        else:
          commend,s_qty = Strategy.Strategy.hold(etf=etfs[i])

        if commend == 'SELL':
          self.sell(etf=etfs[i],date=pivot_date.strftime('%Y-%m-%d'),percent=s_qty)
        elif commend == 'BUY':
          self.buy(etf=etfs[i],date=pivot_date.strftime('%Y-%m-%d'),percent=s_qty)
        else:
          pass
        res_buy += self.hold_qtys[etf.code]*self.avg_price[etf.code]
      
      self.capital = self.cash + res_buy
      for i,etf in enumerate(etfs):
        self.curr_ratios[etf.code] = (self.avg_price[etf.code]*self.hold_qtys[etf.code])/(self.capital)*100

      pivot_date = ETFUtils.get_next_date(pivot_date)

    #self.print_info()
    for i,etf in enumerate(etfs):
      self.sell(etf=etf,date=_end_date.strftime('%Y-%m-%d'),percent=self.hold_qtys[etf.code])
    self.print_info()


if __name__ == '__main__':
  #portpolio_name = 'GTAA'
  #portpolio_name = 'GTAA-NON'
  portpolio_name = 'AW'
  portpolio = Portpolio(portpolio_name)
  capital = 10_000_000


  start_date  = '2019-04-02'
  end_date = '2020-04-05'
  sim = Simulation(portpolio=portpolio, capital=capital).Run(start_date= start_date, end_date= end_date, what='abs_momentum')
  #sim = Simulation(portpolio=portpolio, capital=capital).Run(start_date= start_date, end_date= end_date, what='hold')
  #sim = Simulation(portpolio=portpolio, capital=capital).print_info()
  

  if 0:
    etfs,_ = portpolio.get_etf()
    print(etfs[0])
    etfs[0].get_chart()