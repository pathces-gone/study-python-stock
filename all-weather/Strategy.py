import os
from ETF import ETF
import numpy as np
import datetime

class Strategy(object):
    @staticmethod
    def abs_momentum(etf:ETF, date:str):
        window_size =300
        
        close = etf.price_df[['Date','Close']]
        avg = close['Close'].rolling(window=window_size).mean()
        close = close.assign(avg=avg.values)

        today = date.strftime('%Y-%m-%d')
        index = close.loc[close['Date'] == today]

        v1 = index['Close'].values
        v2 = index['avg'].values

        if v1 < v2:
            commend   = 'SELL'
            update_qty= 10
        elif v1 >= v2:
            commend   = 'BUY'
            update_qty= 10
        else:
            commend = 'HOLD'
            update_qty= 0
        return [commend, update_qty]

    @staticmethod
    def dual_momentum(etf:ETF):
        commend   = 'SELL'
        update_qty= 10
        return [commend, update_qty]