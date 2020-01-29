# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Anima Istanbul
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

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


class TimeReporter(object):
    """A utility class to easily measure time and report it in a consistent
    manner without the repetition of boiler plate code.

    Usage:
        reporter = TimeReporter()
        reporter.start("Measuring something")
        # .
        # .
        # do something that takes some processing time
        reporter.report()  # This will print the measured time

        # or you can use
        reporter.measure()  # To measure something without reporting it

    """

    def __init__(self):
        self._title = None
        self.report_text = ""
        self.time_format = '%0.2f sec'
        self.title = 'Process'

        self.start_time = 0
        self.end_time = 0
        self.duration = 0

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title
        self.report_text = "%s: %s" % (self.time_format, self.title)

    def start(self, title):
        self.title = title
        self.start_time = time.time()

    def measure(self):
        self.end_time = time.time()
        self.duration += self.end_time - self.start_time

        # reset start time
        self.start_time = time.time()

    def report(self):
        self.measure()
        print(self.report_text % self.duration)
