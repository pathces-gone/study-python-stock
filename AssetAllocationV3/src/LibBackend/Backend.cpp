#include "Backend.h"
#include <iostream>

using namespace backend;
using namespace std;

Backend::Backend()
{
}

Backend::~Backend()
{
    for(auto it=m_sheet.begin(); it!=m_sheet.end(); it++)
    {
        if(it->second.size()) it->second.clear();
    }
    m_sheet.clear();
}

Void Backend::append(Ticker ticker, DataFrame df)
{
    if(m_sheet.find(ticker) == m_sheet.end())
    {
        m_sheet[ticker] = df;

    #if 0
        printf("[%s] %s : %4.2f\n",ticker.c_str(), 
            string("2022-07-01").c_str(),
            m_sheet[ticker][string("2022-07-01")]
        );
    #endif
    }
}