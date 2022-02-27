import numpy as np
import yaml, os
import datetime
from dateutil import relativedelta

import ETFUtils
from ETF import ETF
from Portpolio import Portpolio
from Simulation import Simulation, SimEnvironment


class StaticAA(Simulation):
    def __init__(self):
        pass
    
    def Run(self, sim_assets:dict ,sim_env:SimEnvironment, tactic:str='sim1'):
        sim_portpolio = Portpolio(name=sim_env.portpolio_list[0], is_usd_krw_need=True)
        sim_result    = Simulation(portpolio=sim_portpolio, env=sim_env).Run()
        sim_result.sim_name = tactic
        print(sim_result.get_cagr())
        return sim_result #SimResult


if __name__ == '__main__':
    def set_simenv(asset_list:dict, capital:int, start_date:str, end_date:str):
      asset_names = asset_list.keys()
      asset_yamls = [os.path.join(name) for name in asset_names] 

      env = SimEnvironment()
      env.portpolio_index = 0
      env.portpolio_list = asset_yamls
      env.start_capital_krw = 10_000_000
      env.start_date, env.end_date = [start_date, end_date]
      env.reblancing_rule='AW4/11'
      env.market_open_date = ETFUtils.get_trading_date(ticker='SPY')

      env.DO_CUT_OFF = False
      env.PRINT_TRADE_LOG = True
      env.FIXED_EXCHANGE_RATE = False
      return env

    start_date="2021-11-01"
    end_date="2022-02-02"


    #sim1_assets = {'GTAA-NON':'GTAA-NON'}
    sim1_assets = {'MyPortpolio':'MyPortpolio'}
    sim1_env    = set_simenv(asset_list=sim1_assets,capital=10_000_000,start_date=start_date,end_date=end_date)  
    sim1_result = StaticAA().Run(sim_assets=sim1_assets, sim_env=sim1_env)
    print(sim1_result.get_cagr())
    print(np.min(sim1_result.trade_log['MDD']))


    if 0:
      sim2_assets = {'DANTE':'DANTE'}
      sim2_env    = set_simenv(asset_list=sim2_assets,capital=10_000_000,start_date=start_date,end_date=end_date)  
      sim2_result = StaticAA().Run(sim_assets=sim2_assets, sim_env=sim2_env)
      print(sim2_result.get_cagr())
      print(np.min(sim2_result.trade_log['MDD']))

      if 0:
        import matplotlib.pyplot as plt
        plt.figure(figsize=[16,10])
        plt.semilogy(sim1_result.trade_log['Capital'],  label="%s AW4/11"%(list(sim1_assets.keys())[0]))
        plt.semilogy(sim2_result.trade_log['Capital'],  label="%s AW4/11"%(list(sim2_assets.keys())[0]))
        plt.yscale("log")
        plt.legend()
        plt.show()

        plt.figure(figsize=[16,10])
        plt.plot(sim1_result.trade_log['MDD'],  label="%s AW4/11"%(list(sim1_assets.keys())[0]))
        plt.plot(sim2_result.trade_log['MDD'],  label="%s AW4/11"%(list(sim2_assets.keys())[0]))
        plt.legend()
        plt.show()