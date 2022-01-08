

import os

class Strategy(object):
    @staticmethod
    def abs_momentum():
        commend   = 'SELL'
        update_qty= 10
        return [commend, update_qty]

    @staticmethod
    def dual_momentum():
        commend   = 'SELL'
        update_qty= 10
        return [commend, update_qty]