from audioop import avg
from functools import total_ordering
from matplotlib.pyplot import draw, figure
from dateutil import relativedelta
import yaml
import os, datetime, requests
import numpy as np
import ETFUtils
from ETF import ETF
from Portpolio import Portpolio
import pandas as pd
import Strategy


class SimResult(object):
  """
    Simulation Result
  """
  sim_name = 'sim1'
  trade_log = None 
  trade_log_columns=('Date', 'MDD', 'Capital','Earn','Yield', 'Trade', 'SMG55')

  def average_result(self, sim_results:np.ndarray):
    self.sim_name = "Avg"
    avg_date    = sim_results[0].trade_log['Date']
    avg_mdd     = np.array([s.trade_log['MDD'] for s in sim_results]).sum(axis=0)/len(sim_results)
    avg_capital = np.array([s.trade_log['Capital'] for s in sim_results]).sum(axis=0)/len(sim_results)
    avg_earn    = np.array([s.trade_log['Earn'] for s in sim_results]).sum(axis=0)/len(sim_results)
    avg_yield   = np.array([s.trade_log['Yield'] for s in sim_results]).sum(axis=0)/len(sim_results)
    avg_trade   = np.repeat(False,len(avg_date))
    avg = pd.DataFrame([],columns=self.trade_log_columns)
    avg = avg.assign(Date=avg_date, MDD=avg_mdd, Capital=avg_capital,Earn=avg_earn, Yield=avg_yield, Trade=avg_trade)
    self.trade_log = avg
    
  def get_cagr(self):
    start_date   = self.trade_log['Date'].iloc[0]
    end_date     = self.trade_log['Date'].iloc[-1]
    init_capital = self.get_capital(start_date)
    last_capital = self.get_capital(end_date)
    d1 = start_date #datetime.datetime.strptime(start_date,"%Y-%m-%d")
    d2 = end_date #datetime.datetime.strptime(end_date,"%Y-%m-%d")
    num_year = (d2.year - d1.year)
    if num_year > 0:
      cagr = (last_capital/init_capital)**(1/num_year)
      cagr = round((cagr-1)*100,2)
    else:
      cagr=0.00
    return cagr

  def get_cmgr(self):
    start_date   = self.trade_log['Date'].iloc[0]
    end_date     = self.trade_log['Date'].iloc[-1]
    init_capital = self.get_capital(start_date)
    last_capital = self.get_capital(end_date)
    d1 = start_date #datetime.datetime.strptime(start_date,"%Y-%m-%d")
    d2 = end_date #datetime.datetime.strptime(end_date,"%Y-%m-%d")
    num_month = (d2.year - d1.year) * 12 + (d2.month - d1.month)
    if num_month > 0:
      cmgr = (last_capital/init_capital)**(1/num_month)
      cmgr = round((cmgr-1)*100,2)
    else:
      cmgr=0.00
    return cmgr

  @staticmethod
  def get_mdd_per_month(trade_log):
    df = trade_log

    end_date     = df['Date'].iloc[-1]
    start_date   = end_date - relativedelta.relativedelta(month=1)


    #start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d")
    #end_date   = datetime.datetime.strptime(end_date,"%Y-%m-%d")
    
    d1 = start_date
    d2 = end_date
    window = 30

    #print(type(df['Date'].iloc[0]), type(d1.strftime('%Y-%m-%d'))) 
    #df_window = df.loc[(df['Date']>=d1.strftime('%Y-%m-%d')) & (df['Date']<=d2.strftime('%Y-%m-%d')) , 'Capital']
    df_window = df.loc[(df['Date']>=d1) & (df['Date']<=d2) , 'Capital']
    max_price = df_window.rolling(window=window, min_periods=1).max()
    min_price = df_window.rolling(window=window, min_periods=1).min()

    max_dd = ((min_price/max_price) - 1.0 )*100.0
    #print(max_price, min_price,max_dd)
    return max_dd

  def get_last_date(self):
    return self.trade_log['Date'].iloc[-1]

  def get_last_capital(self):
    return self.trade_log['Capital'].iloc[-1]

  def get_capital(self,date:str):
    if type(date) == str:
      date = datetime.datetime.strptime(date,"%Y-%m-%d")
    capital = self.trade_log.loc[self.trade_log['Date'] == date,'Capital']
    ret= float(capital)
    return ret


class SimEnvironment(SimResult):
  """
    Simulation Environment
  """
  if 1: #Sim Data
    start_capital_krw =  10_000_000 
    start_date, end_date, _ = ['2018-02-05', '2019-01-03', 'kospi양적긴축폭락장']
    portpolio_index = 0
    portpolio_list  = ['DANTE']
    reserve_per_period = 0
    reblancing_rule = 'AW4/11' # 'B&H'
    market_open_date = None

  if 1: # Report
    report_name = None

  if 1: #Sim Options
    FIXED_EXCHANGE_RATE = True
    PRINT_TRADE_LOG = False
    PRINT_BUY_PORTPOLIO  = False
    PRINT_SELL_PORTPOLIO = False
    LIMIT_RATIO = True
    RESULT_PLOT = False
    DO_CUT_OFF = False
    FIGSIZE = (10,5)



class Simulation(SimEnvironment):
  """ Return Simulation
    Simulation Root node of Portpolio (ETF chain)
  """
  def __init__(self, portpolio:Portpolio=None, env:SimEnvironment=None):
    self.env = env
    if portpolio:
      self.portpolio = portpolio
    else:
      self.portpolio = Portpolio(env.portpolio_list[env.portpolio_index])

    self.do_save = False
    if env.report_name:
      self.report_path = os.path.join('sim-result',env.report_name+'.png')
      self.do_save = True

    """
    ==========================
          SIM Variables 
    ==========================
    """
    self.init_budgets = env.start_capital_krw
    self.budgets = env.start_capital_krw # constant init value
    self.capital = env.start_capital_krw # reblanced value
    self.cash    = env.start_capital_krw

    self.max_ratios = dict()
    self.curr_ratios = dict()
    self.max_qty = dict()
    self.avg_price = dict()
    self.hold_qtys = dict()
    self.earn= dict()

    for etf in self.portpolio.get_etf()[0]:
      self.avg_price[etf.code]  =0 
      self.hold_qtys[etf.code]  =0
      self.earn[etf.code] =0



  def buy(self, etf:ETF, date:datetime, percent:float)->list:
    """ Return [last_qty, avg_price, self.cash]

    """
    if type(date) == datetime.datetime:
      date = date.strftime('%Y-%m-%d')

    last_qty = self.hold_qtys[etf.code]
    curr_price, valid = etf.get_price(date=date)
    avg_price = self.avg_price[etf.code]
    if avg_price == 0:
      avg_price = curr_price

    if etf.src == 'YAHOO':
      if self.env.FIXED_EXCHANGE_RATE:
        usd_krw = 1150
      else:
        usd_krw = self.portpolio.usd_krw.loc[self.portpolio.usd_krw['Date']==date,'Close'].values[0]
    else:
      usd_krw = 1.0

    curr_price_krw = curr_price*usd_krw
    buy_percent = (self.max_ratios[etf.code]*(percent/100))
    buy_qty = int(buy_percent*self.capital/100 / curr_price_krw)

    if self.env.LIMIT_RATIO:
      over = (self.avg_price[etf.code]*self.hold_qtys[etf.code] + buy_qty*curr_price_krw)/(self.capital)*100
    else:
      over = 0
    if (curr_price_krw*buy_qty <= self.cash):
      if (over <= self.max_ratios[etf.code]):
        update_hold_qtys = last_qty + buy_qty
        update_avg_price = (avg_price*last_qty+curr_price_krw*buy_qty)/update_hold_qtys if update_hold_qtys else 0
        update_cash = self.cash - curr_price_krw*buy_qty
        ret = [update_hold_qtys, update_avg_price, update_cash,valid]
      else:
        ret= [last_qty, avg_price, self.cash, valid]
    else:
      ret = [last_qty, avg_price, self.cash, valid]
    return ret


  def sell(self, etf:ETF, date:datetime, percent:float)->list:
    """ Return [update_hold_qtys, update_earn, update_cash,]

    """
    if type(date) == datetime.datetime:
      date = date.strftime('%Y-%m-%d')

    last_qty  = int(self.hold_qtys[etf.code])
    last_earn = self.earn[etf.code]

    curr_price, valid = etf.get_price(date=date)
    sell_qty = int(self.hold_qtys[etf.code]*(percent/100))

    if etf.src == 'YAHOO':
      if self.env.FIXED_EXCHANGE_RATE:
        usd_krw = 1150
      else:
        usd_krw = self.portpolio.usd_krw.loc[self.portpolio.usd_krw['Date']==date,'Close'].values[0]
    else:
      usd_krw = 1.0

    curr_price_krw = curr_price*usd_krw

    if last_qty >= sell_qty:
      update_hold_qtys = last_qty - sell_qty
      update_earn = (curr_price_krw - self.avg_price[etf.code])*sell_qty
      update_cash = self.cash + curr_price_krw*sell_qty
      ret = [update_hold_qtys, update_earn, update_cash, valid]
    else:
      ret = [last_qty, last_earn, self.cash, valid]
    return ret



  def print_info(self):
    """ Return

    """
    etfs,_ = self.portpolio.get_etf()
    print('='*165)
    print('Portpoilo Info - %s'%self.portpolio.name)
    print("%20s | %30s %20s | %10s %10s %10s %10s %10s %15s %15s"%('index','name','code', 'max(%)','ratio(%)', 'price(krw)', 'qty', 'buy', 'quater-earn','quater-yield'))
    print('-'*165)
    total_buy = 0
    for i,etf in enumerate(etfs):
      qty   = self.hold_qtys[etf.code]
      max_ratio = self.max_ratios[etf.code]
      price  = round(self.avg_price[etf.code],2)
      value = qty*price
      ratios = self.curr_ratios[etf.code]
      earn = self.earn[etf.code]
      total_buy += value
      earn_yield = round(earn/(self.capital*max_ratio)*100*100,2)

      print("%20s | %s %20s | %10.2f %10.2f %10.2f %10d %10d %15d %15.2f"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code,max_ratio,ratios, price, qty, value,earn,earn_yield) )
    print('-'*165)
    print('Total:')
    print('\tbudget: %10d\n\t\tbuy: %10d\n\t\tcash: %10d'%(self.budgets,total_buy,self.cash))
    print('\tcurr/budget=%12d/%12d [%4.2f%%]'%(total_buy+self.cash, self.budgets,(total_buy+self.cash)/self.budgets*100))
    print('='*165)


  def buy_portpolio(self, date:datetime):
    """ Return [total_buy, prices, qtys]

    """
    capital = self.capital
    etfs,ratios = self.portpolio.get_etf()
    budgets = np.multiply(ratios,0.01*capital)

    for i,etf in enumerate(etfs):
      self.max_ratios[etf.code] = ratios[i]
      self.curr_ratios[etf.code]= ratios[i]

    if self.env.PRINT_BUY_PORTPOLIO:
      print('\nBuy - %s'%self.portpolio.name)
      print("%20s | %30s %20s | %10s %10s %10s %10s %10s"%('index','name','code','budget','ratio(%)', 'price', 'qty', 'buy'))
      print('-'*140)
      total_buy = 0
      for i,etf in enumerate(etfs):
        update_hold_qtys, update_avg_price, update_cash,valid = self.buy(etf=etf, date=date, percent=100)
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
        update_hold_qtys, update_avg_price, update_cash, valid = self.buy(etf=etf, date=date, percent=100)
        self.hold_qtys[etf.code] = update_hold_qtys
        self.avg_price[etf.code] = update_avg_price
        self.cash = update_cash
        total_buy += update_hold_qtys*update_avg_price

      return total_buy,valid



  def sell_portpolio(self, date:datetime):#,buy_prices:np.ndarray, buy_qtys:np.ndarray):
    """ Return
      
    """
    etfs,ratios = self.portpolio.get_etf()
    #prices  = [etf.get_price(date=date) for etf in etfs]

    if self.env.PRINT_SELL_PORTPOLIO:
      print('\nSell - %s'%self.portpolio.name)
      print("%20s | %30s %20s | %10s %10s %15s %15s %10s %10s %15s"%('index','name','code','buy','ratio(%)', 'buy price','sell price', 'qty', 'sell', 'earn ratio(%)'))
      print('-'*170)
      for i,etf in enumerate(etfs):
        last_qty = self.hold_qtys[etf.code]
        last_avg_price = self.avg_price[etf.code]
        curr_price, _ = etf.get_price(date=date)
        update_hold_qtys, update_earn, update_cash,valid = self.sell(etf=etf, date=date, percent=100)
        self.hold_qtys[etf.code] = update_hold_qtys
        self.earn[etf.code] = update_earn
        self.cash = update_cash
        earn_yield = (curr_price-last_avg_price)/last_avg_price * 100
        print("%20s | %s %20s | %10d %10.2f %15.2f %15.2f %10d %10d %15.2f"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code, last_qty*last_avg_price ,ratios[i], last_avg_price ,curr_price, last_qty, curr_price*last_qty, earn_yield))
      print('-'*170)
      total_sell = self.cash
      print('Total: %10d\n\n'%total_sell)
    else:
      for i,etf in enumerate(etfs):
        update_hold_qtys, update_earn, update_cash,valid = self.sell(etf=etf, date=date, percent=100)
        self.hold_qtys[etf.code] = update_hold_qtys
        self.earn[etf.code] = update_earn
        self.cash = update_cash
        total_sell = self.cash
    return total_sell ,valid


  def Run(self):
    """ Algorithm
      시작시간부터 하루하루 넘어가면서 MDD계산
    """
    start_date      = self.env.start_date
    end_date        = self.env.end_date
    reblancing_rule = self.env.reblancing_rule
    dt_start_date   = datetime.datetime.strptime(start_date,"%Y-%m-%d")
    dt_end_date     = datetime.datetime.strptime(end_date,"%Y-%m-%d")
    trade_log = pd.DataFrame([],columns=self.trade_log_columns)


    """
    =========================================================================
                          Trading Conditions 
    ========================================================================= 
    """
    cutoff_flag = not self.env.DO_CUT_OFF
    max_draw_down = 0
    count =0
    additional_paid_in = self.env.reserve_per_period

    pivot_date = dt_start_date
    last_reblance_day = pivot_date
    today_capital = 0

    """
    =========================================================================
                          Trading Start 
    ========================================================================= 
    """
    if reblancing_rule != 'Nothing':
      total_buy,valid = self.buy_portpolio(date=dt_start_date)
      etfs,ratios = self.portpolio.get_etf()
      if self.env.PRINT_TRADE_LOG:
        self.print_info()

    last_capital = self.capital
    while(pivot_date <= dt_end_date):
      """
      =========================================================================
                              Strategy Start 
      ========================================================================= 
      """
      if reblancing_rule=='AW4/11':
        AW_4_  = (pivot_date.month==4)  and  (pivot_date.day == 28)
        AW_11_ = (pivot_date.month==11) and  (pivot_date.day == 28)
        #pivot_date = pivot_date.strftime('%Y-%m-%d')
        if (AW_4_ or AW_11_):
          last_capital = self.capital

          # Reblancing
          ## 1. Sell All
          total_sell,valid = self.sell_portpolio(date=pivot_date)

          ## 2. Additional Paid-In
          count += 1
          self.capital = total_sell + additional_paid_in

          ## 3. Buy All
          _,valid = self.buy_portpolio(date=pivot_date)


          # Report
          earn = 0
          for k,v in self.earn.items():
            earn += v
          earn_yield = round((total_sell-last_capital)/last_capital*100,2)

          """
            Next date
          """
          reblancing_results = pd.DataFrame(
            #[[pivot_date,round(max_draw_down,2),round(self.capital,2), earn, earn_yield, valid]],
            [[pivot_date,0,round(self.capital,2), earn, earn_yield, valid,0]],
            columns=self.trade_log_columns)
          trade_log = pd.concat([trade_log,reblancing_results])
          trade_log['SMG55'] = trade_log['Capital'].rolling(window=55).mean()
          cutoff_flag = False
    
          max_dd = SimResult.get_mdd_per_month(trade_log)
          trade_log.loc[trade_log['Date']== pivot_date.strftime('%Y-%m-%d'), ['MDD']] = max_dd.iloc[-1]
          if self.env.PRINT_TRADE_LOG:
            print(pivot_date,'%10d --> %10d  %4.2f[%%]  MDD: %.2f[%%]'%(last_capital,total_sell, earn_yield,max_dd.iloc[-1]))

          pivot_date = ETFUtils.get_next_date(pivot_date)
          continue

      elif reblancing_rule=='B&H':
        pass

      else:
        pass

      """
      =========================================================================
                              Strategy end 
      ========================================================================= 
      """
      """
        Daily report
      """
      if 1: # cma 이자
        cma=(self.cash*(0.012)/365)
        #print('이자: %d -> %d '%(self.cash,cma))
        self.cash += cma
        self.capital += cma

      if reblancing_rule != 'Nothing':
        temp_earn = 0
        for i,etf in enumerate(etfs):
          update_hold_qtys, update_earn, update_cash,valid = self.sell(etf=etf, date=pivot_date.strftime('%Y-%m-%d'), percent=100)
          temp_earn += update_earn
        last_capital = self.capital
        today_capital = self.capital + temp_earn
      else:
        temp_earn = 0
        today_capital = self.capital 
        valid = False

      reblancing_results = pd.DataFrame(
        #[[pivot_date,round(max_draw_down,2),round(today_capital,2), temp_earn, round(temp_earn/self.capital,2),valid]],
        [[pivot_date,0,round(today_capital,2), 0, (temp_earn/last_capital)*100,valid,0]],
        columns=self.trade_log_columns)
       
      trade_log = pd.concat([trade_log,reblancing_results])
      trade_log['SMG55'] = trade_log['Capital'].rolling(window=13).mean()
      max_dd = SimResult.get_mdd_per_month(trade_log)
      trade_log.loc[trade_log['Date']== pivot_date.strftime('%Y-%m-%d'), ['MDD']] = max_dd.iloc[-1]

      """
        Cut off
      """ 
      if self.env.DO_CUT_OFF:
        #loss_cut = (today_capital - trade_log['SMG55'].iloc[-1])/today_capital * 100 #(today_capital/last_capital -1)*100
        loss_cut = (today_capital/last_capital -1)*100
        if ( loss_cut < -10) & (cutoff_flag==False):
          print(pivot_date,'Cut-off!!   loss_cut: %2.2f%%  %.2f %.2f'%(loss_cut, today_capital,last_capital))
          total_sell,valid = self.sell_portpolio(date=pivot_date)
          self.capital = total_sell
          cutoff_flag = True
      else:
        loss_cut = np.NaN

      """
        Next date
      """
      pivot_date = ETFUtils.get_next_date(pivot_date)


    """
    =========================================================================
                            Trading end 
    ========================================================================= 
    """

    """
      Sell All at the end date
    """
    self.budgets += count*additional_paid_in  
    last_capital = self.capital
    total_sell,valid = self.sell_portpolio(date=dt_end_date)
    #self.earn = (total_sell - )
    earn_yield = round((total_sell-self.budgets)/self.budgets*100,2)

    if self.env.PRINT_TRADE_LOG:
      loss_cut = (total_sell/self.budgets -1 )*100
      print(pivot_date,'%10d --> %10d  %4.2f[%%]  MDD: %.2f[%%] Loss:%.2f[%%]'%(last_capital,total_sell, earn_yield,max_draw_down,loss_cut))
      self.print_info()

    sim_result = self.env
    for i in trade_log.index:
      if trade_log.iloc[i,-1]==False:
        if i != 0:
          trade_log.iloc[i,1:-1] = trade_log.iloc[i-1,1:-1]
    sim_result.trade_log = trade_log.reset_index(drop=True)

    return sim_result


"""
=========================================================================
                            MAIN
========================================================================= 
"""
if __name__ == '__main__':
  env = SimEnvironment()
  env.start_capital_krw =  12_000_000 
  env.reserve_per_period = 1000_000
  env.PRINT_TRADE_LOG = True
  env.DO_CUT_OFF = True
  env.portpolio_index = 0
  env.portpolio_list = ['DANTE']
  env.start_date, env.end_date,_ = ['2018-01-12', '2022-02-10','']
  env.report_name = None
  env.reblancing_rule='AW4/11'
  #env.reblancing_rule='B&H'

  sim1 = Simulation(env=env).Run()
  print(sim1.trade_log[0:20])
  print(sim1.get_capital(date=env.end_date))
  print(sim1.get_cmgr())
  print(sim1.get_cagr())

