import numpy as np
import pandas as pd
import os, datetime

import matplotlib.pyplot as plt
import altair as alt

import ETFUtils
from ETF import ETF
from Portpolio import Portpolio
from Simulation import Simulation, SimEnvironment, SimResult
from StaticAA import StaticAA
from DynamicAA import DynamicAA 


class AssetAllocateEnv(object):
    def __init__(self, 
            AssetAllocateType:str = 'Dynamic',
            Tactic:str = 'DualMomentum',
            AssetGroup = {'Aggressive':{'SPY':'SPY','EFA':'EFA','AGG':'AGG'}}):
        self.AssetAllocateType = AssetAllocateType
        self.Tactic = Tactic
        self.AssetGroup = AssetGroup


class Backtest(object):
    def __init__(self, start_date:str="2020-01-03", end_date:str="2020-02-21", capital:int=10_000_000):
        self.start_date= start_date
        self.end_date  = end_date
        self.capital   = capital

    def Run(self, aaenv:AssetAllocateEnv):
        def dynamic_set_simenv(asset_list:dict, capital:int, start_date:str, end_date:str):
            asset_groups = asset_list.keys()
            asset_yamls = np.array([])
            for asset_group in asset_groups:
                asset_names  = asset_list[asset_group] 
                asset_yamls  = np.append(asset_yamls,[os.path.join('DynamicAA',name) for name in asset_names])

            env = SimEnvironment()
            env.portpolio_index = 0
            env.portpolio_list  = asset_yamls
            env.start_capital_krw = capital
            env.start_date, env.end_date = [start_date, end_date]
            env.reblancing_rule='B&H'

            # is needed?
            env.market_open_date = ETFUtils.get_trading_date(ticker='SPY')
            env.DO_CUT_OFF = False
            env.PRINT_TRADE_LOG = False
            env.FIXED_EXCHANGE_RATE = False
            return env

        def static_set_simenv(asset_list:dict, capital:int, start_date:str, end_date:str):
            asset_names = asset_list.keys()
            asset_yamls = [os.path.join(name) for name in asset_names] 

            env = SimEnvironment()
            env.portpolio_index = 0
            env.portpolio_list = asset_yamls
            env.start_capital_krw = 10_000_000
            env.start_date, env.end_date = [start_date, end_date]
            env.reblancing_rule = 'AW4/11'
            env.market_open_date = ETFUtils.get_trading_date(ticker='SPY')

            env.DO_CUT_OFF = False
            env.PRINT_TRADE_LOG = True
            env.FIXED_EXCHANGE_RATE = False
            return env

        start_date = self.start_date
        end_date   = self.end_date
        capital    = self.capital

        sim_assets = aaenv.AssetGroup
        if aaenv.AssetAllocateType == 'Dynamic':
            set_simenv = dynamic_set_simenv
            simulator = DynamicAA()
        else:
            set_simenv = static_set_simenv
            simulator = StaticAA()

        sim_env    = set_simenv(asset_list=sim_assets,capital=capital,start_date=start_date,end_date=end_date)
        sim_result = simulator.Run(sim_assets=sim_assets, sim_env=sim_env, tactic=aaenv.Tactic)
        return sim_result

    @staticmethod
    def get_altair_chart(sim:SimResult):
        sim_df = sim.trade_log.loc[:, ['Date', 'Capital']]
        sim_df['Capital'] = sim_df['Capital'].rolling(window=3).mean()
        sim_df['Symbol'] = np.repeat(sim.sim_name, len(sim_df))

        sim_cap_max = sim_df['Capital'].max()
        sim_cap_min = sim_df['Capital'].min()

        #alt.data_transformers.enable('csv')
        sim_line = alt.Chart(sim_df).mark_line(point=False).encode(
            x='Date',
            y=alt.Y('Capital', scale=alt.Scale(domain=[sim_cap_min, sim_cap_max])),
            color='Symbol'
        )
        return sim_line








if __name__ == '__main__':
    """
    =====================================
              Init
    =====================================
    """
    start_date= "2018-01-23"
    end_date = "2022-02-03"
    capital  = 10_000_000

    sims= [
        ['Dynamic','DualMomentum',{'Aggressive':{'SPY':'SPY','EFA':'EFA','AGG':'AGG'}}],
        ['Dynamic','VAA_aggressive',{'Aggressive':{'SPY':'SPY','EFA':'EFA','EEM':'EEM','AGG':'AGG'},'Conservative':{'LQD':'LQD','IEF':'IEF','SHY':'SHY'}}],
        #['Static', 'AW4/11', {'DANTE':'DANTE'}],
        ['Static', 'LAA', {'LAA':'LAA'}],

    ]
    
    """
    =====================================
              Run
    =====================================
    """
    sim_results = np.array([])
    plots = np.array([])
    for sim in sims:
        env = AssetAllocateEnv(AssetAllocateType=sim[0], Tactic=sim[1], AssetGroup=sim[2])
        sim_result = Backtest(start_date=start_date, end_date=end_date, capital=capital).Run(env)
        sim_results = np.append(sim_results,sim_result)
        plots = np.append(plots,Backtest.get_altair_chart(sim_result))

    avg_result = SimResult()
    avg_result.average_result(sim_results)
    sim_results = np.append(sim_results,avg_result)
    plots = np.append(plots,Backtest.get_altair_chart(avg_result))

    """
    =====================================
              Plot
    =====================================
    """
    lines= np.sum(plots).properties(
        width=16*60,
        height=10*60
    )
    lines.show()
