# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


import unittest
from anima.extension import extends


class ExtenderTester(unittest.TestCase):
    """tests the anima.extension.extender decorator
    """

    def setUp(self):
        """setup the test
        """
        class Foo(object):
            """test class
            """
            def func1(self):
                """an existing function
                """
                return 'func1'

        self.foo_class = Foo

    def test_extends_is_working_fine_for_classes(self):
        """testing if the extender will work properly with class methods
        """
        class Bar(object):
            """A test class whose methods will override other class
            """
            @extends(self.foo_class)
            def new_func1(self):
                return 'new_func1'

        b = Bar()
        b_result = b.new_func1()

        f = self.foo_class()
        f_result = f.new_func1()

        self.assertEqual(
            b_result,
            f_result
        )

    # def test_extends_will_store_clashing_functions(self):
    #     """testing if extended function name already exist will be stored in
    #     __orig__ attribute
    #     """
    #     class Bar(object):
    #         """A test class whose methods will override other class
    #         """
    #         @extends(self.foo_class)
    #         def func1(self):
    #             return 'overridden func1'
    # 
    #     b = Bar()
    #     b_result = b.func1()
    # 
    #     f = self.foo_class()
    #     f_result = f.func1()
    # 
    #     self.assertEqual(
    #         b_result,
    #         f_result
    #     )
    # 
    #     print f.__dict__
    # 
    #     self.assertEqual(
    #         'func1',
    #         f._func1_orig_()
    #     )

    def test_cls_argument_can_be_a_list_of_classes(self):
        """testing if cls argument is a list of classes extender will extend
        them all.
        """
        class Baz(object):
            pass

        class Bar(object):
            pass

        class Extension(object):
            @extends([Baz, Bar])
            def func1(self):
                return 'overridden func1 in %s' % self.__class__.__name__

            @extends(Baz)
            def func2(self):
                return 'overridden func2 in %s' % self.__class__.__name__

            @extends(Bar)
            def func3(self):
                return 'overridden func3 in %s' % self.__class__.__name__

        b1 = Baz()
        b2 = Bar()

        self.assertEqual(
            b1.func1(), 'overridden func1 in Baz'
        )

        self.assertEqual(
            b2.func1(), 'overridden func1 in Bar'
        )

        self.assertEqual(
            b1.func2(), 'overridden func2 in Baz'
        )

        self.assertEqual(
            b2.func3(), 'overridden func3 in Bar'
        )
