# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import time

indentation = 0
tab_stop = 3


def measure_time(f_name):
    """This is a decorator that measures performance of the decorated function

    :param f_name: The name of the decorated function
    """

    def wrapper(f):
        f_inner_name = f_name
        if f_inner_name is None:
            f_inner_name = f.__name__

        def wrapped_f(*args, **kwargs):
            global indentation
            global tab_stop

            start = time.time()
            print("%s%11s start" % (" " * indentation, f_inner_name))
            indentation += tab_stop
            try:
                return_data = f(*args, **kwargs)
            except TypeError:
                    return_data = f(*args)
            finally:
                end = time.time()
                indentation -= tab_stop

                print('%s%11s: %0.3f sec' % (" " * indentation, f_inner_name, (end - start)))

            return return_data

        return wrapped_f
    return wrapper
