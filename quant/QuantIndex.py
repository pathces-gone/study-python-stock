import numpy as np
import types

class QuantIndex:
  def __init__(self, comment:str, f:types.LambdaType, *params):
    self.comment= comment
    _params = params[0]
    num = len(_params)
    if num == 1:
      ret = f(_params[0])
    elif num == 2:
      ret = f(_params[0],_params[1])
    elif num == 3:
      ret = f(_params[0],_params[1],_params[2])
    else:
      ret = 0
    self.ret = ret
  def get_score(self):
    return self.ret 
  def whoami(self):
    print(self.comment)

class StatementIndexTable:
  def __init__(self):
    self.contents = {"per":0, "pbr":0, "pcr":0, "psr":0, "gp/a":0, "roa":0, "ev":0, "ebit":0}
    self.keys = self.contents.keys()

class QuantIndexTable:
  def __init__(self):
    self.contents = {"mmd":0, "sharp_ratio":0}
    self.keys = self.contents.keys()


if __name__ == '__main__':
  mmd = QuantIndex("mmd@min/max-1", lambda x,y: np.abs(x/y-1), [277.37,1145.66])
  print(mmd.get_score())