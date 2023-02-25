#ifndef __PORTFOLIO_H__
#define __PORTFOLIO_H__

#include "Backend.h"


namespace backend
{

class Portfolio : public Backend
{
public:
    Portfolio(){assert(0);};
    Portfolio(Date start, Date end) : Backend(start,end) {};
    ~Portfolio();

protected:
    Sheet m_tradingSheet;

    Void initTradingSheet(Price, RatioMap);
    Void printStatus(Date);
    Void printSheet(Int);
public:
};

} // namespace backend
#endif