#include"../LibCommon/DateUtils.h"
#include <iostream>
#include <string>
#include <ctime>
#include <algorithm>

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
    m_isFront = false;
    m_isBack  = false;
}

DateUtils::~DateUtils()
{
}

Void DateUtils::next(Int days=1)
{
    struct tm next_tm = {0,};
    next_tm.tm_year = atoi(m_curr.substr(0,4).c_str()) - 1900;
    next_tm.tm_mon  = atoi(m_curr.substr(5,2).c_str()) - 1;
    next_tm.tm_mday = atoi(m_curr.substr(8,2).c_str()) + days;
    time_t next_time = mktime(&next_tm);
    struct tm *next_tm_p = localtime(&next_time);
    char       buf[11];
    strftime(buf, sizeof(buf), "%Y-%m-%d ", next_tm_p);
    m_curr = string(buf);
    m_isFront = false;
    if (m_end < m_curr) {
        m_curr = m_end;
        m_isBack = true;
    }
}

Void DateUtils::prev(Int days=1)
{
    struct tm prev_tm = {0,};
    prev_tm.tm_year = atoi(m_curr.substr(0,4).c_str()) - 1900;
    prev_tm.tm_mon  = atoi(m_curr.substr(5,2).c_str()) - 1;
    prev_tm.tm_mday = atoi(m_curr.substr(8,2).c_str()) - days;
    time_t prev_time = mktime(&prev_tm);
    struct tm *prev_tm_p = localtime(&prev_time);
    char       buf[11];
    strftime(buf, sizeof(buf), "%Y-%m-%d ", prev_tm_p);
    m_curr = string(buf);
    m_isBack = false;
    if (m_start > m_curr){ 
        m_curr = m_end;
        m_isFront = true;
    }
}

DateVec DateUtils::fillEmptys(DateVec src)
{
    assert( src.size() );

    // context switching
    Date _start = m_start;
    Date _end   = m_end;
    Date _curr  = m_curr;
    Bool _isFront= m_isFront;
    Bool _isBack = m_isBack;
    DateVec ret;

    initDate(src.front(), src.back());
    for (Date s : src)
    {
        do {
            ret.push_back( m_curr );
            next(1);
        } while( !(m_curr == s) );
    }

    m_start = _start;
    m_end   = _end;
    m_curr  = _curr;
    m_isFront= _isFront;
    m_isBack = _isBack;
    return ret;
}

DateVec DateUtils::getTradings()
{
    DateVec ret;
    this->setDate(m_start);
    while(!this->m_isBack)
    {
        ret.push_back( m_curr );
        this->next(1);
    }
    return ret;
}

DateVec DateUtils::getRemains()
{
    DateVec ret;
    this->setDate(m_curr);
    while(!this->m_isBack)
    {
        ret.push_back( m_curr );
        this->next(1);
    }
    return ret;
}

DateVec DateUtils::getElapsed()
{
    DateVec ret;
    this->setDate(m_curr);
    while(!this->m_isFront)
    {
        ret.push_back( m_curr );
        this->prev(1);
    }
    reverse(ret.begin(), ret.end());
    return ret;
}