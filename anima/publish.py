# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""This module contains scripts those run when a new Version is published. It
is a way of checking the quality of the published versions.
"""

import logging
logger = logging.getLogger(__name__)


publishers = {}


def register_publisher(callable_, type_name=''):
    """Registers a function as a publisher for defined task types.

    :param function callable_: The callable that is the publisher.
    :param str type_name: The string or a list of strings that represents the
      name of the type that this publisher should be registered to. If skipped
      of is an empty string the given callable_ will be registered as a generic
      publisher and will always run first.
    :return:
    """
    if not callable(callable_):
        raise TypeError('%s is not callable' % callable_.__class__.__name__)

    if type_name not in publishers:
        publishers[type_name] = []

    if callable_ not in publishers[type_name]:
        publishers[type_name].append(callable_)


def publisher(type_name=''):
    """A decorator to easily register a method or function as a publisher

    :param str type_name: The name of this publisher type.
    """
    def wrapper(f):
        register_publisher(f, type_name)
        return f

    if callable(type_name):
        # it must be the function it self
        f = type_name
        type_name = ''
        return wrapper(f)

    return wrapper


def run_publishers(type_name=''):
    """Runs all the publishers registered under the given type name

    :param str type_name: A string holding the type name
    :return:
    """
    if type_name != '':
        for f in publishers.get('', []):  # run generic publishers first
            f()

    for f in publishers.get(type_name, []):
        f()
