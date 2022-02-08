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
    
    def Run(self, sim_assets:dict ,sim_env:SimEnvironment):
        sim_portpolio = Portpolio(name=sim_env.portpolio_list[0], is_usd_krw_need=True)
        sim_result    = Simulation(portpolio=sim_portpolio, env=sim_env).Run()
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
      env.PRINT_TRADE_LOG = False
      env.FIXED_EXCHANGE_RATE = False
      return env

    sim1_assets = {'GTAA-NON':'GTAA-NON'}
    sim1_env    = set_simenv(asset_list=sim1_assets,capital=10_000_000,start_date="2007-08-28",end_date="2008-04-01")  
    sim_result = StaticAA().Run(sim_assets=sim1_assets, sim_env=sim1_env)