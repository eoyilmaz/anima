# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
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
