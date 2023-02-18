#include <iostream>

#include "../LibCommon/LibCommonTypes.h"
#include "../LibFrontend/Frontend.h"
#include "../LibBackend/Backend.h"
#include "../LibBackend/DynamicAA.h"

using namespace frontend;
using namespace backend;
using namespace std;

/***
 * Arg0 : root_path
 * Arg1 : module_name
*/
Int main(int argc, char *argv[])
{
   //Frontend pyEnv(argv[1],argv[0]);
   Date sdate = "2022-06-01";
   Date edate = "2022-08-01";


   //Frontend pyTicker(argv[2],argv[0]);
   TickerList tickers;
   tickers.push_back("SPY");
   tickers.push_back("QQQ");

   Frontend  yfinance (argv[1],argv[0]);
   DynamicAA dynamic  (tickers, sdate, edate);
   for (Ticker tick : tickers)
   {
      yfinance.loadDataframe("getFromYF", tick, sdate, edate);
      dynamic.appendTickerToRefSheet(tick, yfinance.getDataframe());
   }

   dynamic.Run();


   return 0;
}