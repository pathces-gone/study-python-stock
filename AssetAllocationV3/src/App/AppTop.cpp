#include <iostream>

#include "../LibCommon/LibCommonTypes.h"
#include "../LibFrontend/Frontend.h"
#include "../LibBackend/Backend.h"
#include "../LibBackend/DynamicAA.h"

using namespace frontend;
using namespace backend;
using namespace std;

Int main(int argc, char *argv[])
{
   // Init Env.
   //Frontend pyEnv(argv[1],argv[0]);
   Date start = "2022-06-01";
   Date end   = "2022-08-01";

   // Set Tickers
   //Frontend pyTicker(argv[2],argv[0]);
   TickerList tickers;
   tickers.push_back("SPY");

   // Init portfolio
   Frontend yfinance (argv[1],argv[0]);
   DynamicAA  dynamic  (tickers, start, end);
   for (Ticker tick : tickers)
   {
   #if 1
      yfinance.loadDataframe("get_spy");
   #else
      yfinance.loadDataframe(tick);
   #endif
      dynamic.appendTickerToRefSheet(tick, yfinance.getDataframe());
   }

   // Run DynamicAA
   dynamic.Run();

   return 0;
}