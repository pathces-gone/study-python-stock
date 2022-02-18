from audioop import avg
from matplotlib.pyplot import draw, figure
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
  trade_log = None

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



class Simulation(object):
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
    print('='*160)
    print('Portpoilo Info - %s'%self.portpolio.name)
    print("%20s | %30s %20s | %10s %10s %10s %10s %10s %10s %12s"%('index','name','code', 'max(%)','ratio(%)', 'price(krw)', 'qty', 'buy', 'earn','earn_yield'))
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
      earn_yield = round(earn/(self.capital*max_ratio)*100*100,2)

      print("%20s | %s %20s | %10.2f %10.2f %10.2f %10d %10d %10d %12.2f"%(etf.index, ETFUtils.preformat_cjk(etf.name,30),etf.code,max_ratio,ratios, price, qty, value,earn,earn_yield) )
    print('-'*160)
    print('Total:')
    print('\tbudget: %10d\n\t\tbuy: %10d\n\t\tcash: %10d'%(self.budgets,total_buy,self.cash))
    print('\tcurr/budget=%12d/%12d [%4.2f%%]'%(total_buy+self.cash, self.budgets,(total_buy+self.cash)/self.budgets*100))
    print('='*160)


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
    trade_log = pd.DataFrame([],columns=['Date', 'MDD', 'Capital','Earn','Yield','Trade'])


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

    max_capital_during_period = self.capital
    min_capital_during_period = self.capital
    temp_earn = 0
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


          if self.env.PRINT_TRADE_LOG:
            print(pivot_date,'%10d --> %10d  %4.2f[%%]  MDD: %.2f[%%]'%(last_capital,total_sell, earn_yield,max_draw_down))

          """
            Next date
          """
          reblancing_results = pd.DataFrame(
            [[pivot_date,round(max_draw_down,2),round(self.capital,2), earn, earn_yield, valid]],
            columns=['Date', 'MDD', 'Capital','Earn','Yield', 'Trade'])
          trade_log = pd.concat([trade_log,reblancing_results])
          cutoff_flag = False
 
          # MDD Reset
          min_capital_during_period = self.capital
          max_capital_during_period = self.capital
          draw_down     = 0
          max_draw_down = 0

          pivot_date = ETFUtils.get_next_date(pivot_date)
    
        else:
          """
            MDD
          """
          temp_earn = 0
          for i,etf in enumerate(etfs):
            update_hold_qtys, update_earn, update_cash,valid = self.sell(etf=etf, date=pivot_date.strftime('%Y-%m-%d'), percent=100)
            temp_earn += update_earn

          last_capital = self.capital
          today_capital = self.capital + temp_earn
          min_capital_during_period = min_capital_during_period if min_capital_during_period <= today_capital else today_capital
          max_capital_during_period = max_capital_during_period if max_capital_during_period >= today_capital else today_capital
          draw_down = (min_capital_during_period-max_capital_during_period)/max_capital_during_period*100

          max_draw_down = draw_down if draw_down<max_draw_down else max_draw_down
      elif reblancing_rule=='B&H':
        """
          MDD
        """
        temp_earn = 0
        for i,etf in enumerate(etfs):
          update_hold_qtys, update_earn, update_cash,valid = self.sell(etf=etf, date=pivot_date.strftime('%Y-%m-%d'), percent=100)
          temp_earn += update_earn

        last_capital = self.capital
        today_capital = self.capital + temp_earn
        min_capital_during_period = min_capital_during_period if min_capital_during_period <= today_capital else today_capital
        max_capital_during_period = max_capital_during_period if max_capital_during_period >= today_capital else today_capital
        draw_down = (min_capital_during_period-max_capital_during_period)/max_capital_during_period*100

        max_draw_down = draw_down if draw_down<max_draw_down else max_draw_down
      else:
        max_draw_down = 0
        today_capital = self.capital
        temp_earn = 0
        valid = 0
        

      """
      =========================================================================
                              Strategy end 
      ========================================================================= 
      """
      if self.env.DO_CUT_OFF:
        if (max_draw_down < -10) & (cutoff_flag==False):
          if self.env.PRINT_TRADE_LOG:
            print(pivot_date,'Cut-off!!   mdd: %2.2f%%'%max_draw_down)
          total_sell,valid = self.sell_portpolio(date=pivot_date)
          self.capital = total_sell
          cutoff_flag = True

      """
        Next date
      """
      if 1: # cma 이자
        cma=(self.cash*(0.012)/365)
        #print('이자: %d -> %d '%(self.cash,cma))
        self.cash += cma
        self.capital += cma
  
      reblancing_results = pd.DataFrame(
        [[pivot_date,round(max_draw_down,2),round(today_capital,2), temp_earn, round(temp_earn/self.capital,2),valid]],
        columns=['Date', 'MDD', 'Capital','Earn','Yield', 'Trade'])
      trade_log = pd.concat([trade_log,reblancing_results])

      pivot_date = ETFUtils.get_next_date(pivot_date)


    """
    =========================================================================
                            Trading end 
    ========================================================================= 
    """

    """
      Result
    """
    if 1:
      """
        Sell All at the end date
      """
      last_capital = self.capital
      total_sell,valid = self.sell_portpolio(date=dt_end_date)
      earn_yield = round((total_sell-last_capital)/last_capital*100,2)

      self.budgets += count*additional_paid_in
      if self.env.PRINT_TRADE_LOG:
        print(pivot_date,'%10d --> %10d  %4.2f[%%]  MDD: %.2f[%%]'%(last_capital,total_sell, earn_yield,max_draw_down))
        self.print_info()

    if self.env.RESULT_PLOT:
      """
        Report
      """
      import matplotlib.pyplot as plt
      df_usd_krw = self.portpolio.usd_krw.loc[ 
        (self.portpolio.usd_krw['Date'] >= start_date) & (self.portpolio.usd_krw['Date'] <= end_date),
        :]
      fig = plt.figure(figsize=(15,10))
      ax1 = fig.add_subplot(3,1,1)
      ax2 = fig.add_subplot(3,1,2)
      ax3 = fig.add_subplot(3,1,3)

      x= trade_log['Date']

      ax1.plot(x, trade_log['MDD'], label = 'mdd(%)')
      ax2.plot(x, trade_log['Capital'], label = 'capital')

      s1 = datetime.datetime.strftime(x.iloc[0],"%Y-%m-%d")
      s2 = datetime.datetime.strftime(x.iloc[-1],"%Y-%m-%d")
      cat_x = df_usd_krw.loc[(df_usd_krw['Date'] >= s1) & (df_usd_krw['Date'] <= s2),'Date']
      cat_y = df_usd_krw.loc[(df_usd_krw['Date'] >= s1) & (df_usd_krw['Date'] <= s2),'Close']

      ax3.plot(cat_x,cat_y, label='usd-krw')

      plt.xticks(np.arange(0, len(df_usd_krw['Date'])+1, 30), rotation=45)

      ax1.legend()
      ax2.legend()
      ax3.legend()
      plt.grid()

      if self.do_save:
        plt.savefig(self.report_path)
      plt.show()

    sim_result = self.env

    for i in trade_log.index:
      if trade_log.iloc[i,-1]==False:
        if i != 0:
          trade_log.iloc[i,1:-1] = trade_log.iloc[i-1,1:-1]
    sim_result.trade_log = trade_log.reset_index(drop=True)
    return sim_result



class SimulationReview(Simulation):
  def __init__(self, sim1:list, sim2:list):
    sim1_name, sim1_mdd, sim1_capital, sim1_date = sim1
    sim2_name, sim2_mdd, sim2_capital, sim2_date = sim2
    assert sim1_date[0] == sim2_date[0],''
    assert sim2_date[-1] == sim2_date[-1],''

    raw_df = pd.DataFrame()

    for i in range(len(sim2_date)+len(sim1_date)):
      if (len(sim1_date)<=i) or (len(sim2_date)<=i):
        break
      if sim1_date[i] > sim2_date[i]:
        sim1_date  = np.insert(sim1_date, i, sim2_date[i])
        sim1_capital = np.insert(sim1_capital, i, sim1_capital[i-1])
      elif sim1_date[i] < sim2_date[i]:
        sim2_date  = np.insert(sim2_date, i, sim1_date[i])
        sim2_capital = np.insert(sim2_capital, i, sim2_capital[i-1])
      else:
        pass

    raw_df['Date'] = sim2_date
    raw_df['sim1'] = sim1_capital
    raw_df['sim2'] = sim2_capital

    self.raw_df = raw_df

    import matplotlib.pyplot as plt
    plt.figure(figsize=FIGSIZE)
    plt.plot(sim1_capital,label=sim1_name)
    plt.plot(sim2_capital,label=sim2_name)
    plt.legend()
    #plt.show()
    
  def get_correlation(self, start_date:str=None, end_date:str=None):
    """ Return
      Correation Dataframe
    """
    raw_df = self.raw_df

    st = raw_df['Date'].iloc[0] if start_date == None else start_date
    ed = raw_df['Date'].iloc[-1]  if end_date == None else end_date

    ranging_df = raw_df[(st<=raw_df['Date']) & (raw_df['Date']<=ed)].iloc[::-1].reset_index(drop=True)
    corr_df = ranging_df.corr(method='pearson')
    print(corr_df)


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
  env.DO_CUT_OFF = False
  env.portpolio_index = 0
  env.portpolio_list = ['DANTE']
  env.start_date, env.end_date,_ = ['2021-01-12', '2022-02-10','']
  env.report_name = None
  env.reblancing_rule='AW4/11'
  env.RESULT_PLOT =False
  #env.reblancing_rule='B&H'

  sim1 = Simulation(env=env).Run()
  print(sim1.trade_log[0:20])
  print(sim1.get_capital(date=env.end_date))
  print(sim1.get_cmgr())
  print(sim1.get_cagr())

