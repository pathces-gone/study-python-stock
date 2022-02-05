import numpy as np
import yaml, os
import datetime
from dateutil import relativedelta

from ETF import ETF
from Portpolio import Portpolio
from Simulation import Simulation, SimEnvironment

BUY = True
SELL = False
DEBUG = False

class Momentum(object):
    def __init__(self, asset_yaml_names:list[str]):
        self.asset_yaml_names = asset_yaml_names
        self.portpolio_list = [Portpolio(os.path.join('DynamicAA',asset_yaml_name), is_usd_krw_need=False) for asset_yaml_name in asset_yaml_names]
        
    def abs_momentum(self, today:datetime):
        """ Return [*Momentums]
            각 자산을 특정일과 현재의 모멘텀을 리턴
        """
        def classic_momentum(assets:list[Portpolio], today:datetime, which:str):
            if 'ABS12':
                prev_date = today - relativedelta.relativedelta(months=12)
            elif 'ABS9':
                prev_date = today - relativedelta.relativedelta(months=9)
            elif 'ABS6':
                prev_date = today - relativedelta.relativedelta(months=6)
            elif 'ABS3':
                prev_date = today - relativedelta.relativedelta(months=3)
            else:
                prev_date = today

            etfs = np.array([])
            for asset in assets:
                _etfs,_ = asset.get_etf()
                etfs = np.append(etfs, _etfs)
            etfs = etfs.squeeze()
            prev_prices = np.array([etf.get_price(date=prev_date)[0] for etf in etfs])
            today_prices= np.array([etf.get_price(date=today)[0] for etf in etfs])
            
            #print(prev_date, today,prev_prices, today_prices, (prev_prices < today_prices))
            return (prev_prices < today_prices)

        portpolio_list = self.portpolio_list
        ret=classic_momentum(assets=portpolio_list,today=today,which='ABS12') 
        return ret

    
    def relative_momentum(self, today:datetime):
        """ Return [*Momentums]
            각 자산끼리 기간수익률을 비교한 모멘텀을 리턴
        """
        def classic_momentum(assets:list[Portpolio],today:datetime, months:int=1):
            prev_date = today - relativedelta.relativedelta(months=months)
            etfs = np.array([])
            for asset in assets:
                _etfs,_ = asset.get_etf()
                etfs = np.append(etfs, _etfs)
            etfs = etfs.squeeze()
            prev_prices = np.array([etf.get_price(date=prev_date)[0] for etf in etfs])
            today_prices= np.array([etf.get_price(date=today)[0] for etf in etfs])
            
            earn_ratio = (today_prices-prev_prices)/prev_prices*100
            index = np.argmax(earn_ratio)
            return etfs[index].code

        portpolio_list = self.portpolio_list
        ret = classic_momentum(assets=portpolio_list,today=today,months=12) 
        return ret
    
    def average_momentum(self):
        pass
    

class Stratgy(Momentum):
    def __init__(self):
        path = os.path.join('yaml','DynamicAA')
        if not os.path.exists(path):
            os.mkdir(path)

    @staticmethod
    def get_compound_growth_rate(asset_group_name:str, today:datetime, months:int):
        """ Return
          [CMGR, CAGR]
        """
        def set_simenv(asset_group_name:str, today:datetime, months:int):
            asset_group_name = os.path.join('DynamicAA',asset_group_name) 
            env = SimEnvironment()
            env.start_capital_krw, env.portpolio_name = [10_000_000 ,asset_group_name]
            prev_date = today - relativedelta.relativedelta(months=months)
            env.start_date, env.end_date = [prev_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')]
            env.reblancing_rule='B&H'
            asset_group = Portpolio(name=asset_group_name,is_usd_krw_need=False)
            return env, asset_group

        simenv, asset_group = set_simenv(asset_group_name, today, months=months)
        sim1 = Simulation(portpolio=asset_group, env=simenv).Run()
        return [sim1.get_cmgr(), sim1.get_cagr()]



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
    def __init__(self):
        Stratgy()
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
        momentum=Momentum(assets)
        
        rel = momentum.relative_momentum(today=today)
        ticker = rel
        abs = momentum.abs_momentum( today=today)
        #print(abs)
        
        ret = [ticker, SELL]
        if abs[assets.index(ticker)]:
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
            env.reblancing_rule='AW4/11'
            env.DO_CUT_OFF = True
            env.PRINT_TRADE_LOG = False
            asset_group = Portpolio(name=asset_group_name,is_usd_krw_need=False)
            return env, asset_group


        def set_simenv2(asset_group_name:str, capital:int, start_date:datetime, end_date:int):
            asset_group_name = os.path.join(asset_group_name)
            env = SimEnvironment()
            env.start_capital_krw, env.portpolio_name = [capital ,asset_group_name]
            env.start_date, env.end_date = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
            env.reblancing_rule='AW4/11'
            env.DO_CUT_OFF = False
            env.PRINT_TRADE_LOG = False
            env.reserve_per_period=6000000
            asset_group = Portpolio(name=asset_group_name,is_usd_krw_need=False)
            return env, asset_group

        """
        =========================================================================
                              Initial
        ========================================================================= 
        """
        init_capital = 10_000_000
        
        import ETFUtils
        market_open_date = ETFUtils.get_trading_date(ticker='SPY')

        def get_next_month(today:datetime):
            nextmonth = today + relativedelta.relativedelta(months=1)
            return nextmonth

        sim_start_date = datetime.datetime.strptime("2018-01-03","%Y-%m-%d")
        sim_end_date   = datetime.datetime.strptime("2022-01-28","%Y-%m-%d")
        today = sim_start_date
        capital = init_capital
        mmd = 0
        """
        =========================================================================
                              Strategy Start
        ========================================================================= 
        """
        tatic='DualMomentum'
        print("Tactic:\n%s %s - %d"%(tatic,sim_start_date ,init_capital))


        capital_list = np.array([])
        mmd_list = np.array([])
        _iter = 0
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
                    mmd     = np.min(sim_partial.mmd_history)
                    mmd_list=np.append(mmd_list,sim_partial.mmd_history)
                    capital_list = np.append(capital_list,sim_partial.capital_history)

                    f.write("%4s %s : %d  mmd=%.02f[%%]\n"%(ticker,today ,capital,mmd))
                    print("%4s %s : %d  mmd=%.02f[%%]"%(ticker,today ,capital,mmd))
                else:
                    days =len(market_open_date.loc[(today.strftime('%Y-%m-%d')<=market_open_date) & (market_open_date<partial_end_date.strftime('%Y-%m-%d'))])
                    print(days)
                    mmd_list     = np.append(mmd_list,    np.ones(days)*mmd_list[-1])
                    capital_list = np.append(capital_list,np.ones(days)*capital_list[-1])
                    today = partial_end_date
                    print("%s %s : %d"%('SELL',today ,capital))

                capital += 1000000
                _iter +=1
                if partial_end_date == sim_end_date:
                    break

            num_year = ( sim_end_date.year-sim_start_date.year)
            cagr = ((capital)/(init_capital+_iter*1000000))**(1/num_year)
            cagr = round((cagr-1)*100,2)
            print(_iter,cagr, np.min(mmd_list))

            """
            =========================================================================
                                  Strategy End & Reference
            ========================================================================= 
            """
            ticker = 'SingleStock'
            f.write("Reference:\n%s %s - %d\n"%(ticker,sim_start_date ,init_capital))
            print("Reference:\n%s %s - %d"%(ticker,sim_start_date ,init_capital))
            simenv, asset_group = set_simenv2(asset_group_name=ticker, capital=init_capital, start_date=sim_start_date, end_date=sim_end_date)
            sim_partial = Simulation(portpolio=asset_group, env=simenv).Run()
            capital = sim_partial.get_last_capital()
            today   = sim_partial.get_last_date()
            mmd     = np.min(sim_partial.mmd_history)
            f.write("%s %s : %d  mmd=%.02f[%%]\n"%(ticker,today ,capital,mmd))
            print("%s %s : %d  mmd=%.02f[%%]"%(ticker,today ,capital,mmd))


            num_year = ( sim_end_date.year-sim_start_date.year)
            cagr = ((capital)/(init_capital+_iter*1000000))**(1/num_year)
            cagr = round((cagr-1)*100,2)
            print(_iter,cagr, np.min(mmd_list))

            import matplotlib.pyplot as plt
            plt.plot(capital_list) 
            plt.plot(sim_partial.capital_history)
            plt.show()

            plt.plot(mmd_list)
            plt.plot(sim_partial.mmd_history)
            plt.show()



if __name__ == '__main__':
    daa = DynamicAA().Run()