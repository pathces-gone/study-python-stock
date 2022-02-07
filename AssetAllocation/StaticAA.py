import numpy as np
import yaml, os
import datetime
from dateutil import relativedelta

from ETF import ETF
from Portpolio import Portpolio
from Simulation import Simulation, SimEnvironment


class StaticAA(Simulation):
    def __init__(self):
        pass

        
    def Run(self):
        def set_simenv(asset_group_name:str, capital:int, start_date:datetime, end_date:int):
            asset_group_name = os.path.join(asset_group_name)
            env = SimEnvironment()
            env.start_capital_krw, env.portpolio_name = [capital ,asset_group_name]
            env.start_date, env.end_date = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
            env.reblancing_rule='AW4/11'
            env.DO_CUT_OFF = False
            env.PRINT_TRADE_LOG = False
            env.reserve_per_period = 0
            asset_group = Portpolio(name=asset_group_name,is_usd_krw_need=False)
            return env, asset_group

        init_capital = 10_000_000
        sim_start_date = datetime.datetime.strptime("2005-01-03","%Y-%m-%d")
        sim_end_date   = datetime.datetime.strptime("2020-01-28","%Y-%m-%d")
        today = sim_start_date
        capital = init_capital
        mmd = 0