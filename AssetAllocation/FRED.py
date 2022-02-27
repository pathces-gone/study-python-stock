from fredapi import Fred
import os
import matplotlib.pyplot as plt


if __name__ == '__main__':
  start= "2005-01-03"
  end  = "2022-02-25"

  key = os.environ.get('FRED_KEY')
  fred = Fred(api_key=key)
  dgs10 = fred.get_series('DGS10',observation_start=start, observation_end=end)
  dgs2  = fred.get_series('DGS2',observation_start=start, observation_end=end)
  dgs10_2 = dgs10-dgs2

  print(dgs10, type(dgs10))

  # plt.plot(dgs10,label='dgs10')
  # #plt.plot(dgs2,label='dgs2')
  # #plt.plot(dgs10_2,label='spread')
  # plt.axhline(y=0)
  # plt.legend()
  # #plt.show()
  # #dgs10_2.to_csv('10_2_spread', index=False)
  # #

  # cpi = fred.get_series('CPIAUCSL')
  # plt.plot(cpi,label='cpi')
  # plt.show()

  # # tips = fred.get_series('DFII10')
  # # inflation = dgs2-tips
  # # plt.plot(inflation)
  # # plt.show()

  #  #cpi = fred.get_series('SP500')
  #  #plt.plot(cpi,label='SP500')
  #  #plt.show()