#include <iostream>
#include "../LibFrontend/Frontend.h"

using namespace std;

namespace frontend
{
Frontend::Frontend (PYModule module_name, const char *root_path){
    string pypath = ".."; //TODO
    this->initialize(pypath.c_str(), module_name, &pModule);
}

void Frontend::initialize(const char* pypath ,PYModule module_name, PyObject **pModule)
{
    string command = string("sys.path.append(\"")+string(pypath)+string("\")"); 
    Py_Initialize();
    PyRun_SimpleString("import sys");
    PyRun_SimpleString(command.c_str());

    PyObject *pName = PyUnicode_DecodeFSDefault(module_name);
    *pModule = PyImport_Import(pName);
    Py_DECREF(pName);
}

void Frontend::finalize(PyObject *pModule)
{
    Py_DECREF(pModule);
    Py_FinalizeEx();
}


typedef PyObject PyList;
void Frontend::loadDataframe(PYMethod pFuncName, Ticker ticker, Date sdate, Date edate)
{
    /**
     * Input:  python method
     * Output: Dataframe
    */
    PyObject *pFunc, *pArgs ,*pValue;
    pFunc  = PyObject_GetAttrString(pModule, pFuncName);

    pArgs = PyTuple_New(3);
    PyTuple_SetItem(pArgs, 0, PyUnicode_FromString(ticker.c_str()));
    PyTuple_SetItem(pArgs, 1, PyUnicode_FromString(sdate.c_str()));
    PyTuple_SetItem(pArgs, 2, PyUnicode_FromString(edate.c_str()));

    pValue = PyObject_CallObject(pFunc, pArgs);

    PyList *pDictKeys   = PyDict_Keys(pValue);
    PyList *pDictValues = PyDict_Values(pValue);
    assert(pDictKeys);
    assert(pDictValues);
    assert(PyDict_Size(pValue)    == PyList_Size(pDictKeys));
    assert(PyList_Size(pDictKeys) == PyList_Size(pDictValues));

    for (Int i = 0; i < PyDict_Size(pValue); ++i)
    {
        Date date  = PyUnicode_AsUTF8(PyList_GetItem(pDictKeys,i));
        Price price= PyFloat_AsDouble(PyList_GetItem(pDictValues,i));
        m_tradeDataframe[date] = price;
    }

    Py_DECREF(pDictKeys);
    Py_DECREF(pDictValues);
    Py_DECREF(pValue);
    Py_DECREF(pFunc);
}

#ifdef PYTHON_EXAMPLE
void make_string(PyObject *pModule, char *arg)
{
   PyObject *pFunc, *pArgs, *pValue;
   pFunc = PyObject_GetAttrString(pModule, "make_string");
   pArgs = PyTuple_New(1);

   PyTuple_SetItem(pArgs, 0, PyUnicode_FromString(arg));
   pValue = PyObject_CallObject(pFunc, pArgs);
   Py_DECREF(pArgs);

   printf("Result of call: %s \n", PyUnicode_AsUTF8(pValue));
   Py_DECREF(pValue);
   Py_DECREF(pFunc);
}

void make_int(PyObject *pModule, int arg)
{
   PyObject *pFunc, *pArgs, *pValue;
   pFunc = PyObject_GetAttrString(pModule, "make_int");
   pArgs = PyTuple_New(1);

   PyTuple_SetItem(pArgs, 0, PyLong_FromLong(arg));
   pValue = PyObject_CallObject(pFunc, pArgs);
   Py_DECREF(pArgs);

   printf("Result of call: %d \n", PyLong_AsLong(pValue));
   Py_DECREF(pValue);
   Py_DECREF(pFunc);

}

void make_list(PyObject *pModule)
{
   PyObject *pFunc, *pArgs, *pValue;
   pFunc = PyObject_GetAttrString(pModule, "make_list");
   pValue = PyObject_CallObject(pFunc, NULL);

   printf("Result of call: \n");
   for (int i = 0; i < PyList_Size(pValue); ++i)
   {
      printf("\t%dst item: %s \n", i, PyUnicode_AsUTF8(PyList_GetItem(pValue, i)));
   }
   Py_DECREF(pValue);
   Py_DECREF(pFunc);
}
#endif

}
