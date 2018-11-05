# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import time


def measure_time(f_name):
    """This is a decorator that measures performance of the decorated function

    :param function_name: The name of the decorated function
    """

    def wrapper(f):
        f_inner_name = f_name
        if f_inner_name is None:
            f_inner_name = f.__name__

        def wrapped_f(*args, **kwargs):
            start = time.time()
            return_data = f(*args, **kwargs)
            end = time.time()
            print('%11s: %0.3f sec' % (f_inner_name, (end - start)))
            return return_data

        return wrapped_f
    return wrapper
