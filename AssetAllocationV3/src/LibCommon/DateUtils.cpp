#include"../LibCommon/DateUtils.h"
#include <iostream>
#include <string>
#include <ctime>

using namespace std;
using namespace utils;

DateUtils::DateUtils(Date start, Date end)
{
    struct tm curr_tm;
    time_t curr_time = time(nullptr);
    localtime_r(&curr_time, &curr_tm);
    Int curr_year = curr_tm.tm_year + 1900;
    Int curr_month= curr_tm.tm_mon + 1;
    Int curr_day  = curr_tm.tm_mday;

    m_today = string_format("%d-%d-%d", curr_year, curr_month, curr_day);
    m_start = start;
    m_end   = end;
    m_curr  = m_start;
}

DateUtils::~DateUtils()
{
}



Date DateUtils::getNextDay(const Date& src)
{
    struct tm next_tm = {0,};
    next_tm.tm_year = atoi(src.substr(0,4).c_str()) - 1900;
    next_tm.tm_mon  = atoi(src.substr(5,2).c_str()) - 1;
    next_tm.tm_mday = atoi(src.substr(8,2).c_str()) + 1;
    time_t next_time = mktime(&next_tm);
    struct tm *next_tm_p = localtime(&next_time);
    char       buf[11];
    strftime(buf, sizeof(buf), "%Y-%m-%d ", next_tm_p);
    return string(buf);
}

Date DateUtils::getNextDay(const Date& src, Int days=1)
{
    struct tm next_tm = {0,};
    next_tm.tm_year = atoi(src.substr(0,4).c_str()) - 1900;
    next_tm.tm_mon  = atoi(src.substr(5,2).c_str()) - 1;
    next_tm.tm_mday = atoi(src.substr(8,2).c_str()) + days;
    time_t next_time = mktime(&next_tm);
    struct tm *next_tm_p = localtime(&next_time);
    char       buf[11];
    strftime(buf, sizeof(buf), "%Y-%m-%d ", next_tm_p);
    return string(buf);
}

Date DateUtils::getPrevDay(const Date& src)
{
    struct tm prev_tm = {0,};
    prev_tm.tm_year = atoi(src.substr(0,4).c_str()) - 1900;
    prev_tm.tm_mon  = atoi(src.substr(5,2).c_str()) - 1;
    prev_tm.tm_mday = atoi(src.substr(8,2).c_str()) - 1;
    time_t prev_time = mktime(&prev_tm);
    struct tm *prev_tm_p = localtime(&prev_time);
    char       buf[11];
    strftime(buf, sizeof(buf), "%Y-%m-%d ", prev_tm_p);
    return string(buf);
}

Date DateUtils::getPrevDay(const Date& src, Int days=1)
{
    struct tm prev_tm = {0,};
    prev_tm.tm_year = atoi(src.substr(0,4).c_str()) - 1900;
    prev_tm.tm_mon  = atoi(src.substr(5,2).c_str()) - 1;
    prev_tm.tm_mday = atoi(src.substr(8,2).c_str()) - days;
    time_t prev_time = mktime(&prev_tm);
    struct tm *prev_tm_p = localtime(&prev_time);
    char       buf[11];
    strftime(buf, sizeof(buf), "%Y-%m-%d ", prev_tm_p);
    return string(buf);
}