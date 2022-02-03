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
  mmd_history     = np.array([])
  capital_history = np.array([])
  date_history    = np.array([])

  def get_cagr(self):
    start_date   = self.date_history[0]
    end_date     = self.date_history[-1]
    init_capital = self.get_capital(start_date)
    last_capital = self.get_capital(end_date)
    d1 = datetime.datetime.strptime(start_date,"%Y-%m-%d")
    d2 = datetime.datetime.strptime(end_date,"%Y-%m-%d")
    num_year = (d2.year - d1.year)
    if num_year > 0:
      cagr = (last_capital/init_capital)**(1/num_year)
      cagr = round((cagr-1)*100,2)
    else:
      cagr=0.00
    return cagr

  def get_cmgr(self):
    start_date   = self.date_history[0]
    end_date     = self.date_history[-1]
    init_capital = self.get_capital(start_date)
    last_capital = self.get_capital(end_date)
    d1 = datetime.datetime.strptime(start_date,"%Y-%m-%d")
    d2 = datetime.datetime.strptime(end_date,"%Y-%m-%d")
    num_month = (d2.year - d1.year) * 12 + (d2.month - d1.month)
    if num_month > 0:
      cmgr = (last_capital/init_capital)**(1/num_month)
      cmgr = round((cmgr-1)*100,2)
    else:
      cmgr=0.00
    return cmgr

  def get_capital(self,date:str):
    index = np.where(self.date_history == date)[0]
    if index.size:
      ret= float(self.capital_history[index])
    else:
      print('get_capital:  date not found')
      """
        TODO next date
      """
      ret = 0.0
    return ret


class SimEnvironment(SimResult):
  """
    Simulation Environment
  """
  if 1: #Sim Data
    start_capital_krw =  10_000_000 
    start_date, end_date, _ = ['2018-02-05', '2019-01-03', 'kospi양적긴축폭락장']
    portpolio_name = 'DANTE'
    reserve_per_period = 0
    reblancing_rule = 'AW4/11' # 'B&H'

  if 1: # Report
    report_name = None

  if 1: #Sim Options
    FIXED_EXCHANGE_RATE = True
    PRINT_TRADE_LOG = False
    PRINT_BUY_PORTPOLIO  = False
    PRINT_SELL_PORTPOLIO = False
    LIMIT_RATIO = True
    RESULT_PLOT = False
    FIGSIZE = (10,5)



class Simulation(object):
  """ Return Simulation
    Simulation Root node of Portpolio (ETF chain)
  """
  #def __init__(self, portpolio:Portpolio, capital:int, report_name:str):
  def __init__(self, portpolio:Portpolio=None, env:SimEnvironment=None):
    self.env = env
    if portpolio:
      self.portpolio = portpolio
    else:
      self.portpolio = Portpolio(env.portpolio_name)

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



  def buy(self, etf:ETF, date:str, percent:float)->list:
    """ Return [last_qty, avg_price, self.cash, trade_date]

    """
    last_qty = self.hold_qtys[etf.code]
    curr_price, trade_date = etf.get_price(date=date)
    avg_price = self.avg_price[etf.code]
    if avg_price == 0:
      avg_price = curr_price

    trade_date_str = trade_date.strftime('%Y-%m-%d')
    if etf.src == 'YAHOO':
      if self.env.FIXED_EXCHANGE_RATE:
        usd_krw = 1150
      else:
        usd_krw = self.portpolio.usd_krw.loc[self.portpolio.usd_krw['Date']==trade_date_str,'Close'].to_list()[0]
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
        ret = [update_hold_qtys, update_avg_price, update_cash,trade_date]
      else:
        ret= [last_qty, avg_price, self.cash, trade_date]
    else:
      ret = [last_qty, avg_price, self.cash, trade_date]
    return ret


  def sell(self, etf:ETF, date:str, percent:float)->list:
    """ Return [update_hold_qtys, update_earn, update_cash, trade_date]

    """
    last_qty  = int(self.hold_qtys[etf.code])
    last_earn = self.earn[etf.code]

    curr_price, trade_date = etf.get_price(date=date)
    sell_qty = int(self.hold_qtys[etf.code]*(percent/100))

    trade_date_str = trade_date.strftime('%Y-%m-%d')
    if etf.src == 'YAHOO':
      if self.env.FIXED_EXCHANGE_RATE:
        usd_krw = 1150
      else:
        usd_krw = self.portpolio.usd_krw.loc[self.portpolio.usd_krw['Date']==trade_date_str,'Close'].to_list()[0]
    else:
      usd_krw = 1.0

    curr_price_krw = curr_price*usd_krw

    if last_qty >= sell_qty:
      update_hold_qtys = last_qty - sell_qty
      update_earn = (curr_price_krw - self.avg_price[etf.code])*sell_qty
      update_cash = self.cash + curr_price_krw*sell_qty
      ret = [update_hold_qtys, update_earn, update_cash, trade_date]
    else:
      ret = [last_qty, last_earn, self.cash ,trade_date]
    return ret



  def print_info(self):
    """ Return

    """
    etfs,_ = self.portpolio.get_etf()
    print('='*160)
    print('Portpoilo Info - %s'%self.portpolio.name)
    print("%20s | %30s %20s | %10s %10s %10s %10s %10s %10s %12s"%('index','name','code', 'max(%)','ratio(%)', 'price(krw)', 'qty', 'buy', 'earn','earn_ratio'))
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

    if self.env.PRINT_BUY_PORTPOLIO:
      print('\nBuy - %s'%self.portpolio.name)
      print("%20s | %30s %20s | %10s %10s %10s %10s %10s"%('index','name','code','budget','ratio(%)', 'price', 'qty', 'buy'))
      print('-'*140)
      total_buy = 0
      for i,etf in enumerate(etfs):
        update_hold_qtys, update_avg_price, update_cash, trade_date = self.buy(etf=etf, date=date, percent=100)
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
        update_hold_qtys, update_avg_price, update_cash, trade_date = self.buy(etf=etf, date=date, percent=100)
        self.hold_qtys[etf.code] = update_hold_qtys
        self.avg_price[etf.code] = update_avg_price
        self.cash = update_cash
        total_buy += update_hold_qtys*update_avg_price

      return total_buy,trade_date



  def sell_portpolio(self, date:str):#,buy_prices:np.ndarray, buy_qtys:np.ndarray):
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
        update_hold_qtys, update_earn, update_cash, trade_date = self.sell(etf=etf, date=date, percent=100)
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
        update_hold_qtys, update_earn, update_cash,trade_date = self.sell(etf=etf, date=date, percent=100)
        self.hold_qtys[etf.code] = update_hold_qtys
        self.earn[etf.code] = update_earn
        self.cash = update_cash
        total_sell = self.cash
    return total_sell,trade_date


  def Run(self):
    """ Algorithm
      시작시간부터 하루하루 넘어가면서 MDD계산
    """
    start_date      = self.env.start_date
    end_date        = self.env.end_date
    reblancing_rule = self.env.reblancing_rule
    dt_start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d")
    dt_end_date = datetime.datetime.strptime(end_date,"%Y-%m-%d")

    """
      plot array
    """
    debug_mmd = np.array([])
    debug_capital = np.array([])
    debug_date= np.array([])

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
    if reblancing_rule=='AW4/11':
      AW_4  = datetime.datetime.strptime('2000-04-30',"%Y-%m-%d") 
      AW_11 = datetime.datetime.strptime('2000-11-30',"%Y-%m-%d")
      s_year = pivot_date.year
      s_year_4 = 0
      s_year_11 = 0

    """
    =========================================================================
                          Trading Start 
    ========================================================================= 
    """
    total_buy, trade_date = self.buy_portpolio(date=start_date)
    etfs,ratios = self.portpolio.get_etf()
    if self.env.PRINT_TRADE_LOG:
      self.print_info()

    while(pivot_date <= dt_end_date):
      """
      =========================================================================
                              Strategy Start 
      ========================================================================= 
      """
      if reblancing_rule=='AW4/11':
        if s_year != pivot_date.year:
          s_year =  pivot_date.year
          s_year_4 = 0
          s_year_11 = 0

        AW_4_  = ((trade_date-AW_4).days  - (trade_date.year-AW_4.year)*365) + 1
        AW_11_ = ((trade_date-AW_11).days - (trade_date.year-AW_11.year)*365) + 1

        if((s_year_4==0 and (0<=AW_4_<3)) | (s_year_11==0 and(0<=AW_11_<3))):
          s_year_4 = (4> AW_4_ >= 0)
          s_year_11= (4>AW_11_ >= 0)

          if 1: # cma 이자
            cma_days = (pivot_date-last_reblance_day).days
            cma=(self.cash*(0.012)/365) * cma_days
            #print('이자: %d -> %d [%d]'%(self.cash,cma,cma_days))
            self.cash += cma
            last_reblance_day = pivot_date

          count += 1
          self.cash += additional_paid_in
          last_capital = self.capital + additional_paid_in

          # Reblancing
          total_sell,trade_date = self.sell_portpolio(date=pivot_date.strftime('%Y-%m-%d'))
          earn_ratio = round((total_sell-last_capital)/last_capital*100,2)

          self.capital = total_sell
          _ = self.buy_portpolio(date=pivot_date.strftime('%Y-%m-%d'))

          # MDD
          earn = 0
          for k,v in self.earn.items():
            earn += v
          draw_down = (earn)/last_capital*100

          max_draw_down = draw_down if draw_down<max_draw_down else max_draw_down

          if self.env.PRINT_TRADE_LOG:
            print(trade_date,'%10d --> %10d  %4.2f[%%]  MDD: %.2f[%%]'%(last_capital,total_sell, earn_ratio,max_draw_down))

          """
            Next date
          """
          debug_mmd = np.append(debug_mmd,round(max_draw_down,2))
          debug_capital = np.append(debug_capital,round(last_capital+temp_earn,2))
          debug_date =  np.append(debug_date,trade_date.strftime('%Y-%m-%d'))
          max_draw_down= 0
          cutoff_flag = False

          if pivot_date == trade_date:
            pivot_date = ETFUtils.get_next_date(pivot_date)
          else:
            pivot_date = ETFUtils.get_next_date(trade_date)
          continue

        else:
          """
            MDD
          """
          temp_earn = 0
          for i,etf in enumerate(etfs):
            update_hold_qtys, update_earn, update_cash, trade_date = self.sell(etf=etf, date=pivot_date.strftime('%Y-%m-%d'), percent=100)
            temp_earn += update_earn

          last_capital = self.capital
          draw_down = (temp_earn)/last_capital*100

          max_draw_down = draw_down if draw_down<max_draw_down else max_draw_down

      elif reblancing_rule=='B&H':
          """
            MDD
          """
          temp_earn = 0
          for i,etf in enumerate(etfs):
            update_hold_qtys, update_earn, update_cash, trade_date = self.sell(etf=etf, date=pivot_date.strftime('%Y-%m-%d'), percent=100)
            temp_earn += update_earn

          last_capital = self.capital
          draw_down = (temp_earn)/last_capital*100

          max_draw_down = draw_down if draw_down<max_draw_down else max_draw_down
      else:
        break

      """
      =========================================================================
                              Strategy end 
      ========================================================================= 
      """

      if self.env.DO_CUT_OFF:
        if (max_draw_down < -10) & (cutoff_flag==False):
          if self.env.PRINT_TRADE_LOG:
            print(pivot_date,'Cut-off!!   mmd: %2.2f%%'%max_draw_down)
          total_sell, trade_date = self.sell_portpolio(date=pivot_date.strftime('%Y-%m-%d'))
          self.capital = total_sell
          cutoff_flag = True

      """
        Next date
      """
      debug_mmd = np.append(debug_mmd,round(max_draw_down,2))
      debug_capital = np.append(debug_capital,round(last_capital+temp_earn,2))
      debug_date =  np.append(debug_date,trade_date.strftime('%Y-%m-%d'))

      if pivot_date == trade_date:
        pivot_date = ETFUtils.get_next_date(pivot_date)
      else:
        pivot_date = ETFUtils.get_next_date(trade_date)

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
      total_sell, trade_date = self.sell_portpolio(date=end_date)
      earn_ratio = round((total_sell-last_capital)/last_capital*100,2)

      self.budgets += count*additional_paid_in
      if self.env.PRINT_TRADE_LOG:
        print(pivot_date,'%10d --> %10d  %4.2f[%%]  MDD: %.2f[%%]'%(last_capital,total_sell, earn_ratio,max_draw_down))
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

      ax1.plot(range(len(debug_mmd)), debug_mmd , label = 'mmd(%)')
      ax2.plot(range(len(debug_mmd)), debug_capital, label = 'capital')
      ax3.plot(df_usd_krw['Date'],df_usd_krw['Close'], label='usd-krw')

      plt.xticks(np.arange(0, len(df_usd_krw['Date'])+1, 30), rotation=45)

      ax1.legend()
      ax2.legend()
      ax3.legend()
      plt.grid()

      if self.do_save:
        plt.savefig(self.report_path)
      plt.show()

    sim_result = self.env
    sim_result.mmd_history     = debug_mmd
    sim_result.capital_history = debug_capital
    sim_result.date_history    = debug_date
    return sim_result



class SimulationReview(Simulation):
  def __init__(self, sim1:list, sim2:list):
    sim1_name, sim1_mmd, sim1_capital, sim1_date = sim1
    sim2_name, sim2_mmd, sim2_capital, sim2_date = sim2
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

  def get_inflection(self,start_date:str=None, end_date:str=None):
    raw_df = self.raw_df

    st = raw_df['Date'].iloc[0] if start_date == None else start_date
    ed = raw_df['Date'].iloc[-1]  if end_date == None else end_date

    df = raw_df[(st<=raw_df['Date']) & (raw_df['Date']<=ed)].iloc[::-1]
    df_close = df['sim1']

    inflection = pd.DataFrame(columns=['Date', 'High', 'Low'])
    inflection['Date'] = df['Date']
    inflection['Point'] = [0 for _ in range(len(df['Date']))]
    
    forward1 = df_close.iloc[1:]
    forward2 = df_close.iloc[2:]

    df_index = df_close.index
    min_ = df_index[-1]+2
    max_ = df_index[0]-1

    for i in df_index:
      if min_ < i < max_:
        c = df_close.loc[i]
        f1 = forward1.loc[i-1]
        f2 = forward2.loc[i-2]
        if c < f1:
          if f1 > f2:
            inflection['High'].loc[i-1] = f1

        if c > f1:
          if f1 < f2:
            inflection['Low'].loc[i-1] = f1

    
    inflection['High'].replace(0, np.nan, inplace=True)
    inflection['Low'].replace(0, np.nan, inplace=True)
    
    import matplotlib.pyplot as plt
    plt.figure(figsize=FIGSIZE)
    plt.plot(df_close)
    plt.plot(inflection['High'],'bo')
    plt.plot(inflection['Low'],'ro')
    #plt.hlines(inflection['Point'],xmin=7150,xmax=7300)
    
  def get_vix(self, start_date:str=None, end_date:str=None):
    """
      TODO
    """
    ticker = 'VIXM'
    vix = ETF(name=ticker, code=ticker, index=ticker, src='YAHOO')
    vix.get_chart(start_date=start_date ,end_date=end_date)

"""
=========================================================================
                            MAIN
========================================================================= 
"""
if __name__ == '__main__':
  env = SimEnvironment()
  env.start_capital_krw =  12_000_000 
  env.PRINT_TRADE_LOG = False
  env.DO_CUT_OFF = False
  env.portpolio_name = 'DANTE'
  env.start_date, env.end_date,_ = ['2021-01-12', '2021-02-26','']
  env.report_name = None
  env.reblancing_rule='AW4/11'

  sim1 = Simulation(env=env).Run()
  print(sim1.get_capital(date=env.end_date))
  print(sim1.get_cmgr())
  print(sim1.get_cagr())

