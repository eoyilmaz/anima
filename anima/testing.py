# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""This module stores helper functions and classes which can be used through
unit testing.
"""


def count_calls(f):
    """A decorator that counts the call count of the decorated method for
    testing purposes

    :param f: the function to be decorated
    :return: function
    """

    def wrapper(*args, **kwargs):
        # first arg is the self
        self = args[0]

        function_name = f.__name__
        if function_name not in self.test_data:
            self.test_data[function_name] = {'call_count': 0, 'data': []}

        d = self.test_data[function_name]

        d['call_count'] += 1
        d['data'] = {'args': args[1:], 'kwargs': kwargs}

        return f(*args, **kwargs)

    return wrapper


class CallInfo(object):
    """A class for completely patching other classes.

    CallInfo classes or derived classes will not function correctly but it will
    store the call info, that is it will store which function or method is
    called and what was the arguments.
    """

    def __init__(self):
        self.call_info = {}
        self.patched_func_names = [
            'setRange', 'setValue', 'setLabelText', 'show', 'close',
            'labelText', 'setLabelText'
        ]

        self.register_functions()

    def function_generator(self, name):
        """Generates a new method with the given name to store the call info

        :param name: the name of the desired method
        :return: function object
        """
        def call_recorder(*args, **kwargs):
            """records the call to a function along with its arguments
            """
            self.call_info[name] = [args, kwargs]
        return call_recorder

    def register_functions(self):
        for f_name in self.patched_func_names:
            setattr(self, f_name, self.function_generator(f_name))
