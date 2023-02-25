#include "Portfolio.h"
#include <string>
#include <vector>
#include <iostream>


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
    for (auto it = m_refSheet.begin(); it != m_refSheet.end(); it++)
    {
        Ticker ticker = it->first;
        tickers.push_back(ticker);
    }

    DateUtils date_instance( 
        m_refSheet.begin()->second.begin()->first,
        (--m_refSheet.begin()->second.end())->first);

    Date sdate = date_instance.getCurr();
    Dataframe total_df;
    for(Date date : date_instance.getTradings())
    {
        Price total_price = 0.0f;
        for( Ticker ticker : tickers)
        {
            Price init_price = m_refSheet[ticker][sdate];
            Price init_asset = initAsset*ratios[ticker];
            Int   init_qty   = init_asset/init_price;
            total_price += init_qty*m_refSheet[ticker][date];
        }
        total_df[date] = total_price;
    }
    m_tradingSheet[string("Total")] = total_df;
    total_df.clear();
    tickers.clear();
}

Void Portfolio::printSheet(Int n)
{
    vector<Ticker> keyVec;
    for(auto it_map=m_tradingSheet.begin(); it_map != m_tradingSheet.end(); it_map++)
    {
        Ticker key = it_map->first;
        keyVec.push_back(key);
    }

    printf("%10s","");
    for(Ticker key : keyVec)
    {
        printf("\t%6s",key.c_str());
    }
    cout<<endl;

    Date sdate =m_tradingSheet["Total"].begin()->first;
    Date edate =(--m_tradingSheet["Total"].end())->first;
    DateUtils date_instance(sdate,edate);
    for(Int i=0; i<n; i++)
    {
        Date today = date_instance.getCurr();
        printf("%10s ",today.c_str());
        for(Ticker key : keyVec)
        {
            printf("\t%4.2f",m_tradingSheet[key][today]);
        }
        cout<<endl;
        date_instance.next(1);
    }
}


Void Portfolio::printStatus(Date view)
{
    Price initAsset = static_cast<UInt>(m_tradingSheet["Total"].begin()->second);
    Price lastAsset = initAsset;
    Price earn      = 0;
    printf("-----------------------------------------\n");
    printf("[%11s]\nInit Asset: $%10.2f\n\t", view.c_str(), initAsset);
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
    printf("-----------------------------------------\n");
}