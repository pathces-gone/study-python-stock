import numpy as np
import yaml, os, types
import datetime
from dateutil import relativedelta
import pandas as pd

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
        COLUMN = ['Close']
        prev_date = today - relativedelta.relativedelta(months=months)
        prev_date = prev_date.strftime("%Y-%m-%d")
        today = today.strftime("%Y-%m-%d")

        etf_data_vec = pd.DataFrame([], columns=COLUMN)
        for etf in etfs:
          v1 = etf.price_df.loc[etf.price_df['Date']==today, COLUMN].reset_index(drop=True)
          v2 = etf.price_df.loc[etf.price_df['Date']==prev_date, COLUMN].reset_index(drop=True)
          vec = (v1-v2)/v2*100
          etf_data_vec = pd.concat([etf_data_vec, vec])
        max_idx = etf_data_vec.reset_index(drop=True)['Close'].apply(pd.to_numeric).idxmax()
        score = np.zeros(len(etfs))
        score[max_idx] = 1
        return score


    @staticmethod
    def vaa_momentum_score(etfs:list[ETF], today:datetime, months:int=None, score_func:types.LambdaType=None):
        """ Return list[float]
          모멘텀 스코어=(12×1개월 수익률)+(4×3개월 수익률)+(2×6개월 수익률)+(1×12개월 수익률)
        """
        momentums_for_month = np.zeros(len(etfs))
        pivot_month = [1,3,6,12]
        weight      = [12,4,2,1]

        COLUMN = ['Close']

        for i in pivot_month:
            prev_date = today - relativedelta.relativedelta(months=i)
            today_prices = [etf.price_df.loc[etf.price_df['Date']==today.strftime('%Y-%m-%d'), COLUMN].iloc[0,0]     for etf in etfs]
            prev_prices = [etf.price_df.loc[etf.price_df['Date']==prev_date.strftime('%Y-%m-%d'), COLUMN].iloc[0,0]  for etf in etfs]
            today_prices = np.array(today_prices, np.float64)
            prev_prices = np.array(prev_prices, np.float64)

            earn = (today_prices-prev_prices)/prev_prices*100
            momentums_for_month = np.vstack((momentums_for_month, earn))

        momentums_for_month = momentums_for_month[1:] # 4xetfs
        score = np.matmul(weight, momentums_for_month)# 1x4  4xetfs = 1xetfs
        return score


    @staticmethod
    def mvg_momentum_score(etfs:list[ETF], today:datetime, months:int=None, score_func:types.LambdaType=None):
        """ Return list[float]
        """
        today = today.strftime('%Y-%m-%d')

        etf_data_vec = pd.DataFrame([], columns=['Close','mvg224'])
        for etf in etfs:
          vec = etf.price_df.loc[etf.price_df['Date']==today, ['Close','mvg224']]
          etf_data_vec = pd.concat([etf_data_vec,vec])

        etf_data_vec['score'] = etf_data_vec.iloc[:,0] >= etf_data_vec.iloc[:,1]
        score = etf_data_vec['score'].to_list()
        return score


    @staticmethod
    def abs_momentum_score(etfs:list[ETF], today:datetime, months:int=12, score_func:types.LambdaType=None):
        """ Return list[float]
        """
        prev_date = today - relativedelta.relativedelta(months=months)
        prev_date = prev_date.strftime('%Y-%m-%d')
        today = today.strftime('%Y-%m-%d')

        etf_data_vec = pd.DataFrame([], columns=['Close','mvg224'])
        for etf in etfs:
          v1 = etf.price_df.loc[etf.price_df['Date']==today, ['Close','mvg224']].reset_index(drop=True)
          v2 = etf.price_df.loc[etf.price_df['Date']==prev_date, ['Close','mvg224']].reset_index(drop=True)
          vec =(v1-v2)/v2*100
          etf_data_vec = pd.concat([etf_data_vec,vec])

        etf_data_vec['score'] = etf_data_vec.iloc[:,1] > 1.1  #224
        #print(etf_data_vec)
        score = etf_data_vec['score'].to_list()
        return score


class Momentum(MomentumScore):
    def __init__(self, asset_yaml_names:list[str]):
        self.asset_yaml_names = asset_yaml_names
        self.portpolio_list = [Portpolio(os.path.join('DynamicAA',asset_yaml_name), is_usd_krw_need=False) for asset_yaml_name in asset_yaml_names]


    def abs_momentum(self, today:datetime):
        """ Return [*Momentums]
            은행금리보다 낮을경우 
        """
        portpolio_list = self.portpolio_list

        etfs = np.array([])
        for asset in portpolio_list:
            _etfs,_ = asset.get_etf()
            etfs = np.append(etfs, _etfs)
        etfs = etfs.squeeze()
        #score = MomentumScore.vaa_momentum_score(etfs=etfs,today=today)
        #score = score > 0
        #score = MomentumScore.mvg_momentum_score(etfs=etfs,today=today)
        score = MomentumScore.abs_momentum_score(etfs=etfs,today=today)
        return score

    
    def relative_momentum(self, today:datetime):
        """ Return list[(ticker, ratio_score)]

        """
        portpolio_list = self.portpolio_list

        etfs = np.array([])
        for asset in portpolio_list:
            _etfs,_ = asset.get_etf()
            etfs = np.append(etfs, _etfs)
        etfs = etfs.squeeze()

        #score       = MomentumScore.classic_momentum_score(etfs=etfs,today=today, months=12, score_func=lambda x,y: (y-x)/x*100) 
        score = MomentumScore.classic_momentum_score(etfs=etfs,today=today, months=12, score_func=None)
        #score = MomentumScore.vaa_momentum_score(etfs=etfs,today=today)
        ratio_score = np.ones(len(etfs))

        index = np.argmax(score)
        ticker   = etfs[index].code
        return [ticker, ratio_score]
    
    def average_momentum(self):
        pass
    
    def vaa_momentum(self, today:datetime):
        portpolio_list = self.portpolio_list

        etfs = np.array([])
        for asset in portpolio_list:
            _etfs,_ = asset.get_etf()
            etfs = np.append(etfs, _etfs)
        etfs = etfs.squeeze()

        score       = MomentumScore.vaa_momentum_score(etfs=etfs,today=today, months=None, score_func=None) 
        index = np.argmax(score)
        ticker   = etfs[index].code
        return [ticker, score]


class Stratgy(Momentum):
    pass



class FastTactial(Stratgy):
    @staticmethod
    def items():
        ITEMS = ['VAA_aggressive']
        return {'FastTactial':ITEMS}

    @staticmethod
    def VAA_aggressive(assets:dict, today:datetime):
        """ Return [ticker_index, BUY, ratio]
          Aggressive Assets  : SPY, EFA, EEM, AGG
          Conservative Assets: LQD, IEF, SHY

          Momentum Score: 1, 3, 6, 12 months
            모멘텀 스코어=(12×1개월 수익률)+(4×3개월 수익률)+(2×6개월 수익률)+(1×12개월 수익률)

          if Aggressive가 모두 모멘텀스코어 0 이상일 경우 
            -> 가장 점수가 높은 aggressive asset에 투자
          else
            -> 모멘텀 스코어가 가장 높은 Conservative Assets에 투자
        """
        agg_list = list(assets['Aggressive'].keys())
        con_list = list(assets['Conservative'].keys())
        agg = Momentum(agg_list)
        con = Momentum(con_list)

        agg_ticker, agg_score = agg.vaa_momentum(today=today)
        if np.min(agg_score) < 0:
            con_ticker, con_score = con.vaa_momentum(today=today)
            which_group = 'Conservative'
            which_group_index = len(con_list)
            ticker = con_ticker
        else:
            which_group = 'Aggressive'
            which_group_index = 0
            ticker = agg_ticker

        index = list(assets[which_group].keys()).index(ticker)
       # which_group_index = list(assets.keys()).index(which_group) * assets[which_group]
        ret = [which_group_index,index,BUY,1]
        return ret

class PrimarilyPassive(Stratgy):
    @staticmethod
    def items():
        ITEMS = ['LAA','MyQQQ']
        return {'PrimarilyPassive':ITEMS}

    @staticmethod
    def MyQQQ():
        """
          AW4/11로 가다가
          카나리아가 울때 QQQ를 파는 전략
        """
        pass

    @staticmethod
    def LAA():
        """ Return
          LAA 전략은 영구 포트폴리오처럼 주식, 채권, 금 비중을 4분의 1로 똑같이 한다.
          단, 경기가 안 좋을 때만 현금 비중을 그대로 두고, 경기가 좋을 때는 현금을 나스닥에 투자한다.
          평상시에는 주식 50%, 금과 채권 각각 25% 비중이고 경기가 안 좋을 때는 현금, 주식, 금, 채권 비중이 각각 25%가 된다.

          “실업률이 최근 10개월 평균보다 위라면 경제가 안 좋다고 가정한다. 
          예를 들어 미국 실업률이 보통 3~4%였는데 지난해 4월 15%까지 상승했다. 
          이럴 때를 경기가 안 좋다는 신호로 본다.”

          > https://weekly.donga.com/BestClick/3/all/11/3102871/1
        """
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
    def DualMomentum(assets:dict, today:datetime):
        """ Return [which_group_index, ticker_index, BUY, ratio]
          Benchmark score: https://www.turingtrader.com/antonacci-dual-momentum/
        """
        agg_list = list(assets['Aggressive'].keys())
        con_list = list(assets['Conservative'].keys())
        agg = Momentum(agg_list)
        con = Momentum(con_list)

        rel, ratio_score = agg.relative_momentum(today=today) # [ticker, ratio_score]
        abs = agg.abs_momentum( today=today)
        agg_index = agg_list.index(rel)
        ratio = ratio_score[agg_index]


        ret = [len(agg_list),0,BUY,1]
        if abs[agg_index]:
            ret = [0, agg_index, BUY, ratio]

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
            nextmonth = today + relativedelta.relativedelta(months=1) - relativedelta.relativedelta(days=1)
            return nextmonth

        def get_next_day(today:datetime):
            nextday = today + relativedelta.relativedelta(days=14) - relativedelta.relativedelta(days=1)
            return nextday

        sim_start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d")
        sim_end_date   = datetime.datetime.strptime(end_date,"%Y-%m-%d")
        today   = sim_start_date
        capital = sim_env.start_capital_krw
        mdd = 0

        if tactic == 'DualMomentum':
            tactic_func = SlowTactical.DualMomentum
            next_date_func = get_next_month
        elif tactic == 'VAA_aggressive':
            tactic_func = FastTactial.VAA_aggressive
            next_date_func = get_next_month #get_next_day
        else:
            # TODO
            tactic_func = SlowTactical.DualMomentum
            next_date_func = get_next_month

        """
        =========================================================================
                              Strategy Start
        ========================================================================= 
        """
        print("Tactic:\n%s %s - %d"%(tactic,sim_start_date ,init_capital))

        capital_list = np.array([])
        mdd_list = np.array([])
        _iter = 0
        additional_paid_in = 0
        trade_log = pd.DataFrame([],columns=self.trade_log_columns)

        while 1:
            next_month = next_date_func(today=today)
            which_group, ticker_index, is_buy, ratio = tactic_func(sim_assets_dict, today)
            partial_end_date = next_month if next_month < sim_end_date else sim_end_date

            input_capital             = round(ratio,4)*capital
            sim_env.portpolio_index   = ticker_index
            sim_env.start_capital_krw = input_capital
            sim_env.start_date        = today.strftime('%Y-%m-%d')
            sim_env.end_date          = partial_end_date.strftime('%Y-%m-%d')
            sim_portpolio             = Portpolio(name=sim_env.portpolio_list[which_group+ticker_index], is_usd_krw_need=True)
  
            if is_buy:
                sim_env.reblancing_rule   = 'B&H'
                sim_partial               = Simulation(portpolio=sim_portpolio, env=sim_env).Run()
            else:
                sim_env.reblancing_rule   = 'Nothing'
                sim_partial               = Simulation(portpolio=sim_portpolio, env=sim_env).Run()

            capital      = sim_partial.get_last_capital() + (capital-input_capital)
            today        = sim_partial.get_last_date()  + relativedelta.relativedelta(days=1)
            mdd          = sim_partial.trade_log['MDD'].min()
            trade_log    = pd.concat([trade_log, sim_partial.trade_log])
            if is_buy:
              print("%14s %s : %d  mdd=%.02f[%%]"%(sim_env.portpolio_list[which_group+ticker_index],today ,capital,mdd))
            else:
              print("%14s %s : %d  mdd=%.02f[%%]"%('Cutoff',today ,capital,0))
            capital += additional_paid_in
            _iter +=1
            if partial_end_date == sim_end_date:
                break

        """
        =========================================================================
                              Strategy End & Reference
        ========================================================================= 
        """
        def post_process(df):
          idx = pd.date_range(df['Date'].min(),df['Date'].max())
          s = df.set_index('Date')
          s = s.reindex(idx, fill_value=0)
          s = s.reset_index().rename(columns={"index": "Date"})
          for i in s.index:
            if s.iloc[i,-1]==False:
              s.iloc[i,-1] = False
          return s

        sim_result = SimResult()
        sim_result.sim_name = tactic
        sim_result.trade_log = post_process(trade_log)
        #print(sim_result.trade_log)
        num_year = (sim_end_date.year-sim_start_date.year)
        cagr = 0
        if num_year > 0:
            cagr = ((capital)/(init_capital+_iter*additional_paid_in))**(1/num_year)
            cagr = round((cagr-1)*100,2)

        print('Simulation Done.\nITER: %d, CAGR: %4.02f[%%] MMD:%4.02f[%%]\n'%(_iter,cagr, sim_result.trade_log['MDD'].min()))
        return sim_result



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
        env.FIXED_EXCHANGE_RATE = True
        return env
  
    start_date= "2017-02-01"
    end_date  = "2022-02-02"

    ##sim1_assets = {'Aggressive':{'SPY':'SPY','EFA':'EFA','QQQ':'QQQ'},'Conservative':{'AGG':'AGG'}}
    sim1_assets = {'Aggressive':{'SPY':'SPY','EFA':'EFA','EEM':'EEM','AGG':'AGG'},'Conservative':{'LQD':'LQD','IEF':'IEF','SHY':'SHY'}}
    sim1_env    = set_simenv(asset_list=sim1_assets,capital=10_000_000,start_date=start_date,end_date=end_date)
    #daa1 = DynamicAA().Run(sim_assets=sim1_assets, sim_env=sim1_env, tactic='DualMomentum')
    daa1 = DynamicAA().Run(sim_assets=sim1_assets, sim_env=sim1_env, tactic='VAA_aggressive')