#ifndef __DATEUTILS_H__
#define __DATEUTILS_H__


#include <ctime>
#include <assert.h>
#include <string>
#include <stdexcept>
#include <memory>
#include "../LibCommon/mytypes.h"

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
protected:
    template<typename ... Args>
    std::string string_format(const std::string& format, Args ... args)
    {
        size_t size = snprintf(nullptr, 0, format.c_str(), args ...) + 1;
        if (size <= 0) { throw std::runtime_error("Error during formatting."); }
        std::unique_ptr<char[]> buf(new char[size]);
        snprintf(buf.get(), size, format.c_str(), args ...);
        return std::string(buf.get(), buf.get() + size - 1);
    }
    Date getNextDay(const Date&);
    Date getNextDay(const Date&, Int);
    Date getPrevDay(const Date&);
    Date getPrevDay(const Date&, Int);
};


}
#endif