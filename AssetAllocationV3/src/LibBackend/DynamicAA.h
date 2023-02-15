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
    };
    ~DynamicAA();

private:
    TickerList m_tickerList;

public:
    Void Run();
};

} // namespace backend
#endif