if __name__ == '__main__':
  from fredapi import Fred
  import os
  fred = Fred(api_key=os.environ.get('FRED_KEY'))
  dgs10 = fred.get_series('DGS10')
  dgs2  = fred.get_series('DGS2')
  dgs10_2 = dgs10-dgs2

  cpi = fred.get_series('CPIAUCSL')

  import matplotlib.pyplot as plt
  plt.plot(dgs10_2)
  plt.plot(cpi)