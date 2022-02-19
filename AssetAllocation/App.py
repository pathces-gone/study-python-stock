import streamlit as st
import numpy as np
import pandas as pd
import os, datetime

import altair as alt

import ETFUtils
from ETF import ETF
from Portpolio import Portpolio
from Simulation import Simulation, SimEnvironment, SimResult
from StaticAA import StaticAA
from DynamicAA import DynamicAA 




class AssetAllocateEnv(object):
    AssetAllocateType:str = 'Dynamic'
    Tactic:str = 'DualMomentum'
    AssetGroup = {'Aggressive':{'SPY':'SPY','EFA':'EFA','AGG':'AGG'}}
    #{'Aggressive':{'QRFT':'QRFT','EFA':'EFA','AGG':'AGG'}}

class Backtest(object):
    def __init__(self):
        self.start_date="2020-01-03"
        self.end_date  ="2020-02-21"
        self.capital   =10_000_000

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
        sim_df['Symbol'] = np.repeat(sim.sim_name, len(sim_df))

        sim_cap_max = sim_df['Capital'].max()
        sim_cap_min = sim_df['Capital'].min()

        alt.data_transformers.enable('csv')
        sim_lines = alt.Chart(sim_df).mark_line(point=False).encode(
            x='Date',
            y=alt.Y('Capital', scale=alt.Scale(domain=[sim_cap_min, sim_cap_max])),
            color='Symbol'
        )
        return sim_lines


class GuiApp(Backtest):
    def __init__(self):

        sim1 = AssetAllocateEnv()
 
        self.sim_result = Backtest().Run(aaenv=sim1)
        pass

    def display_table(self):
        table = self.sim_result.trade_log
        st.table(table)

    def display_chart(self):
        sim_lines = self.get_altair_chart(self.sim_result)
        st.altair_chart(sim_lines, use_container_width=True)


if __name__ == '__main__':    
    app = GuiApp()
    #app.display_table()
    #app.display_chart()

