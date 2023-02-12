#ifndef __DYNAMICAA_H__
#define __DYNAMICAA_H__

#include "Backend.h"

namespace backend
{

class DynamicAA : public Backend
{
public:
    DynamicAA(){assert(0);};
    DynamicAA(Date start, Date end) : Backend(start,end) {};
    ~DynamicAA();

private:


public:
    Void Run();
};

}
#endif