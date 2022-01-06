import yaml
import os
import numpy as np


class ETF(object):
  """ Return ETF
    ETF object
  """
  def __init__(self, name:str, index:str='gold'):
    self.name  =name
    self.index =index
  def get_price(self):
    price = 30000 #parsing
    return price



class Portpolio(object):
  """ Return Portpolio
    Portpolio Node (ETF chain)
  """
  def __init__(self, name):
    self.name = name

  @staticmethod
  def get_yaml(index:str)->list:
    yaml_file_path = os.path.join(os.path.dirname(__file__))
    with open(os.path.join(yaml_file_path, '%s.yaml'%index)) as f:
      conf = yaml.load(f, Loader=yaml.FullLoader)
    return conf

  def get_etf(self):
    name = self.name
    yaml = Portpolio.get_yaml(name)

    etfs = np.array([])
    cmds = np.array([], np.int32)
    ratios = np.array([], np.float32)
    for i,label in enumerate(yaml[name].values()):
      for sub_label in label:
        etfs   = np.append(etfs, sub_label['etf'])
        ratios = np.append(ratios,sub_label['ratio'])
        cmds = np.append(cmds, i)
    assert np.sum(ratios) == 100, ""

    portpolio = []
    for i,etf in enumerate(etfs):
      tmp = list(yaml[name].keys())
      portpolio.append( ETF(name=etf, index= tmp[cmds[i]]))
    return [portpolio, ratios]


class Simulation(object):
  """ Return Simulation
    Simulation Root node of Portpolio (ETF chain)
  """
  def __init__(self, portpolio:Portpolio, capital:int):
    self.portpolio = portpolio
    self.capital = capital

  def run(self):
    capital = self.capital
    etfs,ratios = self.portpolio.get_etf()
    budgets = (ratios*0.01)*capital
    prices  = [etf.get_price() for etf in etfs]

    qtys = np.array([],np.int32)
    for i,etf in enumerate(etfs):
      qtys = np.append(qtys, int(budgets[i]/prices[i]))

    print('Run - %s'%self.portpolio.name)


    print("%30s | %20s : %10s %10s %10s"%('index','name','budget', 'price', 'qty'))
    print('-'*100)
    for i,etf in enumerate(etfs):
      print("%30s | %20s :  %10d %10d %10d"%(etf.index,etf.name,budgets[i],prices[i],qtys[i]) )

if __name__ == '__main__':
  gvaa = Portpolio('gvaa')
  Simulation(portpolio = gvaa, capital= 100_000_00).run()

