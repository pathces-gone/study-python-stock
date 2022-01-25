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


FIXED_EXCHANGE_RATE = True
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
    """ Return [last_qty, avg_price, self.cash, trade_date]
  
    """
    last_qty = self.hold_qtys[etf.code]
    curr_price, trade_date = etf.get_price(date=date)
    avg_price = self.avg_price[etf.code]
    if avg_price == 0:
      avg_price = curr_price

    trade_date_str = trade_date.strftime('%Y-%m-%d')
    if etf.src == 'YAHOO':
      if FIXED_EXCHANGE_RATE:
        usd_krw = 1150
      else:
        usd_krw = self.portpolio.usd_krw.loc[self.portpolio.usd_krw['Date']==trade_date_str,'Close'].to_list()[0]
    else:
      usd_krw = 1.0

    curr_price_krw = curr_price*usd_krw
    buy_percent = (self.max_ratios[etf.code]*(percent/100))
    buy_qty = int(buy_percent*self.capital/100 / curr_price_krw)

    if LIMIT_RATIO:
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
      if FIXED_EXCHANGE_RATE:
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

    if PRINT_BUY_PORTPOLIO==True:
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

    if PRINT_SELL_PORTPOLIO==True:
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


  def Run(self, start_date:str, end_date:str, what:str):
    """ Algorithm
      시작시간부터 하루하루 넘어가면서 MDD계산
    """
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
    cutoff_flag = not DO_CUT_OFF
    max_draw_down = 0
    count =0
    additional_paid_in = 0 #8_000_000

    pivot_date = dt_start_date

    last_reblance_day = pivot_date
    if what=='AW4/11':
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
    #self.print_info()

    while(pivot_date <= dt_end_date):
      """
      =========================================================================
                              Strategy Start 
      ========================================================================= 
      """
      if what=='AW4/11':
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

          if PRINT_TRADE_LOG:
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


      elif what=='B&H':
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

      elif what == 'AbsMomentum':
        """
      
        """
        pass
      elif what == 'RelativeMomentum':
        """
          <Relative Strength Strategies for Investing>
            * This portfolio begins with the asset classes listed in the GTAA Moderate allocation.
            * selects the top six out of the thirteen assets as ranked by an average of 1, 3, 6, and
              12-month total returns (momentum).
                1. US Large-cap value - 5%
                2. US Large-cap Momentum - 5%
                3. US Small-cap value - 5%
                4. US Small-cap Momentum - 5%
                5. Foreign Developed - 10%
                6. Foreign Emerging  - 10%
                7. US 10 Year Goverment Bonds  - 5%
                8. Foreign 10 Year Goverment Bonds  - 5%
                9. US Corporate Bonds  - 5%
                10. US 30 Year Goverment Bonds  - 5%
                11. Commodities(Index)  - 10%
                12. Commodities(Gold)   - 10%
                12. Real Estate Investment Trusts - 20%
            * The assets are only included if they are above their long-term moving average, 
            otherwise that portion of the portfolio is moved to cash.
        """
        pass

      elif what == 'DualMomentum':
        pass
      else:
        pass

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
      print(pivot_date,'%10d --> %10d  %4.2f[%%]  MDD: %.2f[%%]'%(last_capital,total_sell, earn_ratio,max_draw_down))

      self.budgets += count*additional_paid_in
      self.print_info()

      if 1: # CAGR
        if int((dt_end_date-dt_start_date).days/365) > 0:
          cagr = (self.capital/self.budgets)**(1/int((dt_end_date-dt_start_date).days/365))
          cagr = round((cagr-1)*100,2)
          print("CAGR= %3.2f [%%]"%cagr)
    if 0:
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

      #ax1.plot(debug_date, debug_mmd , label = 'mmd(%)')
      #ax2.plot(debug_date, debug_capital, label = 'capital')
      ax1.plot(range(len(debug_mmd)), debug_mmd , label = 'mmd(%)')
      ax2.plot(range(len(debug_mmd)), debug_capital, label = 'capital')
      ax3.plot(df_usd_krw['Date'],df_usd_krw['Close'], label='usd-krw')


      plt.xticks(np.arange(0, len(df_usd_krw['Date'])+1, 30), rotation=45)

      ax1.legend()
      ax2.legend()
      ax3.legend()
      plt.grid()

      if self.do_save:
        plt.savefig(self.report_name)
      plt.show()

    return [debug_mmd,debug_capital,debug_date]







class SimulationReview(Simulation):
  def __init__(self, sim1:list, sim2:list):
    sim1_mmd, sim1_capital, sim1_date = sim1
    sim2_mmd, sim2_capital, sim2_date = sim2
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
    plt.plot(sim1_capital,label='sim1')
    plt.plot(sim2_capital,label='sim2')
    plt.legend()


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

    return 0



"""
=========================================================================
                            MAIN
========================================================================= 
"""
if __name__ == '__main__':

  start_capital_krw =  6_000_000 
  capital = start_capital_krw

  start_date, end_date, _ = ['2018-02-05', '2019-01-03', 'kospi양적긴축폭락장']

  if 0:
    PRINT_TRADE_LOG = True
    DO_CUT_OFF = 0
    portpolio_name = 'GTAA'
    start_date, end_date,_ = ['2022-01-04', '2022-01-24','gtaa-non']
    #start_date, end_date,_ = ['2006-11-02', '2022-01-02','gtaa-non']
    portpolio = Portpolio(portpolio_name)
    report_name = portpolio_name + '_cutoff10'
    sim1 = Simulation(portpolio=portpolio, capital=capital,report_name=report_name).Run(start_date= start_date, end_date= end_date, what='AW4/11')
  
  if 0:
    PRINT_TRADE_LOG = True
    DO_CUT_OFF = 0
    report_name = None
    start_date, end_date,_ = ['2020-01-04', '2020-04-24','']

    portpolio_name = 'DANTE'
    portpolio = Portpolio(portpolio_name)
    sim1 = Simulation(portpolio=portpolio, capital=capital,report_name=report_name).Run(start_date= start_date, end_date= end_date, what='AW4/11')

    portpolio_name = 'MyPortpolio'
    portpolio = Portpolio(portpolio_name)
    sim2 = Simulation(portpolio=portpolio, capital=capital,report_name=report_name).Run(start_date= start_date, end_date= end_date, what='AW4/11')

    SimulationReview(sim1=sim1, sim2=sim2).get_correlation()

  if 1:
    FIXED_EXCHANGE_RATE = True
    PRINT_TRADE_LOG = True
    DO_CUT_OFF = 0
    report_name = None
    start_date, end_date,_ = ['2020-01-04', '2020-04-24','']

    portpolio_name = 'DBC'
    portpolio = Portpolio(portpolio_name)
    sim1 = Simulation(portpolio=portpolio, capital=capital,report_name=report_name).Run(start_date= start_date, end_date= end_date, what='AW4/11')

    portpolio_name = 'SingleStocks'
    portpolio = Portpolio(portpolio_name)
    sim2 = Simulation(portpolio=portpolio, capital=capital,report_name=report_name).Run(start_date= start_date, end_date= end_date, what='AW4/11')

    SimulationReview(sim1=sim1, sim2=sim2).get_correlation()
