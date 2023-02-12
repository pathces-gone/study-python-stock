#ifndef __BACKEND_H__
#define __BACKEND_H__

#include "../LibCommon/mytypes.h"
#include "../LibCommon/DateUtils.h"

using namespace utils;

namespace backend
{

class Backend : public DateUtils
{
public:
    Backend(){assert(0);};
    Backend(Date start, Date end) : DateUtils(start, end){};
    ~Backend();
private:
    Sheet m_sheet;
public:
    void append(Ticker, DataFrame);

};



} // namespace backend
#endif