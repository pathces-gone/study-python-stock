#ifndef __FRONTEND_H__
#define __FRONTEND_H__

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "../LibCommon/LibCommonTypes.h"

namespace frontend
{

class Frontend
{
public:
    Frontend (PYModule module_name, const char *root_path);
    ~Frontend(){
        if(pModule) this->finalize(pModule);
        m_tradeDataframe.clear();
    }
private:
    PyObject *pModule;
    Void initialize(const char* pypath, PYModule module_name, PyObject **pModule);
    Void finalize(PyObject *pModule);

    Dataframe m_tradeDataframe;
public:
    Void loadDataframe(PYMethod, Ticker, Date, Date);
    Dataframe getDataframe() {return m_tradeDataframe;};
};

}
#endif