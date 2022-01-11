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
FORWARD_VALUE_ESTIMATE = True #  # FALSE - Has Bug
LIMIT_RATIO = True


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

    if LIMIT_RATIO:
      over = (self.avg_price[etf.code]*self.hold_qtys[etf.code] + buy_qty*curr_price)/(self.capital)*100
    else:
      over = 0
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
      ret = True
    else:
      ret = False

    return ret    



  def print_info(self):
    """ Return

    """
    etfs,_ = self.portpolio.get_etf()
    print('='*150)
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
    print('\tbudget: %10d\n\t\tbuy: %10d\n\t\tcash: %10d'%(self.budgets,total_buy,self.cash))
    print('\tcurr/budget=%12d/%12d [%4.2f%%]'%(total_buy+self.cash, self.budgets,(total_buy+self.cash)/self.budgets*100))
    print('='*150)


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
    #self.print_info()

    max_capital = self.capital
    min_capital = self.capital
    max_draw_down = 0
    res_sell_all = 0

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
        elif what == 'abs_momentum2':
          commend,s_qty = Strategy.Strategy.abs_momentum2(etf=etfs[i],date=pivot_date)
        else:
          commend,s_qty = Strategy.Strategy.hold(etf=etfs[i])


        arg_date = pivot_date.strftime('%Y-%m-%d')
        if commend == 'SELL':
          self.sell(etf=etfs[i],date=arg_date,percent=s_qty)
        elif commend == 'BUY':
          self.buy(etf=etfs[i],date=arg_date,percent=s_qty)
        else:
          pass

        if FORWARD_VALUE_ESTIMATE:
          res_buy += self.hold_qtys[etf.code]*etf.get_price(date=arg_date) #trailing value
        else:
          res_buy += self.hold_qtys[etf.code]*self.avg_price[etf.code] #trailing value
          res_sell_all += self.hold_qtys[etf.code]*etf.get_price(date=arg_date) 
      # Trading Result
      self.capital = self.cash + res_buy

      if FORWARD_VALUE_ESTIMATE:
        res_sell_all = self.capital
      else:
        res_sell_all = res_sell_all + self.cash
    
      for i,etf in enumerate(etfs):
        self.curr_ratios[etf.code] = (self.avg_price[etf.code]*self.hold_qtys[etf.code])/(self.capital)*100

      min_capital = res_sell_all if(res_sell_all<min_capital) else min_capital
      max_capital = res_sell_all if(res_sell_all>=max_capital) else max_capital

      # Next day
      pivot_date = ETFUtils.get_next_date(pivot_date)


    #self.print_info()
    for i,etf in enumerate(etfs):
      self.sell(etf=etf,date=_end_date.strftime('%Y-%m-%d'),percent=100)

    # MDD
    max_draw_down = (min_capital-self.budgets)/self.budgets*100
    
    self.print_info()
    print("Max:%10d\nMin:%10d\nMDD: %.2f[%%]"%(max_capital,min_capital,max_draw_down))

if __name__ == '__main__':
  capital = 1_000_000


  #start_date, end_date = ['2021-04-03', '2021-10-06']
  #start_date, end_date = ['2021-04-03', '2021-12-06']
  start_date, end_date, _ = ['2018-02-05', '2019-01-03', 'kospi양적긴축폭락장']
  if 0:
    #portpolio_name = 'GTAA-NON'
    #portpolio_name = 'AW'
    #portpolio_name = 'MyPortpolio'
    portpolio_name = 'DANTE'
    portpolio = Portpolio(portpolio_name)
    #sim = Simulation(portpolio=portpolio, capital=capital).Run(start_date= start_date, end_date= end_date, what='abs_momentum')
    #print('\n'*5)
    #sim = Simulation(portpolio=portpolio, capital=capital).Run(start_date= start_date, end_date= end_date, what='abs_momentum2')
    #print('\n'*5)
    #sim = Simulation(portpolio=portpolio_a, capital=capital).Run(start_date= start_date, end_date= end_date, what='hold')
  else:
    portpolio_name_a = 'MyPortpolio'
    portpolio_name_b = 'GTAA-H'
    portpolio_a = Portpolio(portpolio_name_a)
    portpolio_b = Portpolio(portpolio_name_b)
    sim = Simulation(portpolio=portpolio_a, capital=capital).Run(start_date= start_date, end_date= end_date, what='hold')
    sim = Simulation(portpolio=portpolio_b, capital=capital).Run(start_date= start_date, end_date= end_date, what='hold')


  if 0:
    etfs,_ = portpolio.get_etf()
    etfs[0].get_chart()
    etfs[1].get_chart()