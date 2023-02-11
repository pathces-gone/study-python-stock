#define PY_SSIZE_T_CLEAN
#include <iostream>
#include <Python.h>
#include "../include/LibCommon/mytypes.h"

using namespace std;

void initialize(char* module_name, PyObject **pModule)
{
   Py_Initialize();
   PyRun_SimpleString("import sys");
   PyRun_SimpleString("sys.path.append(\"..\")"); //Project root dir.
   PyObject *pName = PyUnicode_DecodeFSDefault(module_name);
   *pModule = PyImport_Import(pName);

   Py_DECREF(pName);
}

void finalize(PyObject *pModule)
{
   Py_DECREF(pModule);
   Py_FinalizeEx();
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

typedef PyObject PyList;
void get_dict(PyObject *pModule)
{
   PyObject *pFunc, *pValue;
   pFunc = PyObject_GetAttrString(pModule, "get_spy");
   pValue = PyObject_CallObject(pFunc, NULL);


   PyList *pDictKeys   = PyDict_Keys(pValue);
   PyList *pDictValues = PyDict_Values(pValue);
   assert(pDictKeys);
   assert(pDictValues);
   assert(PyDict_Size(pValue)    == PyList_Size(pDictKeys));
   assert(PyList_Size(pDictKeys) == PyList_Size(pDictValues));


   printf("Result of call: \n");
   for (int i = 0; i < PyDict_Size(pValue); ++i)
   {
      if(i<10) printf("%s : %4.2f\n", 
            PyUnicode_AsUTF8(PyList_GetItem(pDictKeys,i)),
            PyFloat_AsDouble(PyList_GetItem(pDictValues,i))
         );

   }

   Py_DECREF(pDictKeys);
   Py_DECREF(pDictValues);
   Py_DECREF(pValue);
   Py_DECREF(pFunc);
}

int main(int argc, char *argv[])
{
   PyObject *pModule;
   initialize(argv[1], &pModule);

#ifdef PYTHON_EXAMPLE
   make_string(pModule, "Hello World!");
   make_int(pModule, 99);
   make_list(pModule);
#endif

   get_dict(pModule);

   finalize(pModule);
   return 0;
}