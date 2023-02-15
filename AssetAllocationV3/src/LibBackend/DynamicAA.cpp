#include "DynamicAA.h"
#include <iostream>

using namespace backend;
using namespace std;

namespace backend
{

DynamicAA::~DynamicAA()
{
    m_tickerList.clear();
}

Void DynamicAA::Run()
{
    Ticker ticker = m_tickerList[0];
    printf("[%s] %s : %4.2f\n",ticker.c_str(), 
        string("2022-07-01").c_str(),
        m_refSheet[ticker][string("2022-07-01")]
    );
}

} // namespace backend