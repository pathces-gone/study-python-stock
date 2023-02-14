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
typedef std::string Date;
typedef Float Price;
typedef std::map<Date,Price> Dataframe;
typedef std::string Ticker;
typedef std::map<Ticker, Dataframe> Sheet;
typedef std::vector<Date> DateVec;
#endif