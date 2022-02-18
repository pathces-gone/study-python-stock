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




if __name__ == '__main__':
    """
    =====================================
              Dynamic AA
    =====================================
    """
    def set_simenv(asset_list:dict, capital:int, start_date:str, end_date:str):
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
        env.market_open_date = ETFUtils.get_trading_date(ticker='SPY')

        env.DO_CUT_OFF = False
        env.PRINT_TRADE_LOG = False
        env.FIXED_EXCHANGE_RATE = False
        return env
  
    start_date="2020-01-03"
    end_date  ="2020-02-21"

    sim1_assets = {'Aggressive':{'SPY':'SPY','EFA':'EFA','AGG':'AGG'}}
    ##sim1_assets = {'Aggressive':{'QRFT':'QRFT','EFA':'EFA','AGG':'AGG'}}
    sim1_env    = set_simenv(asset_list=sim1_assets,capital=10_000_000,start_date=start_date,end_date=end_date)
    daa1 = DynamicAA().Run(sim_assets=sim1_assets, sim_env=sim1_env, tactic='DualMomentum')

    if 1:
        sim2_assets = {'Aggressive':{'SPY':'SPY','EFA':'EFA','EEM':'EEM','AGG':'AGG'},'Conservative':{'LQD':'LQD','IEF':'IEF','SHY':'SHY'}}
        #sim1_assets = {'Aggressive':{'QRFT':'QRFT','EFA':'EFA','EEM':'EEM','AGG':'AGG'},'Conservative':{'LQD':'LQD','IEF':'IEF','SHY':'SHY'}}
        sim2_env    = set_simenv(asset_list=sim2_assets,capital=10_000_000,start_date=start_date,end_date=end_date)
        daa2 = DynamicAA().Run(sim_assets=sim2_assets, sim_env=sim2_env, tactic='VAA_aggressive')

        """
        ====================================
                Reference: Static AA
        ====================================
        """
        def set_simenv(asset_list:dict, capital:int, start_date:str, end_date:str):
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

        sim3_assets = {'DANTE':'DANTE'}
        sim3_env    = set_simenv(asset_list=sim3_assets,capital=10_000_000,start_date=start_date,end_date=end_date)
        saa = StaticAA().Run(sim_assets=sim3_assets, sim_env=sim3_env)

        if 0: #Plot
            plt.figure(figsize=[16,10])
            plt.semilogy(daa1.trade_log['Capital'], label="Dual Momentum")
            plt.semilogy(daa2.trade_log['Capital'], label="VAA")
            plt.semilogy(saa.trade_log['Capital'],  label="%s AW4/11"%(list(sim3_assets.keys())[0]))
            
            avg_c = daa1.trade_log['Capital']  +  daa2.trade_log['Capital'] +saa.trade_log['Capital'] #
            avg_c = avg_c/3
            plt.semilogy(avg_c,label='avg')
            plt.legend()
            #plt.show()


            plt.figure(figsize=[16,10])
            plt.plot(daa1.trade_log['MDD'], label="Dual Momentum")
            plt.plot(daa2.trade_log['MDD'], label="VAA")
            plt.plot(saa.trade_log['MDD'],  label="%s AW4/11"%(list(sim3_assets.keys())[0]))

            avg_m = daa1.trade_log['MDD']  + saa.trade_log['MDD'] + daa2.trade_log['MDD']#
            avg_m = avg_m/3
            plt.plot(avg_m, label='avg')
            plt.legend()
            #plt.show()
