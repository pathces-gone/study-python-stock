#ifndef __DATEUTILS_H__
#define __DATEUTILS_H__

#include <ctime>
#include <assert.h>
#include <string>
#include <stdexcept>
#include <memory>
#include "../LibCommon/LibCommonTypes.h"

namespace utils
{

class DateUtils
{
public:
    DateUtils() {assert(0);};
    DateUtils(Date start, Date end);
    ~DateUtils();
private:
    Date m_start;
    Date m_end;
    Date m_today;
    Date m_curr;
    Bool m_isFront;
    Bool m_isBack;
public:
    Void next(Int);
    Void prev(Int);
    Void initDate(Date start, Date end){
        m_start=start;
        m_end=end;
        m_curr=start;
        m_isFront = false;
        m_isBack  = false;
    };
    Void setDate (Date curr) {
        m_curr=curr;
        if(m_start>=curr){m_curr=m_start; m_isFront = true; m_isBack = false;}
        if(m_end<=curr)  {m_curr=m_end;   m_isFront = false; m_isBack = true;}
    };
    Bool getIsFront()const {return m_isFront;};
    Bool getIsBack() const {return m_isBack;};
    Date getCurr()   const {return m_curr;};
    DateVec fillEmptys(DateVec);
    DateVec getTradings();
    DateVec getRemains();
    DateVec getElapsed();
};

template<typename ... Args>
std::string string_format(const std::string& format, Args ... args)
{
    size_t size = snprintf(nullptr, 0, format.c_str(), args ...) + 1;
    if (size <= 0) { throw std::runtime_error("Error during formatting."); }
    std::unique_ptr<char[]> buf(new char[size]);
    snprintf(buf.get(), size, format.c_str(), args ...);
    return std::string(buf.get(), buf.get() + size - 1);
}
}
#endif