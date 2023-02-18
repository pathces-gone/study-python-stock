#ifndef __MY_TYPES_H__
#define __MY_TYPES_H__

typedef int Int;
typedef char Char;
typedef short Short;
typedef double Double;
typedef float Float;
typedef unsigned int UInt;
typedef void Void;
typedef bool Bool;

#include <map>
#include <string>
#include <vector>
typedef Float Price;
typedef std::string Date;
typedef std::string Ticker;
typedef std::vector<Date>   DateVec;
typedef std::vector<Ticker> TickerList;
typedef std::map<Ticker, Price>  RatioMap;
typedef std::map<Date,Price> Dataframe;
typedef std::map<Ticker, Dataframe> Sheet;
typedef const char* PYMethod;
typedef const char* PYModule;
#endif