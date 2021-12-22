

import backtesting
import pandas as pd

import sys, os
sys.path.append(os.path.join('..',os.path.dirname(__file__),'..','quant'))
from . import StockPrice

def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()