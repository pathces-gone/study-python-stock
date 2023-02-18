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
#if 1
    for (Ticker ticker : m_tickerList)
    {
        printf("[%s] %s : %4.2f\n",ticker.c_str(), 
            string("2022-07-01").c_str(),
            m_refSheet[ticker][string("2022-07-01")]
        );
    }
#endif

    Float eq_ratio = 1/static_cast<Float>(m_tickerList.size()); 
    for (Ticker ticker : m_tickerList)
    {
        m_ratio[ticker] = eq_ratio;
    }

    Portfolio::initTradingSheet(m_initAsset, m_ratio);

    Date view = string("2022-07-01");
    Portfolio::printStatus(view);

}

} // namespace backend