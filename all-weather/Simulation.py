from audioop import avg
from matplotlib.pyplot import draw
import yaml
import os, datetime, requests
import numpy as np
import ETFUtils
from ETF import ETF
from Portpolio import Portpolio
import pandas as pd
import Strategy


PRINT_TRADE_LOG = False
PRINT_BUY_PORTPOLIO  = False#False #True
PRINT_SELL_PORTPOLIO = False #False
LIMIT_RATIO = True # ??


class Simulation(object):
  """ Return Simulation
    Simulation Root node of Portpolio (ETF chain)
  """
  def __init__(self, portpolio:Portpolio, capital:int, report_name:str):
    self.portpolio = portpolio
    if report_name != None:
      self.report_name = os.path.join('sim-result',report_name+'.png')
      self.do_save = True
    else:
      self.do_save = False
    self.init_budgets = capital
    self.budgets = capital # constant init value
    self.capital = capital # reblanced value
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


  def buy(self, etf:ETF, date:str, percent:float)->list:
    """ Return [update_hold_qtys, update_avg_price, update_cash]
  
    """
    last_qty = self.hold_qtys[etf.code]
    curr_price = etf.get_price(date=date)
    avg_price = self.avg_price[etf.code]
    if avg_price == 0:
      avg_price = curr_price
    buy_percent = (self.max_ratios[etf.code]*(percent/100))
    buy_qty = int(buy_percent*self.capital/100 / curr_price)

    if LIMIT_RATIO:
      over = (self.avg_price[etf.code]*self.hold_qtys[etf.code] + buy_qty*curr_price)/(self.capital)*100
    else:
      over = 0
    if (curr_price*buy_qty <= self.cash):
      if (over <= self.max_ratios[etf.code]):
        update_hold_qtys = last_qty + buy_qty
        update_avg_price = (avg_price*last_qty+curr_price*buy_qty)/update_hold_qtys
        update_cash = self.cash - curr_price*buy_qty
        ret = [update_hold_qtys, update_avg_price, update_cash]
      else:
        ret= [last_qty, avg_price, self.cash]
    else:
      ret = [last_qty, avg_price, self.cash]
    return ret


  def sell(self, etf:ETF, date:str, percent:float)->list:
    """ Return [update_hold_qtys, update_earn, update_cash]

    """
    last_qty  = int(self.hold_qtys[etf.code])
    last_earn = self.earn[etf.code]

    curr_price = etf.get_price(date=date)
    sell_qty = int(self.hold_qtys[etf.code]*(percent/100))
    #print(last_qty,sell_qty)
    if last_qty >= sell_qty:
      update_hold_qtys = last_qty - sell_qty
      update_earn = (curr_price - self.avg_price[etf.code])*sell_qty
      update_cash = self.cash + curr_price*sell_qty
      ret = [update_hold_qtys, update_earn, update_cash]
    else:
      ret = [last_qty, last_earn, self.cash]
    return ret    



  def print_info(self):
    """ Return

    """
    etfs,_ = self.portpolio.get_etf()
    print('='*160)
    print('Portpoilo Info - %s'%self.portpolio.name)
    print("%20s | %30s %20s | %10s %10s %10s %10s %10s %10s %12s"%('index','name','code', 'max(%)','ratio(%)', 'price', 'qty', 'buy', 'earn','earn_ratio'))
    print('-'*160)
    total_buy = 0
    for i,etf in enumerate(etfs):
      qty   = self.hold_qtys[etf.code]
      max_ratio = self.max_ratios[etf.code]
      price  = round(self.avg_price[etf.code],2)
      value = qty*price
      ratios = self.curr_ratios[etf.code]
      earn = self.earn[etf.code]
      total_buy += value
      earn_ratio = round(earn/(self.capital*max_ratio)*100*100,2)

      print("%20s | %s %20s | %10.2f %10.2f %10.2f %10d %10d %10d %12.2f"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code,max_ratio,ratios, price, qty, value,earn,earn_ratio) )
    print('-'*160)
    print('Total:')
    print('\tbudget: %10d\n\t\tbuy: %10d\n\t\tcash: %10d'%(self.budgets,total_buy,self.cash))
    print('\tcurr/budget=%12d/%12d [%4.2f%%]'%(total_buy+self.cash, self.budgets,(total_buy+self.cash)/self.budgets*100))
    print('='*160)


  def buy_portpolio(self, date:str):
    """ Return [total_buy, prices, qtys]

    """
    capital = self.capital
    etfs,ratios = self.portpolio.get_etf()
    budgets = np.multiply(ratios,0.01*capital)

    for i,etf in enumerate(etfs):
      self.max_ratios[etf.code] = ratios[i]
      self.curr_ratios[etf.code]= ratios[i]

    if PRINT_BUY_PORTPOLIO==True:
      print('\nBuy - %s'%self.portpolio.name)
      print("%20s | %30s %20s | %10s %10s %10s %10s %10s"%('index','name','code','budget','ratio(%)', 'price', 'qty', 'buy'))
      print('-'*140)
      total_buy = 0
      for i,etf in enumerate(etfs):
        update_hold_qtys, update_avg_price, update_cash = self.buy(etf=etf, date=date, percent=100)
        self.hold_qtys[etf.code] = update_hold_qtys
        self.avg_price[etf.code] = update_avg_price
        self.cash = update_cash
        value = update_hold_qtys*update_avg_price
        total_buy += value
        print("%20s | %s %20s | %10d %10.2f %10.2f %10d %10d"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code,budgets[i],ratios[i],update_avg_price,update_hold_qtys,value) )
      print('-'*140)
      
      print('Total: %10d\n\n'%total_buy)
    else:
      total_buy = 0
      for i,etf in enumerate(etfs):
        update_hold_qtys, update_avg_price, update_cash = self.buy(etf=etf, date=date, percent=100)
        self.hold_qtys[etf.code] = update_hold_qtys
        self.avg_price[etf.code] = update_avg_price
        self.cash = update_cash
        total_buy += update_hold_qtys*update_avg_price


      return total_buy



  def sell_portpolio(self, date:str):#,buy_prices:np.ndarray, buy_qtys:np.ndarray):
    """ Return
      
    """
    etfs,ratios = self.portpolio.get_etf()
    #prices  = [etf.get_price(date=date) for etf in etfs]

    if PRINT_SELL_PORTPOLIO==True:
      print('\nSell - %s'%self.portpolio.name)
      print("%20s | %30s %20s | %10s %10s %15s %15s %10s %10s %15s"%('index','name','code','buy','ratio(%)', 'buy price','sell price', 'qty', 'sell', 'earn ratio(%)'))
      print('-'*170)
      for i,etf in enumerate(etfs):
        last_qty = self.hold_qtys[etf.code]
        last_avg_price = self.avg_price[etf.code]
        curr_price = etf.get_price(date=date)
        update_hold_qtys, update_earn, update_cash = self.sell(etf=etf, date=date, percent=100)
        self.hold_qtys[etf.code] = update_hold_qtys
        self.earn[etf.code] = update_earn
        self.cash = update_cash
        earn_ratio = (curr_price-last_avg_price)/last_avg_price * 100
        print("%20s | %s %20s | %10d %10.2f %15.2f %15.2f %10d %10d %15.2f"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code, last_qty*last_avg_price ,ratios[i], last_avg_price ,curr_price, last_qty, curr_price*last_qty, earn_ratio))
      print('-'*170)
      total_sell = self.cash
      print('Total: %10d\n\n'%total_sell)
    else:
      for i,etf in enumerate(etfs):
        update_hold_qtys, update_earn, update_cash = self.sell(etf=etf, date=date, percent=100)
        self.hold_qtys[etf.code] = update_hold_qtys
        self.earn[etf.code] = update_earn
        self.cash = update_cash
      total_sell = self.cash
    return total_sell
  
  def Run(self, start_date:str, end_date:str, what:str):
    """ Algorithm
      시작시간부터 하루하루 넘어가면서 MDD계산
    """
    dt_end_date = datetime.datetime.strptime(end_date,"%Y-%m-%d")

    total_buy = self.buy_portpolio(date=start_date)
    etfs,ratios = self.portpolio.get_etf()
    #self.print_info()

    max_draw_down = 0
    cutoff_flag = not DO_CUT_OFF
    debug_mmd = np.array([])
    debug_capital = np.array([])

    pivot_date = datetime.datetime.strptime(start_date,"%Y-%m-%d")
    while(pivot_date < dt_end_date):
      """
      =========================================================================
                              Strategy Start 
      ========================================================================= 
      """
      if what=='AW4/11':
        if ((pivot_date.month==4) & (pivot_date.day==1)) | ((pivot_date.month==11) & (pivot_date.day==1)):
          last_capital = self.capital

          # Reblancing
          total_sell = self.sell_portpolio(date=pivot_date.strftime('%Y-%m-%d'))
          earn_ratio = round((total_sell-last_capital)/last_capital*100,2)
          self.capital = total_sell
          _ = self.buy_portpolio(date=pivot_date.strftime('%Y-%m-%d'))

          # MDD
          earn = 0
          for k,v in self.earn.items():
            earn += v
          draw_down = (earn)/last_capital*100

          max_draw_down = draw_down if draw_down<max_draw_down else max_draw_down

          if PRINT_TRADE_LOG:
            print(pivot_date,'%10d --> %10d  %4.2f[%%]  MDD: %.2f[%%]'%(last_capital,total_sell, earn_ratio,max_draw_down))

          """
            Next date
          """
          debug_mmd = np.append(debug_mmd,round(max_draw_down,2))
          debug_capital = np.append(debug_capital,round(last_capital+temp_earn,2))
          max_draw_down= 0
          cutoff_flag = False
          pivot_date = ETFUtils.get_next_date(pivot_date)
          continue

        else:
          """
            MDD
          """
          temp_earn = 0
          for i,etf in enumerate(etfs):
            update_hold_qtys, update_earn, update_cash = self.sell(etf=etf, date=pivot_date.strftime('%Y-%m-%d'), percent=100)
            temp_earn += update_earn

          last_capital = self.capital
          draw_down = (temp_earn)/last_capital*100

          max_draw_down = draw_down if draw_down<max_draw_down else max_draw_down


      elif what=='AWHold':
        """
          MDD
        """
        temp_earn = 0
        for i,etf in enumerate(etfs):
          update_hold_qtys, update_earn, update_cash = self.sell(etf=etf, date=pivot_date.strftime('%Y-%m-%d'), percent=100)
          temp_earn += update_earn

        last_capital = self.capital
        draw_down = (temp_earn)/last_capital*100

        max_draw_down = draw_down if draw_down<max_draw_down else max_draw_down

      elif what == 'AbsMomentum':
        pass
      elif what == 'DualMomentum':
        pass
      else:
        """
        =========================================================================
                                Strategy end 
        ========================================================================= 
        """

      """
        Cut-off
      """
      if DO_CUT_OFF:
        if (max_draw_down < -10) & (cutoff_flag==False):
          if PRINT_TRADE_LOG:
            print(pivot_date,'Cut-off!!   mmd: %2.2f%%'%max_draw_down)
          total_sell = self.sell_portpolio(date=pivot_date.strftime('%Y-%m-%d'))
          self.capital = total_sell
          cutoff_flag = True

      """
        Next date
      """
      debug_mmd = np.append(debug_mmd,round(max_draw_down,2))
      debug_capital = np.append(debug_capital,round(last_capital+temp_earn,2))
      pivot_date = ETFUtils.get_next_date(pivot_date)


    """
      Result
    """
    if 1:
      """
        Sell All at the end date
      """
      last_capital = self.capital
      total_sell = self.sell_portpolio(date=end_date)
      earn_ratio = round((total_sell-last_capital)/last_capital*100,2)
      print(pivot_date,'%10d --> %10d  %4.2f[%%]  MDD: %.2f[%%]'%(last_capital,total_sell, earn_ratio,max_draw_down))
      self.print_info()

    if 1:
      """
        Report
      """
      import matplotlib.pyplot as plt
      fig = plt.figure(figsize=(10,10))
      ax1 = fig.add_subplot(2,1,1)
      ax2 = fig.add_subplot(2,1,2)
      ax1.plot(range(len(debug_mmd)),debug_mmd , label = 'mmd(%)')
      ax2.plot(range(len(debug_capital)),debug_capital, label = 'capital')    
      ax2.legend()
      ax1.legend()

      if self.do_save:
        plt.savefig(self.report_name)
      plt.show()

    return total_sell



if __name__ == '__main__':

  start_capital =  100_000
  capital = start_capital

  #start_date, end_date, _ = ['2018-02-05', '2019-01-03', 'kospi양적긴축폭락장']
  if 0:
    DO_CUT_OFF = 1
    portpolio_name = 'GTAA-NON'
    start_date, end_date,_ = ['2006-11-02', '2022-01-02','gtaa-non']
    portpolio = Portpolio(portpolio_name)
    report_name = portpolio_name + '_cutoff10'
    sim1 = Simulation(portpolio=portpolio, capital=capital,report_name=report_name).Run(start_date= start_date, end_date= end_date, what='AW4/11')
  
  if 1:
  
    PRINT_TRADE_LOG = True
    DO_CUT_OFF = 1
    portpolio_name = 'DANTE'
    start_date, end_date,_ = ['2013-11-02', '2022-01-02','단테 올웨더']
    #start_date, end_date,_ = ['2014-11-02', '2019-11-02','단테 올웨더']

    portpolio = Portpolio(portpolio_name)
    #report_name = portpolio_name + '_cutoff10'
    report_name = None
    sim2 = Simulation(portpolio=portpolio, capital=capital,report_name=report_name).Run(start_date= start_date, end_date= end_date, what='AW4/11')
    #sim2 = Simulation(portpolio=portpolio, capital=capital,report_name=report_name).Run(start_date= start_date, end_date= end_date, what='AWHold')

  if 0:
    DO_CUT_OFF = 1
    portpolio_name = 'DANTE'
    start_date, end_date,_ = ['2013-11-02', '2022-01-02','단테 올웨더']
    portpolio = Portpolio(portpolio_name)


    import datetime
    import random

    def random_date(start, end):
      start_date = datetime.datetime.strptime(start,"%Y-%m-%d")
      end_date = datetime.datetime.strptime(end,"%Y-%m-%d")
      day_range = int((end_date - start_date).total_seconds()/3600/24)

      ret = start_date + datetime.timedelta(days=random.randint(0, day_range))
      ret = ret.strftime('%Y-%m-%d')
      return ret

    for i in range(10):
      start_date = random_date('2014-01-01','2018-12-31')
      print('\n\n',start_date)
      sim2 = Simulation(portpolio=portpolio, capital=capital,report_name='').Run(start_date= start_date, end_date= end_date, what='AW4/11')
