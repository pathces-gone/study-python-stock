import numpy as np
from ETF import ETF
from Portpolio import Portpolio
from Simulation import Simulation


class Stratgy(object):
    """
        전략에 따라 종목을 받고 
        1. 모멘텀 계산 후 사야될 것
        2. 비중
        을 반환함
    """
    def __init__(self):
        pass
    def abs_momentum(self):
        pass
    def relative_momentum(self):
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
    def DualMomentum():
       pass


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
        self.onload_tactic = None
        for k,vs in self.Tactics.items():
            if tactic in vs:
                self.onload_tactic = {k:tactic}

        assert self.onload_tactic != None, 'tactic not found'
        print(self.onload_tactic)

    def Run(self):
        pass

if __name__ == '__main__':
    daa = DynamicAA()