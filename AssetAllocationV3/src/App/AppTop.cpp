#include <iostream>
#include "../LibCommon/mytypes.h"
#include "../LibFrontend/Frontend.h"

using namespace std;
using namespace frontend;

Int main(int argc, char *argv[])
{
   Frontend yfinance (argv[1],argv[0]) ;
   yfinance.loadDataFrame("get_spy");
   return 0;
}