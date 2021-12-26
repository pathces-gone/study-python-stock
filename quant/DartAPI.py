import numpy as np
import dart_fss as dart
import pandas as pd
import requests
import os

class DartAPI(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            ## Dart Attrib
            cls.api_key = os.environ.get('DART_KEY')
            assert cls.api_key is not  None, "Please set $DART_KEY env."
            cls.path    = os.path.join(os.path.dirname(__file__),'fsdata')
            cls.bgn_de  = '20200101'
            cls.end_de  = '20211231'
            cls.init_dart()
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True

    @classmethod
    def debug(cls):
        print(type(cls.fs))
        return 0

    @classmethod
    def init_dart(cls):
        dart.set_api_key(api_key=cls.api_key)
        cls.corp_list = dart.get_corp_list()

    @classmethod
    def get_item(cls, name:str):
        cls.curr_item = cls.corp_list.find_by_corp_name(name, exactly=True)[0]
        print(cls.curr_item)
        if cls.curr_item is not None:
            cls.name = name
        ''' fss.extract_fs()
          bgn_de = 시작일
          end_de = 끝
          fs_tp = ‘bs’ 재무상태표, ‘is’ 손익계산서, ‘cis’ 포괄손익계산서, ‘cf’ 현금흐름표
          report_tp = 'annual','quarter','half'
        '''    
        cls.fs = cls.curr_item.extract_fs(
          bgn_de=cls.bgn_de,
          end_de=cls.end_de,
          report_tp=['quarter','annual','half']
          )
        return cls.fs

    @classmethod
    def save(cls):
        file_='fs_%s.xlsx'%(cls.name)
        cls.fs.save(file_,cls.path)


class StockDataGroup(object):
  def __new__(cls, *args, **kwargs):
    if not hasattr(cls, "_instance"):
      cls._instance = super().__new__(cls)
      cls.semaphore = False
    return cls._instance

  def __init__(self):
    cls = type(self)
    if not hasattr(cls, "_init"):
      cls._init = True

  @classmethod
  def download(cls, corp_list):
    if cls.semaphore == False:
      for corp in corp_list:
        DartAPI().get_item(corp)
        DartAPI().save()
    cls.semaphore = True

if __name__ == '__main__':
  corp_list = ['카카오게임즈']#['서울옥션', '삼성전자', '카카오게임즈', '해성디에스', '이녹스첨단소재']
  StockDataGroup().download(corp_list)
