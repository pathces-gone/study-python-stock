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
        m_refSheet[ticker] = df;
    }
}