import os
from ETF import ETF
import numpy as np
import datetime
import ETFUtils

class Strategy(object):
    @staticmethod
    def retry(df,date:datetime):
        """ Return [v1,date]

        """
        RETRY = 14
        today = date
        for retry in range(RETRY):
            v1 = df.loc[df['Date']==today.strftime('%Y-%m-%d')]['Close'].values
            if len(v1)==0:
                today = ETFUtils.get_next_date(today)
                v1 = df.loc[df['Date']==today]['Close'].values
            else:
                break
        return [v1, today]

    @staticmethod
    def compare(v1,v2):
        """ Return [CMD, QTY]
            v1 < v2 :SELL
            v2 < v1 :BUY
        """
        THRESHOLD_SELL, THRESHOLD_BUY = [0.0, 0.0]

        commend = 'BUY'
        if v1 < v2:
          if (v2-v1)/v2 > THRESHOLD_SELL:
            commend   = 'SELL'
        elif v1 >= v2:
          if (v1-v2)/v2 >= THRESHOLD_BUY:
            commend   = 'BUY'
        else:
          pass
        return commend

    @staticmethod
    def abs_momentum(etf:ETF, date:datetime):
        """
            모멘텀기준 3|6|9|12개월 전 가격 (추세추종 돌파매매)
            Trades/Year=1.2
        """
        momentum = 90#180
        close = etf.price_df[['Date','Close']]
        pivot = ETFUtils.get_prev_date(date,days=momentum)

        v1,today = Strategy.retry(df=close, date=date)
        v2,pivot = Strategy.retry(df=close, date=pivot)
        return Strategy.compare(v1=v1,v2=v2)

    @staticmethod
    def abs_momentum2(etf:ETF, date:datetime):
        """
          Todo: Portpolio를 받아서 etf의 순위를 매김 Top3 & 12개월 이평선 위의 종목 매수?
        """
        window_size =224
        mavg  = etf.get_mavg(criteria='Low', window=window_size)
        close = etf.price_df[['Date', 'Close']]
        close = close.assign(mavg=mavg.values)

        #today = date.strftime('%Y-%m-%d')
        index = close.loc[close['Date'] == date]

        v1 = index['Close'].values
        v2 = index['mavg'].values
        return Strategy.compare(v1=v1,v2=v2)

    @staticmethod
    def dual_momentum(etf:ETF):
        commend   = 'SELL'
        update_qty= 10
        return [commend, update_qty]