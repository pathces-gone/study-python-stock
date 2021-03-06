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
            env.DO_CUT_OFF = True
            env.PRINT_TRADE_LOG = False
            env.FIXED_EXCHANGE_RATE = True
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

            env.DO_CUT_OFF = True
            env.PRINT_TRADE_LOG = True
            env.FIXED_EXCHANGE_RATE = True
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
    def get_altair_chart(sim:pd.DataFrame, sim_name:str, key:str='Capital'):
        #alt.data_transformers.enable('csv',urlpath=os.path.dirname(__file__))
        sim_df = sim.loc[:, ['Date', key]]
        sim_df[key] = sim_df[key].rolling(window=3).mean()
        sim_df['Symbol'] = np.repeat(sim_name, len(sim_df))

        sim_cap_max = sim_df[key].max()
        sim_cap_min = sim_df[key].min()

        #alt.data_transformers.enable('csv')
        if key == 'MDD':
            sim_line = alt.Chart(sim_df).mark_line(
                    point=False,
                    strokeDash=[8, 6], size=2).encode(y=alt.datum(350)    
                ).encode(
                x='Date',
                y=alt.Y(key, scale=alt.Scale(domain=[sim_cap_min, sim_cap_max])),
                color='Symbol'
            )

        else:
            sim_line = alt.Chart(sim_df).mark_line(point=False).encode(
                x='Date',
                y=alt.Y(key, scale=alt.Scale(domain=[sim_cap_min, sim_cap_max])),
                color='Symbol'
            )
        return sim_line








if __name__ == '__main__':
    """
    =====================================
              Init
    =====================================
    """

    # 2009-2015
    # 2018-2020
    #start_date= "2009-02-02"
    #end_date  = "2015-02-02"
    
    start_date= "2010-01-03"
    end_date  = "2022-03-16"
    
    #start_date= "2005-02-02"
    #end_date  = "2022-02-02"
    

    #start_date= "2005-01-03"
    #end_date  = "2022-02-24"

    capital  = 10_000_000

    sims= [
        #['Static', 'GTAA', {'GTAA-NON':'GTAA-NON'}],
        #['Static', 'DANTE', {'DANTE':'DANTE'}],
        #['Dynamic','DualMomentum',{'Aggressive':{'SPY':'SPY','EFA':'EFA','QQQ':'QQQ'},'Conservative':{'SHY':'SHY'}}],
        #['Dynamic','DualMomentum',{'Aggressive':{'SPY':'SPY','EFA':'EFA','QQQ':'QQQ','DIA':'DIA'},'Conservative':{'IEF':'IEF','SHY':'SHY'}}],
        #['Dynamic','DualMomentum',{'Aggressive':{'SPY':'SPY','DBC':'DBC','QQQ':'QQQ','VNQ':'VNQ'},'Conservative':{'IEF':'IEF','SHY':'SHY'}}],
        #['Dynamic','DualMomentum',{'Aggressive':{'IYT':'IYT','DBC':'DBC'},'Conservative':{'AGG':'AGG'}}],
        #['Dynamic','DualMomentum',{'Aggressive':{'SPY':'SPY','EFA':'EFA'},'Conservative':{'AGG':'AGG'}}],
        #['Dynamic','VAA_aggressive',{'Aggressive':{'SPY':'SPY','EFA':'EFA','EEM':'EEM','AGG':'AGG'},'Conservative':{'LQD':'LQD','IEF':'IEF','SHY':'SHY'}}],
        #['Static', 'SPY', {'DynamicAA/SPY':'DynamicAA/SPY'}],
        #['Static', 'qqq', {'qqq-aw':'qqq-aw'}],
        #['Static', 'spy', {'spy-aw':'spy-aw'}],
        #['Static', 'MyPortpolio', {'MyPortpolio':'MyPortpolio'}],
        #['Static', 'LAA', {'LAA':'LAA'}],
        #['Static', 'SingleStock', {'SingleStock':'SingleStock'}],
        #['Static', 'DynamicAA/IEF', {'DynamicAA/IEF':'DynamicAA/IEF'}],
        #['Static', 'DynamicAA/GLD', {'DynamicAA/GLD':'DynamicAA/GLD'}],
        #['Static', 'DynamicAA/SPY', {'DynamicAA/SPY':'DynamicAA/SPY'}],
        #['Static', 'DynamicAA/SPHY', {'DynamicAA/SPHY':'DynamicAA/SPHY'}],
        ['Static', 'DynamicAA/IYT', {'DynamicAA/IYT':'DynamicAA/IYT'}],
        #['Static', 'Fred/DGS10', {'Fred/DGS10':'Fred/DGS10'}],
        #['Static', 'Canary', {'Canary':'Canary'}],
    ]
    
    """
    =====================================
              Run
    =====================================
    """
    sim_results = np.array([])
    cap_plots = np.array([])
    mdd_plots = np.array([])
    for sim in sims:
        env = AssetAllocateEnv(AssetAllocateType=sim[0], Tactic=sim[1], AssetGroup=sim[2])
        sim_result = Backtest(start_date=start_date, end_date=end_date, capital=capital).Run(env)
        sim_result.trade_log['Date'] = sim_result.trade_log['Date'].apply(pd.to_datetime) 
        
        #mdd = sim_result.get_mdd_per_month(sim_result.trade_log)
        #sim_result.trade_log['MDD'] = mdd
        sim_results = np.append(sim_results,sim_result)
        cap_plots = np.append(cap_plots,Backtest.get_altair_chart(sim_result.trade_log, sim_result.sim_name,key='Capital'))
        #mdd_plots = np.append(mdd_plots,Backtest.get_altair_chart(sim_result,key='Yield'))

    avg_result = SimResult()
    avg_result.average_result(sim_results)
    avg_mdd = avg_result.get_mdd_per_month(avg_result.trade_log)
    avg_result.trade_log['MDD'] = avg_mdd
    sim_results = np.append(sim_results,avg_result)
    cap_plots = np.append(cap_plots,Backtest.get_altair_chart(avg_result.trade_log, avg_result.sim_name,key='Capital'))
   # mdd_plots = np.append(mdd_plots,Backtest.get_altair_chart(avg_result.trade_log, sim_result.sim_name,key='MDD'))




    """
    =====================================
              FRED
    =====================================
    """
    if 0:
      fred_df = ETFUtils.utils_get_price(code='DGS10', source='FRED')
      fred_df = fred_df.loc[(fred_df['Date']>=start_date) & (fred_df['Date']<=end_date),:]
      fred_plot = Backtest.get_altair_chart(fred_df,'DGS10',key='Close')

    """
    =====================================
              Plot
    =====================================
    """
    alt.data_transformers.disable_max_rows()
    capline= np.sum(cap_plots)
    if 0:
        #mddline= np.sum(mdd_plots)
        lines = alt.layer(capline,fred_plot).resolve_scale(
            y = 'independent'
        ).properties(
            width=16*30,
            height=10*30
        ) #.show()
    else:
        capline.properties(
            width=16*30,
            height=10*30
        ).show()