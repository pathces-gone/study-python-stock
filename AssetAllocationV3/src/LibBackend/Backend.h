#ifndef __BACKEND_H__
#define __BACKEND_H__

#include "../LibCommon/LibCommonTypes.h"
#include "../LibCommon/DateUtils.h"

using namespace utils;

namespace backend
{

class Backend : public DateUtils
{
/**
 *  @brief For management of m_refSheet which consists of {Ticker : {Date, Price}}.
*/
public:
    Backend(){assert(0);};
    Backend(Date start, Date end) : DateUtils(start, end){};
    ~Backend();
protected:
    Sheet  m_refSheet;
public:
    Void   appendTickerToRefSheet(Ticker, Dataframe);
};


} // namespace backend
#endif