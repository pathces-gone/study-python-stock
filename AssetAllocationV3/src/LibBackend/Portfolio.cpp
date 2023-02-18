#include "Portfolio.h"
#include <string>
#include <vector>


using namespace backend;
using namespace std;

Portfolio::~Portfolio()
{
    for(auto it=m_tradingSheet.begin(); it!=m_tradingSheet.end(); it++)
    {
        if(it->second.size()) it->second.clear();
    }
    m_tradingSheet.clear();
}


Void Portfolio::initTradingSheet(Price initAsset, RatioMap ratios)
{
    m_tradingSheet = m_refSheet;

    TickerList tickers;
    for (auto it = m_refSheet.begin(); it != m_refSheet.end(); it++) {
        tickers.push_back(it->first);   
    }

    Dataframe &ref_df  = m_refSheet[tickers[0]];
    Dataframe total_df; 
 
    Date sdate = ref_df.begin()->first;
    for(auto iter=ref_df.begin(); iter != ref_df.end(); iter++)
    {
        const Date &date = iter->first;
        Price total_price = 0.0f;
        for( Ticker ticker : tickers)
        {
            total_price += ((initAsset*ratios[ticker]) / m_refSheet[ticker][sdate]) * m_refSheet[ticker][date];
        }
        total_df[date] = total_price;

    }

    m_tradingSheet[string("Total")] = total_df;
    total_df.clear();
    tickers.clear();
}


Void Portfolio::printStatus(Date view)
{
    Price initAsset = static_cast<UInt>(m_tradingSheet["Total"].begin()->second);
    Price lastAsset = initAsset;
    Price earn      = 0;
    printf("------------------------------------\n");
    printf("[%11s] Init Asset: %10f$\n\t", view.c_str(), initAsset);
    for (auto it = m_tradingSheet.begin(); it != m_tradingSheet.end(); it++) {
        printf("%6s  ",it->first.c_str());
    }
    printf("\n\t");
    for (auto it = m_tradingSheet.begin(); it != m_tradingSheet.end(); it++) {
        Ticker ticker=it->first;
        if(ticker == string("Total")) lastAsset = it->second[view];
        printf("%4.2f  ",it->second[view]);
    }
    earn = (lastAsset-initAsset)/initAsset*100;
    printf("\n %3.2f%% \n", earn);
    printf("------------------------------------\n");
}