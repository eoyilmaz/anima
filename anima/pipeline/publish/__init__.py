# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""This module contains scripts those run when a new Version is published. It
is a way of cleaning the published versions.

The python file matching the type of the Task.type will run when publishing the
Version instance.
"""

import logging
logger = logging.getLogger(__name__)


def register_publisher(callable, type_name):
    """Registers a function as a publisher for defined task types.

    :param callable: The callable that is the publisher.
    :param type_name: The string or a list of strings that represents the
      name of the type that this publisher should be registered to.
    :return:
    """
    pass


def publisher(type_name):
    """A decorator to easily register a method or function as a publisher
    """

    def wrapper(f):
        logger.debug('registering %s as a publisher for ')
        register_publisher(f, type_name)

        def wrapped_f(*args, **kwargs):
            f(*args, **kwargs)

        return wrapped_f
    return wrapper


class PublisherBase(object):
    """The base class for publish checkers.

    A Publisher is a class derived from this base class and checks version
    contents if they are complying with rules defined by the Pipeline.
    """

    @publisher('LookDev')
    def test_func1(self, a, b, c='', d=''):
        print 'inside test_func1'
