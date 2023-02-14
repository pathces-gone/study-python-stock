#ifndef __BACKEND_H__
#define __BACKEND_H__

#include "../LibCommon/mytypes.h"
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
private:
    Sheet  m_refSheet;
protected:
    Void   appendTickerToRefSheet(Ticker, Dataframe);
    Sheet& getRefSheet(); 
};


} // namespace backend
#endif