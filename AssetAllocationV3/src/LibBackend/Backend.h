#ifndef __BACKEND_H__
#define __BACKEND_H__

#include "../LibCommon/mytypes.h"
#include <vector>

namespace backend
{

class Backend
{
public:
    Backend();
    ~Backend();
private:
    Sheet m_sheet;
public:
    Void append(Ticker, DataFrame);
};





} // namespace backend
#endif