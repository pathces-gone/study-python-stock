#ifndef __MY_TYPES_H__
#define __MY_TYPES_H__

typedef int Int;
typedef char Char;
typedef short Short;
typedef double Double;
typedef float Float;
typedef unsigned int UInt;
typedef void Void;

#include <map>
#include <string>
typedef std::string Date;
typedef Float Price;
typedef std::map<Date,Price> DataFrame;
typedef std::string Ticker;
typedef std::map<Ticker, DataFrame> Sheet;
#endif