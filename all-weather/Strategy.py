import os
from ETF import ETF
import numpy as np
import datetime
import ETFUtils

class Strategy(object):
    @staticmethod
    def retry(df,date):
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

        SELL_QTY = 20
        BUY_QTY = 5

        if v1 < v2:
            commend   = 'SELL'
            update_qty= SELL_QTY
        elif v1 >= v2:
            commend   = 'BUY'
            update_qty= BUY_QTY
        else:
            commend = 'HOLD'
            update_qty= 0

        return [commend, update_qty]

    @staticmethod
    def abs_momentum2(etf:ETF, date:str):
        """
            모멘텀기준 12개월 전 가격 (추세추종 돌파매매)
            Trades/Year=1.2
        """
        momentum = 90
        close = etf.price_df[['Date','Close']]
        pivot = ETFUtils.get_prev_date(date,days=momentum)

        v1,today = Strategy.retry(df=close, date=date)
        v2,pivot = Strategy.retry(df=close, date=pivot)
        return Strategy.compare(v1=v1,v2=v2)

    @staticmethod
    def abs_momentum(etf:ETF, date:str):
        """
            300일 이동평균선
        """
        window_size =300
        
        close = etf.price_df[['Date','Close']]
        avg = close['Close'].rolling(window=window_size).mean()
        close = close.assign(avg=avg.values)

        today = date.strftime('%Y-%m-%d')
        index = close.loc[close['Date'] == today]

        v1 = index['Close'].values
        v2 = index['avg'].values

        return Strategy.compare(v1=v1,v2=v2)

    @staticmethod
    def dual_momentum(etf:ETF):
        commend   = 'SELL'
        update_qty= 10
        return [commend, update_qty]