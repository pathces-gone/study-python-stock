#ifndef __DYNAMICAA_H__
#define __DYNAMICAA_H__

#include "Backend.h"
#include "Portfolio.h"

namespace backend
{

class DynamicAA : public Portfolio
{
public:
    DynamicAA(){assert(0);};
    DynamicAA(TickerList tickerList,Date start, Date end) : Portfolio(start,end) 
    {
        m_tickerList = tickerList;
        m_initAsset  = 100000;
    };
    ~DynamicAA();
private:
    Price      m_initAsset;
    TickerList m_tickerList;
    RatioMap   m_ratio;
public:
    Void Run();
};

} // namespace backend
#endif