# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Anima Istanbul
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT


class Singleton(type):
    """Metaclass for singletons
    """

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.__instance__ = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance__ is None:
            cls.__instance__ = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.__instance__
