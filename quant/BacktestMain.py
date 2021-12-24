from os import stat
import pandas as pd
from backtesting import Backtest
from backtest import BacktestUtils,SMA

if __name__ == '__main__':
  stock = BacktestUtils.BacktestUtils.get_price(page=10)
  bt = Backtest(stock, SMA.SmaCross, cash=10_000_000, commission=.002)
  stats = bt.run()
  print(stats)
  bt.plot()