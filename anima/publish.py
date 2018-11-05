# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""This module contains scripts those run when a new Version is published. It
is a way of checking the quality of the published versions.
"""
PRE_PUBLISHER_TYPE = 0
POST_PUBLISHER_TYPE = 1


publishers = {
    PRE_PUBLISHER_TYPE: {},
    POST_PUBLISHER_TYPE: {}
}

# This is a storage for intermediate data like newly created versions etc.
staging = {}


def register_publisher(callable_, type_name='', publisher_type=PRE_PUBLISHER_TYPE):
    """Registers a function as a publisher for defined task types.

    :param function callable_: The callable that is the publisher.
    :param str type_name: The string or a list of strings that represents the
      name of the type that this publisher should be registered to. If skipped
      of is an empty string the given callable_ will be registered as a generic
      publisher and will always run first.
    :param int publisher_type: 0 for pre publishers 1 for post publishers.
    :return:
    """

    if not callable(callable_):
        raise TypeError('%s is not callable' % callable_.__class__.__name__)

    def register_one(t_name, p_type):
        t_name = t_name.lower()
        if t_name not in publishers[p_type]:
            publishers[p_type][t_name] = []

        if callable_ not in publishers[p_type][t_name]:
            publishers[p_type][t_name].append(callable_)

    if isinstance(type_name, list):
        for item in type_name:
            register_one(item, publisher_type)
    else:
        # it should have only one item
        register_one(type_name, publisher_type)


def publisher(type_name='', publisher_type=PRE_PUBLISHER_TYPE):
    """A decorator to easily register a method or function as a publisher

    :param str type_name: The name of this publisher type.
    :param int publisher_type: 0 for pre 1 for post publishers
    """
    def wrapper(f):
        register_publisher(f, type_name, publisher_type)
        return f

    if callable(type_name):
        # it must be the function it self
        f = type_name
        type_name = ''
        return wrapper(f)

    return wrapper


def run_publishers(type_name='', publisher_type=PRE_PUBLISHER_TYPE):
    """Runs all the publishers registered under the given type name

    :param str type_name: A string holding the type name
    :return:
    """
    if type_name != '':
        for f in publishers[publisher_type].get('', []):  # run generic
            f()                                           # publishers first

    for f in publishers[publisher_type].get(type_name.lower(), []):
        f()


def clear_publishers():
    """utility function to clear publishers
    """
    publishers[PRE_PUBLISHER_TYPE].clear()
    publishers[POST_PUBLISHER_TYPE].clear()


class ProgressControllerBase(object):
    """Base class for progress controllers.

    If given each publisher can call progress_controller objects. This class is
    the base class and shows the minimum required interface to the progress
    controllers.

    Instantiate this and customize to your needs.
    """

    def __init__(self, minimum=0.0, maximum=100.0, value=0.0):
        self._minimum = 0.0
        self._maximum = 100.0
        self._value = 0.0

        self.value = value
        self.minimum = minimum
        self.maximum = maximum

    @property
    def value(self):
        """getter for the value attribute
        """
        return self._value

    @value.setter
    def value(self, value):
        """setter for the value attribute

        :param value: 
        :return: 
        """
        self._value = value

    @property
    def minimum(self):
        """getter for the minimum attribute
        """
        return self._minimum

    @minimum.setter
    def minimum(self, minimum):
        """setter for the minimum attribute

        :param minimum: 
        :return: 
        """
        self._minimum = minimum

    @property
    def maximum(self):
        """getter for the maximum attribute
        """
        return self._maximum

    @maximum.setter
    def maximum(self, maximum):
        """setter for the maximum attribute

        :param maximum: 
        :return: 
        """
        self._maximum = maximum

    def increment(self, step=1.0):
        """increases value by 1 step
        """
        self.value += step

    def complete(self):
        """completes the progress
        """
        self.value = self.maximum
