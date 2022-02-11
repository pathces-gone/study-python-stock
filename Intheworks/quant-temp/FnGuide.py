from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as bs
import pandas as pd
import os, time
from StockPrice import StockPrice
from Manager import DEBUG_ELAPSED_TIME

class FnGuide(object):
  @staticmethod
  def name_to_code(name:str):
    path = os.path.join(os.path.dirname(__file__),'fsdata','listed_corporation.csv')
    code_df = pd.read_csv(path)

    if code_df.empty:
      StockPrice(item_name='',page=10).download_all_listed_corporation_as_csv()    
      code_df = pd.read_csv(path)

    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
    code_df = code_df[['회사명', '종목코드']]
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
   
    ret = code_df.loc[code_df['name'] == name]['code'].to_list()
    return str(ret[0]) 

  @staticmethod
  def get_html(_code:str=None,_name:str=None, _page:int=0):
    if DEBUG_ELAPSED_TIME:
      start_time = time.time()

    if _code == None:
      if _name == None:
        return None
      else:
        code = FnGuide.name_to_code(_name)

    url=[]
    url.append("https://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A" + code + "&cID=&MenuYn=Y&ReportGB=&NewMenuID=103&stkGb=701")
    url.append("https://comp.fnguide.com/SVO2/ASP/SVD_FinanceRatio.asp?pGB=1&gicode=A" + code + "&cID=&MenuYn=Y&ReportGB=&NewMenuID=104&stkGb=701")
    url.append("https://comp.fnguide.com/SVO2/ASP/SVD_Invest.asp?pGB=1&gicode=A"+ code + "&cID=&MenuYn=Y&ReportGB=&NewMenuID=105&stkGb=701")
    url.append("https://comp.fnguide.com/SVO2/ASP/SVD_Consensus.asp?pGB=1&gicode=A" + code +"&cID=&MenuYn=Y&ReportGB=&NewMenuID=108&stkGb=701")
    
    if _page > len(url):
      return None
    url = url[_page]

    try:
      req = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
      html_text = urlopen(req).read()
    except AttributeError as e :
      return None
    
    if DEBUG_ELAPSED_TIME:
      print("FnGuide get_html Elapsed Time : %.2f"%round(time.time()-start_time,2))

    return html_text, url

  @staticmethod
  def get_multiples_prev_quater(code:str=None, name:str=None, item:str=None):
    """ Return float
      Multiples: per, psr, pcr, ev/ebit, pbr
    """
    html_text, url = FnGuide.get_html(code,name, 2)
    assert html_text != None, "Fail to get_html." 
        
    soup = bs(html_text, 'lxml')
    d = soup.find_all(text=item)
    if(d == None):
      return None
    f1 = (d[-1].find_all_next(class_="cle r tdbg_y",limit=3))
    v = [v.text for v in f1]
    v= [v[1],v[2]]
    ret = round(float(v[0].replace(',',''))/float(v[1].replace(',','')),2)
    return ret 

  @staticmethod
  def get_data(_code:str=None, _name:str=None, _page:int=0, _item:str=None, _n=4, _term="annual"):
    """
    :param _code: 종목코드
    :param _page: 데이터 종류 (0 : 재무제표, 1 : 재무비율, 2: 투자지표)
    :param _item: html_text file에서 원하는 계정의 데이터를 가져온다.
    :param _n: 최근 몇 개의 데이터를 가져 올것인지
    :param _term: annual : 연간재무, quarter : 분기재무    
    :return: item의 과거 데이터
    """
    
    html_text, url = FnGuide.get_html(_code,_name, _page)
    assert html_text != None, "Fail to get_html." 
    
    soup = bs(html_text, 'lxml')
    d = soup.find_all(text=_item)

    if(len(d)==0) :
      return None

    nlimit =3 if _page==0 else 4

    if _n > nlimit :
      return None

    if _term == "annual":
      if _page == 0:
        d_ = d[0].find_all_next(class_="r",limit=nlimit)
      else:
        d_ = d[-1].find_all_next(class_="r",limit=nlimit)

    elif _term =="quarter":
      if _page:
        d_ = d[1].find_all_next(class_="r",limit=nlimit)
      else:
        d_ = d[-1].find_all_next(class_="r",limit=nlimit)

    else:
      d_ = None

    try :
      data = d_[(nlimit-_n):nlimit]
      v = [v.text for v in data]
    except AttributeError as e:
      return None

    return v, url


if __name__ == '__main__':
  # https://blog.naver.com/PostView.naver?blogId=htk1019&logNo=221266979613&parentCategoryNo=&categoryNo=27&viewDate=&isShowPopularPosts=true&from=search
  ret,_ = FnGuide.get_data(_name="이녹스첨단소재", _page=2,_item="PER",_n=5,_term="quarter")
  print(ret)
  FnGuide.get_multiples_prev_quater(name="삼성전자",item="PER")
  

