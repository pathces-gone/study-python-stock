#include <iostream>

#include "../LibCommon/mytypes.h"
#include "../LibFrontend/Frontend.h"
#include "../LibBackend/Backend.h"
#include "../LibBackend/DynamicAA.h"

using namespace frontend;
using namespace backend;
using namespace std;

Int main(int argc, char *argv[])
{
   Date start = "2022-07-31";
   Date end   = "2022-08-01";

   Frontend yfinance (argv[1],argv[0]) ;
   yfinance.loadDataFrame("get_spy");


   DynamicAA dynamic(start, end);
   dynamic.append(string("SP500"), yfinance.getDataFrame());
   dynamic.append(string("NP500"), yfinance.getDataFrame());

   return 0;
}