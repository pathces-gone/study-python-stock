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
   Date start = "2022-07-11";
   Date end   = "2022-08-01";

   Frontend yfinance (argv[1],argv[0]) ;
   yfinance.loadDataframe("get_spy");

   DynamicAA dynamic(start, end);
   dynamic.append(string("SP500"), yfinance.getDataframe());
   dynamic.append(string("NP500"), yfinance.getDataframe());
   return 0;
}