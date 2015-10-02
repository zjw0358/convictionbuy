/*
http://www.zhihu.com/question/23003213

E:\work\convictionbuy\study>cl /LD great_module.cpp /o great_module.pyd -I"C:\Pr
ogram Files (x86)\Enthought\Canopy32\App\appdata\canopy-1.5.1.2730.win-x86\inclu
de" "C:\Program Files (x86)\Enthought\Canopy32\App\appdata\canopy-1.5.1.2730.win
-x86\libs\python27.lib"
*/
#include <Python.h>

int great_function(int a) {
    return a + 1;
}

static PyObject * _great_function(PyObject *self, PyObject *args)
{
    int _a;
    int res;

    if (!PyArg_ParseTuple(args, "i", &_a))
        return NULL;
    res = great_function(_a);
    return PyLong_FromLong(res);
}

static PyMethodDef GreateModuleMethods[] = {
    {
        "great_function",
        _great_function,
        METH_VARARGS,
        ""
    },
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initgreat_module(void) {
    (void) Py_InitModule("great_module", GreateModuleMethods);
}