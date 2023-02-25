#include "Backend.h"
#include <iostream>

using namespace backend;
using namespace std;

Backend::~Backend()
{
    for(auto it=m_refSheet.begin(); it!=m_refSheet.end(); it++)
    {
        if(it->second.size()) it->second.clear();
    }
    m_refSheet.clear();
}

Void Backend::appendTickerToRefSheet(Ticker ticker, Dataframe df)
{
    if(m_refSheet.find(ticker) == m_refSheet.end())
    {
        m_refSheet[ticker] = Backend::fillEmptyDays(df);
    }
}

Dataframe Backend::fillEmptyDays(Dataframe &df)
{
    Dataframe ret=df;
    DateUtils date_instance(
        df.begin()->first,
        (--df.end())->first
    );

    for(Date date : date_instance.getTradings())
    {
        if (ret.find(date) == ret.end()) ret[date] = 0.0f;
    }

    for(Date date : date_instance.getTradings())
    {
        if(ret[date] != 0.0f) continue;
        date_instance.setDate(date);
        date_instance.prev(1);
        
        if(date_instance.getIsFront()) continue;
    
        Date prev = date_instance.getCurr();
        ret[date] = ret[prev];
    }

    date_instance.initDate( df.begin()->first, (--df.end())->first);
    for(Date date : date_instance.getTradings())
    {
        if(ret[date] == 0.0f) ret.erase(date);
    }
    return ret;
}