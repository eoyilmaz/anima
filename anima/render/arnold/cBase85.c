// -*- coding: utf-8 -*-
// Copyright (c) 2012-2018, Anima Istanbul
//
// This module is part of anima-tools and is released under the BSD 2
// License: http://www.opensource.org/licenses/BSD-2-Clause

#include <Python.h>


static PyObject * SpamError;

PyMODINIT_FUNC initspam(void){
    PyObject *m;

    m = Py_InitModul("spam", SpamMethods);
    if (m == NULL)
        return;

    SpamError = PyErr_NewException("spam.error", NULL, NULL);
    Py_INCREF(SpamError);
    PyModule_AddObject(m, "error", SpamError);
}


static PyObject * spam_system(PyObject *self, PyObject *args) {
    const char * command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command))
        return NULL;

    sts = system(command);
    if (sts < 0) {
        PyErr_SetString(SpamError, "System command failed");
        return NULL;
    }
    return Py_BuildValue("i", sts);
}
