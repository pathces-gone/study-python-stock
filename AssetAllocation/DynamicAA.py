import numpy as np
import yaml, os
import datetime
from dateutil import relativedelta

from ETF import ETF
from Portpolio import Portpolio
from Simulation import Simulation, SimEnvironment

BUY = True
SELL = False
INDEX_CMGR = 0
INDEX_CAGR = 1
INDEX = INDEX_CMGR
DEBUG = False


class Stratgy(object):
    @staticmethod
    def get_compound_growth_rate(asset_group_name:str, today:datetime, months:int):
        """ Return
          [CMGR, CAGR]
        """
        def set_simenv(asset_group_name:str, today:datetime, months:int):
            path = os.path.join('yaml','DynamicAA')
            if not os.path.exists(path):
                os.mkdir(path)
            asset_group_name = os.path.join('DynamicAA',asset_group_name)
            env = SimEnvironment()
            env.start_capital_krw, env.portpolio_name = [10_000_000 ,asset_group_name]

            prev_date = today - relativedelta.relativedelta(months=months)
            env.start_date, env.end_date = [prev_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')]
            env.reblancing_rule='B&H'
            asset_group = Portpolio(name=asset_group_name)
            return env, asset_group

        simenv, asset_group = set_simenv(asset_group_name, today, months=months)
        sim1 = Simulation(portpolio=asset_group, env=simenv).Run()
        return [sim1.get_cmgr(), sim1.get_cagr()]

    @staticmethod
    def abs_momentum(asset_group:list, today:datetime):
        """ Return [[crit_cmgr], [crit_cagr]]
          CMGR or CAGR > 0 or not
        """
        crit_cmgr = []
        crit_cagr = []
        for asset in asset_group:
            _cmgr, _cagr = Stratgy.get_compound_growth_rate(asset, today, months=1)
            crit_cmgr.append(bool(_cmgr>-5))
            crit_cagr.append(bool(_cagr>-5))

        return crit_cmgr, crit_cagr

    @staticmethod
    def relative_momentum(asset_group:list, today:datetime):
        """ Return [ticker_cmgr, ticker_cagr]
        """
        asset1_cmgr, asset1_cagr = Stratgy.get_compound_growth_rate(asset_group[0], today, months=1)
        asset2_cmgr, asset2_cagr = Stratgy.get_compound_growth_rate(asset_group[1], today, months=1)
        ticker_cmgr = asset_group[1] if (asset1_cmgr < asset2_cmgr) else asset_group[0]
        ticker_cagr = asset_group[1] if (asset1_cagr < asset2_cagr) else asset_group[0]
        
        if DEBUG:
            print("%s: %.02f[%%] /  %s: %0.2f[%%]"%(asset_group[0], asset1_cmgr, asset_group[1], asset2_cmgr))
        return [ticker_cmgr, ticker_cagr]


class FastTactial(Stratgy):
    @staticmethod
    def items():
        ITEMS = ['VAA_aggressive']
        return {'FastTactial':ITEMS}

    @staticmethod
    def VAA_aggressive():
        pass

class PrimarilyPassive(Stratgy):
    @staticmethod
    def items():
        ITEMS = ['LAA']
        return {'PrimarilyPassive':ITEMS}
    
    @staticmethod
    def LAA():
        pass

class SlowTactical(Stratgy):
    @staticmethod
    def items():
        ITEMS = ['CompositeDualMomentum','DualMomentum']
        return {'SlowTatical':ITEMS}

    @staticmethod
    def CompositeDualMomentum():
        pass

    @staticmethod
    def DualMomentum(today:datetime):
        """
          Binary selection -> ratio = 100%
        """
        assets = ['SPY','EFA']

        rel = Stratgy.relative_momentum(asset_group = assets, today=today)
        ticker = rel[INDEX]
        ref = Stratgy.relative_momentum(asset_group = [ticker,'SHY'], today=today)
        ticker = ref[INDEX]

        assets = ['SPY','EFA','SHY']
        abs = Stratgy.abs_momentum(assets, today=today)
        if not abs[INDEX][assets.index(ticker)]:
            ret = [ticker, SELL]
        else:
            ret = [ticker, BUY]
        
        return ret


class DynamicAA(Simulation):
    def __init__(self):
        def flatten(_lst:list):
            dic = dict()
            for  _l in _lst:
                dic.update(_l)
            return dic

        self.Tactics = flatten([FastTactial.items(),PrimarilyPassive.items(),SlowTactical.items()])
        self.load_tactic('DualMomentum')
        pass

    def load_tactic(self, tactic:str='DualMomentum'):
        """  Return 
          'onload_tactic'
        """
        onload_tactic = None
        for k,vs in self.Tactics.items():
            if tactic in vs:
                onload_tactic = {k:tactic}

        assert onload_tactic != None, 'tactic not found'
        return onload_tactic



    def Run(self):
        def set_simenv(asset_group_name:str, capital:int, start_date:datetime, end_date:int):
            path = os.path.join('yaml','DynamicAA')
            if not os.path.exists(path):
                os.mkdir(path)
            asset_group_name = os.path.join('DynamicAA',asset_group_name)
            env = SimEnvironment()
            env.start_capital_krw, env.portpolio_name = [capital ,asset_group_name]
            env.start_date, env.end_date = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
            env.reblancing_rule='B&H'
            env.DO_CUT_OFF = True
            env.PRINT_TRADE_LOG = False
            asset_group = Portpolio(name=asset_group_name)
            return env, asset_group


        """
        =========================================================================
                              Initial
        ========================================================================= 
        """
        init_capital = 10_000_000

        def get_next_month(today:datetime):
            nextmonth = today + relativedelta.relativedelta(months=1)
            return nextmonth

        sim_start_date = datetime.datetime.strptime("2005-01-03","%Y-%m-%d")
        sim_end_date   = datetime.datetime.strptime("2022-01-28","%Y-%m-%d")
        today = sim_start_date
        capital = init_capital
        mmd = 0
        """
        =========================================================================
                              Strategy
        ========================================================================= 
        """
        tatic='DualMomentum'
        print("Tactic:\n%s %s - %d"%(tatic,sim_start_date ,init_capital))

        with open(os.path.join('sim-result','%s-%s-%s.txt'%(tatic,sim_start_date ,init_capital)),'w') as f:
            while 1:
                next_month = get_next_month(today=today)
                ticker, is_buy = SlowTactical.DualMomentum(today)
                partial_end_date = next_month if next_month < sim_end_date else sim_end_date
                if is_buy:
                    simenv, asset_group = set_simenv(asset_group_name=ticker, capital=capital, start_date=today, end_date=partial_end_date)
                    sim_partial = Simulation(portpolio=asset_group, env=simenv).Run()
                    capital = sim_partial.get_last_capital()
                    today   = sim_partial.get_last_date()
                    mmd     = sim_partial.mmd_history[-1]

                    f.write("%s %s : %d  mmd=%.02f[%%]\n"%(ticker,today ,capital,mmd))
                else:
                    today = partial_end_date
                    #print("%s %s : %d"%('SELL',today ,capital))

                if partial_end_date == sim_end_date:
                    break

            """
            =========================================================================
                                  Strategy
            ========================================================================= 
            """
            ticker = 'SPY'
            f.write("Reference:\n%s %s - %d\n"%(ticker,sim_start_date ,init_capital))
            print("Reference:\n%s %s - %d"%(ticker,sim_start_date ,init_capital))
            simenv, asset_group = set_simenv(asset_group_name=ticker, capital=init_capital, start_date=sim_start_date, end_date=sim_end_date)
            sim_partial = Simulation(portpolio=asset_group, env=simenv).Run()
            capital = sim_partial.get_last_capital()
            today   = sim_partial.get_last_date()
            mmd     = sim_partial.mmd_history[-1]
            f.write("%s %s : %d  mmd=%.02f[%%]\n"%(ticker,today ,capital,mmd))
            print("%s %s : %d  mmd=%.02f[%%]"%(ticker,today ,capital,mmd))

if __name__ == '__main__':
    daa = DynamicAA().Run()
