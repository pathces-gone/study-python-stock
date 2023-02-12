#ifndef __FRONTEND_H__
#define __FRONTEND_H__

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "../LibCommon/mytypes.h"

#include <vector>
#include <map>
#include <string>

using namespace std;

typedef std::string Date;
typedef Float Price;
typedef std::map<Date,Price> DataFrame;

namespace frontend
{
    class Pandas;
    class Frontend
    {
    public:
        Frontend (const char *module_name, const char *root_path);
        ~Frontend(){
            if(pModule) this->finalize(pModule);
            m_tradeDataFrame.clear();
        }
    private:
        PyObject *pModule;
        Void initialize(const char* pypath, const char* module_name, PyObject **pModule);
        Void finalize(PyObject *pModule);

        DataFrame m_tradeDataFrame;
    public:
        Void loadDataFrame(const char* pFuncName);
        DataFrame getDataFrame() {return m_tradeDataFrame;};
    };
}
#endif