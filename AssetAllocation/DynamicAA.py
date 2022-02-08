import numpy as np
import yaml, os, types
import datetime
from dateutil import relativedelta

import ETFUtils
from ETF import ETF
from Portpolio import Portpolio
from Simulation import Simulation, SimEnvironment, SimResult
from StaticAA import StaticAA

BUY = True
SELL = False
DEBUG = False

class MomentumScore(object):
    @staticmethod
    def average_momentum_score(etfs:list[ETF],today:datetime):
        """ Return list[float]
            
        """
        momentums_for_month = np.zeros(len(etfs))
        for i in range(1,13,1):
            prev_date = today - relativedelta.relativedelta(months=i)
            prev_prices = np.array([etf.get_price(date=prev_date)[0] for etf in etfs])
            today_prices= np.array([etf.get_price(date=today)[0] for etf in etfs])

            compare = (prev_prices < today_prices)
            momentums_for_month = np.vstack((momentums_for_month,compare))

        momentums_for_month = momentums_for_month[0:].transpose()

        score = np.array([],np.float64)
        for i in range(len(etfs)):
            score = np.append(score, round(np.sum(momentums_for_month[i,:].astype(np.int32))/12, 3))

        return score

    @staticmethod
    def classic_momentum_score(etfs:list[ETF], today:datetime, months:int, score_func:types.LambdaType):
        """ Return list[float]
            lamda(x,y) where x=prev_prices, y=today_prices
        """
        prev_date = today - relativedelta.relativedelta(months=months)
        prev_prices = np.array([etf.get_price(date=prev_date)[0] for etf in etfs])
        today_prices= np.array([etf.get_price(date=today)[0] for etf in etfs])
        score = score_func(prev_prices, today_prices).astype(np.float32)
        return score

class Momentum(MomentumScore):
    def __init__(self, asset_yaml_names:list[str]):
        self.asset_yaml_names = asset_yaml_names
        self.portpolio_list = [Portpolio(os.path.join('DynamicAA',asset_yaml_name), is_usd_krw_need=False) for asset_yaml_name in asset_yaml_names]


    def abs_momentum(self, today:datetime):
        """ Return [*Momentums]
            각 자산을 특정일과 현재의 모멘텀을 리턴
        """
        portpolio_list = self.portpolio_list

        etfs = np.array([])
        for asset in portpolio_list:
            _etfs,_ = asset.get_etf()
            etfs = np.append(etfs, _etfs)
        etfs = etfs.squeeze()
        score = MomentumScore.classic_momentum_score(etfs=etfs,today=today, months=12, score_func=lambda x,y: x<y)
        return score.astype(bool)

    
    def relative_momentum(self, today:datetime):
        """ Return list[(ticker, ratio_score)]
            각 자산끼리 기간수익률을 비교한 모멘텀을 리턴
        """
        portpolio_list = self.portpolio_list

        etfs = np.array([])
        for asset in portpolio_list:
            _etfs,_ = asset.get_etf()
            etfs = np.append(etfs, _etfs)
        etfs = etfs.squeeze()

        score       = MomentumScore.classic_momentum_score(etfs=etfs,today=today, months=12, score_func=lambda x,y: (y-x)/x*100) 
        ratio_score = np.ones(len(etfs))
        #ratio_score = MomentumScore.average_momentum_score(etfs=etfs, today=today) 

        index = np.argmax(score)
        ticker   = etfs[index].code
        return [ticker, ratio_score]
    
    def average_momentum(self):
        pass
    


class Stratgy(Momentum):
    pass



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
        """ Return [ticker_index, BUY, ratio]
          Binary selection -> ratio = 100%

          * ORIGIANL:
            if SPY12 > BLI12:
                ret = max(SPY12, EFA12)
            else:
                ret = AGG

          * MODIFY:
            if SPY12<0 and EFA12<0:
              ret = AGG
            else:
              ret = max(SPY12, EFA12)

        """
        #assets = {'SPY':'219480','EFA':'195930'}
        #assets = {'SPY':'SPY','EFA':'EFA','SHY':'SHY'}
        #assets = {'SPY':'SPY','EFA':'EFA'}
        assets = {'SPY':'SPY','EFA':'EFA','AGG':'AGG'}
        assets_inv = {value: key for key, value in assets.items()}
        momentum=Momentum(list(assets.keys()))

        rel, ratio_score = momentum.relative_momentum(today=today)
        abs = momentum.abs_momentum( today=today)

        ticker = assets_inv.get(rel)
        index = list(assets.keys()).index(ticker)
        ratio = ratio_score[index]

        ret = [0,BUY,1]
        if abs[index]:
            ret = [index, BUY, ratio]

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

        path = os.path.join('yaml','DynamicAA')
        if not os.path.exists(path):
            os.mkdir(path)


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


    def Run(self, sim_assets:dict ,sim_env:SimEnvironment, tactic:str='DualMomentum'):
        """
          In:
            * assets
            * simenv
            * tactic
          Out: 
            * simout
        """
        path = os.path.join('yaml','DynamicAA')
        if not os.path.exists(path):
            os.mkdir(path)

        """
        =========================================================================
                              Initial
        ========================================================================= 
        """
        sim_assets_dict = sim_assets
        start_date = sim_env.start_date
        end_date   = sim_env.end_date

        init_capital = sim_env.start_capital_krw
        market_open_date = sim_env.market_open_date

        def get_next_month(today:datetime):
            nextmonth = today + relativedelta.relativedelta(days=7)#(months=1)
            return nextmonth

        sim_start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d")
        sim_end_date   = datetime.datetime.strptime(end_date,"%Y-%m-%d")
        today   = sim_start_date
        capital = sim_env.start_capital_krw
        mmd = 0

        if tactic == 'DualMomentum':
            tactic_func = SlowTactical.DualMomentum
        else:
            # TODO
            tactic_func = SlowTactical.DualMomentum

        """
        =========================================================================
                              Strategy Start
        ========================================================================= 
        """
        print("Tactic:\n%s %s - %d"%(tactic,sim_start_date ,init_capital))

        capital_list = np.array([])
        mmd_list = np.array([])
        _iter = 0
        additional_paid_in = 0

        with open(os.path.join('sim-result','%s-%s-%s.txt'%(tactic,sim_start_date ,init_capital)),'w') as f:
            while 1:
                next_month = get_next_month(today=today)
                ticker_index, is_buy, ratio = tactic_func(today)
                partial_end_date = next_month if next_month < sim_end_date else sim_end_date
  
                if is_buy:
                    input_capital             = round(ratio,4)*capital
                    sim_env.portpolio_index   = ticker_index
                    sim_env.start_capital_krw = input_capital
                    sim_env.start_date        = today.strftime('%Y-%m-%d')
                    sim_env.end_date          = partial_end_date.strftime('%Y-%m-%d')
                    sim_portpolio             = Portpolio(name=sim_env.portpolio_list[ticker_index], is_usd_krw_need=True)

                    sim_partial               = Simulation(portpolio=sim_portpolio, env=sim_env).Run()

                    capital      = sim_partial.get_last_capital() + (capital-input_capital)
                    today        = sim_partial.get_last_date()  + relativedelta.relativedelta(days=1)
                    mmd          = np.min(sim_partial.mmd_history)
                    mmd_list     = np.append(mmd_list, sim_partial.mmd_history)
                    capital_list = np.append(capital_list, sim_partial.capital_history + (capital-input_capital))

                    f.write("%4s %s : %d  mmd=%.02f[%%]\n"%(sim_env.portpolio_list[ticker_index],today ,capital,mmd))
                    print("%4s %s : %d  mmd=%.02f[%%]"%(sim_env.portpolio_list[ticker_index],today ,capital,mmd))
                else:
                    days = len(market_open_date.loc[(today.strftime('%Y-%m-%d')<=market_open_date) & (market_open_date<partial_end_date.strftime('%Y-%m-%d'))])
                    mmd_list     = np.append(mmd_list,    np.ones(days)*mmd_list[-1])
                    capital_list = np.append(capital_list,np.ones(days)*capital_list[-1])
                    today        = partial_end_date
                    print("%4s %s : %d"%('SELL',today ,capital))

                capital += additional_paid_in
                _iter +=1
                if partial_end_date == sim_end_date:
                    break

            num_year = ( sim_end_date.year-sim_start_date.year)
            cagr = 0
            if num_year > 0:
                cagr = ((capital)/(init_capital+_iter*additional_paid_in))**(1/num_year)
                cagr = round((cagr-1)*100,2)
            print('Simulation Done.\nITER: %d, CAGR: %4.02f[%%] MMD:%4.02f[%%]\n'%(_iter,cagr, np.min(mmd_list)))

            """
            =========================================================================
                                  Strategy End & Reference
            ========================================================================= 
            """

        sim_result = SimResult()
        sim_result.mmd_history = mmd_list
        sim_result.capital_history = capital_list
        sim_result.date_history = np.array([]) #TODO
        return sim_result



if __name__ == '__main__':
    """
    =====================================
              Dynamic AA
    =====================================
    """
    def set_simenv(asset_list:dict, capital:int, start_date:str, end_date:str):
        asset_names = asset_list.keys()
        asset_yamls = [os.path.join('DynamicAA',name) for name in asset_names] 

        env = SimEnvironment()
        env.portpolio_index = 0
        env.portpolio_list = asset_yamls
        env.start_capital_krw = capital
        env.start_date, env.end_date = [start_date, end_date]
        env.reblancing_rule='AW4/11'
        env.market_open_date = ETFUtils.get_trading_date(ticker='SPY')

        env.DO_CUT_OFF = False
        env.PRINT_TRADE_LOG = False
        env.FIXED_EXCHANGE_RATE = False
        return env

    sim1_assets = {'SPY':'SPY','EFA':'EFA','AGG':'AGG'}
    sim1_env    = set_simenv(asset_list=sim1_assets,capital=10_000_000,start_date="2014-08-01",end_date="2022-01-15")
    daa = DynamicAA().Run(sim_assets=sim1_assets, sim_env=sim1_env)

    """
    ====================================
            Reference: Static AA
    ====================================
    """
    if 1: 
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

        sim1_assets = {'GTAA-NON':'GTAA-NON'}
        sim1_env    = set_simenv(asset_list=sim1_assets,capital=10_000_000,start_date="2014-08-01",end_date="2022-01-15")
        saa = StaticAA().Run(sim_assets=sim1_assets, sim_env=sim1_env)


    """
    ====================================
      
    ====================================
    """
    if 1:
        import matplotlib.pyplot as plt

        plt.plot(daa.capital_history, label="Dual Momentum")
        plt.plot(saa.capital_history, label="GTAA AW4/11")
        plt.show()

        plt.plot(daa.mmd_history, label="Dual Momentum")
        plt.plot(saa.mmd_history, label="GTAA AW4/11")
        plt.show()