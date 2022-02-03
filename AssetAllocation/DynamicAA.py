import numpy as np
import yaml, os, datetime
from ETF import ETF
from Portpolio import Portpolio
from Simulation import Simulation, SimEnvironment


class Stratgy(object):
    @staticmethod
    def get_compound_growth_rate(asset_group_name:str, today:datetime):
        """ Return
          [CMGR, CAGR]
        """
        def set_simenv(asset_group_name:str, today:datetime, interval:int):
            path = os.path.join('yaml','DynamicAA')
            if not os.path.exists(path):
                os.mkdir(path)
            asset_group_name = os.path.join('DynamicAA',asset_group_name)
            env = SimEnvironment()
            env.start_capital_krw, env.portpolio_name = [10_000_000 ,asset_group_name]

            prev_date = today - datetime.timedelta(days=interval)
            env.start_date, env.end_date = [prev_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')]
            env.reblancing_rule='B&H'
            asset_group = Portpolio(name=asset_group_name)
            return env, asset_group

        simenv, asset_group = set_simenv(asset_group_name, today, interval=365)
        sim1 = Simulation(portpolio=asset_group, env=simenv).Run()
        return [sim1.get_cmgr(), sim1.get_cagr()]

    @staticmethod
    def abs_momentum(asset_group:list, today:datetime):
        """ Return [[crit_cmgr], [crit_cagr]]
          CMGR or CAGR > 0 or not
        """
        HOLD = True
        SELL = False
        crit_cmgr = []
        crit_cagr = []
        for asset in asset_group:
            _cmgr, _cagr = Stratgy.get_compound_growth_rate(asset, today)
            if _cmgr > 0:
                crit_cmgr.append(HOLD)
            else:
                crit_cmgr.append(SELL)

            if _cagr > 0:
                crit_cagr.append(HOLD)
            else:
                crit_cagr.append(SELL)
        return crit_cmgr, crit_cagr

    @staticmethod
    def relative_momentum(asset_group:list, today:datetime):
        """ Return [crit_cmgr, crit_cagr]
        """
        asset1_cmgr, asset1_cagr = Stratgy.get_compound_growth_rate(asset_group[0], today)
        asset2_cmgr, asset2_cagr = Stratgy.get_compound_growth_rate(asset_group[1], today)
        crit_cmgr = asset_group[1] if (asset1_cmgr < asset2_cmgr) else asset_group[0]
        crit_cagr = asset_group[1] if (asset1_cagr < asset2_cagr) else asset_group[0]
        return [crit_cmgr, crit_cagr]


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
    def DualMomentum(today:str):
        """
          Binary selection -> ratio = 100%
        """
        assets = ['SPY','EFA']
        today = datetime.datetime.strptime(today,"%Y-%m-%d")

        rel = Stratgy.relative_momentum(asset_group = assets, today=today)
        ticker = rel[1] #CAGR

        abs = Stratgy.abs_momentum(assets, today=today) # rel에서 선택한 ticker의 abs가 False(SELL)라면 전체매도 
        if not abs[assets.index(ticker)]:
            print(ticker, 'SELL')
        else:
            print(ticker, 'BUY')
        
        return 0


class DynamicAA(Simulation):
    """
        일정 주기동안 포트폴리오를 돌리고
        리벨런싱 타이밍시
        1. Stratgy 클래스의 종목/비중 을 반환 받고
        2. Portpolio를 반환함
        3. 다시 Simulation
    """
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
        SlowTactical.DualMomentum('2022-02-02')
        pass

if __name__ == '__main__':
    daa = DynamicAA().Run()