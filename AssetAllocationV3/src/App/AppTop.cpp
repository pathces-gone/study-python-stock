#include <iostream>

#include "../LibCommon/mytypes.h"
#include "../LibFrontend/Frontend.h"
#include "../LibBackend/Backend.h"

using namespace frontend;
using namespace backend;
using namespace std;

Int main(int argc, char *argv[])
{
   Frontend yfinance (argv[1],argv[0]) ;
   yfinance.loadDataFrame("get_spy");
   
   Backend dynamic;
   dynamic.append(string("SP500"), yfinance.getDataFrame());
   dynamic.append(string("NP500"), yfinance.getDataFrame());

   return 0;
}