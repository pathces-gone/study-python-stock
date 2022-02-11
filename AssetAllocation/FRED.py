if __name__ == '__main__':
  from fredapi import Fred
  import os
  fred = Fred(api_key=os.environ.get('FRED_KEY'))
  data = fred.get_series('SP500')

  print(data)