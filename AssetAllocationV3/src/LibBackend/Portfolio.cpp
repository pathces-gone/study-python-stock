#include "Portfolio.h"

using namespace backend;


Portfolio::~Portfolio()
{
    for(auto it=m_tradingSheet.begin(); it!=m_tradingSheet.end(); it++)
    {
        if(it->second.size()) it->second.clear();
    }
    m_tradingSheet.clear();
}