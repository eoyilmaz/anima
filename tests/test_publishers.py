# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Anima Istanbul
#
# This module is part of anima-tools and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

import unittest

from anima.publish import (publishers, publisher, run_publishers,
                           clear_publishers, register_publisher,
                           PRE_PUBLISHER_TYPE, POST_PUBLISHER_TYPE)


class PublishersTestCase(unittest.TestCase):
    """tests the anima.publish module
    """

    def tearDown(self):
        """clean up test
        """
        # clean up publishers dictionary
        clear_publishers()

    def test_registering_a_publisher(self):
        """testing if registering a publisher is working properly
        """
        self.assertEqual(publishers, {PRE_PUBLISHER_TYPE: {},
                                      POST_PUBLISHER_TYPE: {}})

        def some_callable():
            pass

        register_publisher(some_callable, 'Test')

        self.assertTrue('test' in publishers[PRE_PUBLISHER_TYPE])
        self.assertTrue(
            isinstance(publishers[PRE_PUBLISHER_TYPE]['test'], list)
        )
        self.assertTrue(publishers[PRE_PUBLISHER_TYPE]['test'][0],
                        some_callable)

    def test_registering_a_post_publisher(self):
        """testing if registering a post publisher is working properly
        """
        self.assertEqual(publishers, {PRE_PUBLISHER_TYPE: {},
                                      POST_PUBLISHER_TYPE: {}})

        def some_callable():
            pass

        register_publisher(some_callable, 'Test', POST_PUBLISHER_TYPE)

        self.assertTrue('test' in publishers[POST_PUBLISHER_TYPE])
        self.assertTrue(
            isinstance(publishers[POST_PUBLISHER_TYPE]['test'], list)
        )
        self.assertTrue(publishers[POST_PUBLISHER_TYPE]['test'][0],
                        some_callable)

    def test_registering_with_the_decorator_is_working_properly(self):
        """testing if registering with decorator is working properly
        """
        @publisher('Test')
        def some_callable():
            pass

        self.assertTrue('test' in publishers[PRE_PUBLISHER_TYPE])
        self.assertTrue(
            isinstance(publishers[PRE_PUBLISHER_TYPE]['test'], list)
        )
        self.assertTrue(
            publishers[PRE_PUBLISHER_TYPE]['test'][0],
            some_callable
        )

    def test_run_publishers_is_working_properly(self):
        """testing if the run_publishers() function calls all the publishers
        under given name
        """
        called = []

        @publisher('Test')
        def func1():
            called.append('func1')

        @publisher('Test')
        def func2():
            called.append('func2')

        @publisher('Test2')
        def func3():
            """another publisher for some other type
            """
            called.append('func3')

        @publisher
        def func4():
            """this should run for everything
            """
            called.append('func4')

        # be sure that the called is still empty
        self.assertEqual(called, [])

        # now run all publishers
        run_publishers('Test')
        self.assertEqual(called, ['func4', 'func1', 'func2'])

    def test_run_publishers_is_working_properly_with_pre_publishers_specified(self):
        """testing if the run_publishers() function calls all the pre
        publishers under given name
        """
        called = []

        @publisher('Test', publisher_type=PRE_PUBLISHER_TYPE)
        def func1():
            called.append('func1')

        @publisher('Test', publisher_type=PRE_PUBLISHER_TYPE)
        def func2():
            called.append('func2')

        @publisher('Test2', publisher_type=PRE_PUBLISHER_TYPE)
        def func3():
            """another publisher for some other type
            """
            called.append('func3')

        @publisher(publisher_type=PRE_PUBLISHER_TYPE)
        def func4():
            """this should run for everything
            """
            called.append('func4')

        # be sure that the called is still empty
        self.assertEqual(called, [])

        # now run all publishers
        run_publishers('Test')
        self.assertEqual(called, ['func4', 'func1', 'func2'])

    def test_run_publishers_is_working_properly_with_post_publishers_specified(self):
        """testing if the run_publishers() function calls all the post
        publishers under given name
        """
        called = []

        # Register some pre publishers
        @publisher('Test', publisher_type=PRE_PUBLISHER_TYPE)
        def pre_func1():
            called.append('pre_func1')

        @publisher('Test', publisher_type=PRE_PUBLISHER_TYPE)
        def pre_func2():
            called.append('pre_func2')

        @publisher('Test2', publisher_type=PRE_PUBLISHER_TYPE)
        def pre_func3():
            """another publisher for some other type
            """
            called.append('pre_func3')

        @publisher(publisher_type=PRE_PUBLISHER_TYPE)
        def pre_func4():
            """this should run for everything
            """
            called.append('pre_func4')

        # Register some post publishers
        @publisher('Test', publisher_type=POST_PUBLISHER_TYPE)
        def func1():
            called.append('func1')

        @publisher('Test', publisher_type=POST_PUBLISHER_TYPE)
        def func2():
            called.append('func2')

        @publisher('Test2', publisher_type=POST_PUBLISHER_TYPE)
        def func3():
            """another publisher for some other type
            """
            called.append('func3')

        @publisher(publisher_type=POST_PUBLISHER_TYPE)
        def func4():
            """this should run for everything
            """
            called.append('func4')

        # be sure that the called is still empty
        self.assertEqual(called, [])

        # now run all publishers
        run_publishers('Test', publisher_type=POST_PUBLISHER_TYPE)
        self.assertEqual(called, ['func4', 'func1', 'func2'])

    def test_registering_a_callable_multiple_times(self):
        """testing if registering a callable multiple times will not call the
        function more than 1 time
        """
        called = []

        @publisher('Test')
        def func1():
            called.append('func1')

        @publisher('Test')
        def func2():
            called.append('func2')

        @publisher('Test2')
        def func3():
            """another publisher for some other type
            """
            called.append('func3')

        @publisher
        def func4():
            """this should run for everything
            """
            called.append('func4')

        # be sure that the called is still empty
        self.assertEqual(called, [])

        # register fun1 and func2 more than one times
        register_publisher(func1, 'Test')
        register_publisher(func2, 'Test')
        register_publisher(func1, 'Test')
        register_publisher(func2, 'Test')

        # now run all publishers
        run_publishers('Test')
        self.assertEqual(called, ['func4', 'func1', 'func2'])

    def test_calling_base_callable_multiple_times(self):
        """testing if calling the base publishers will not call the functions
        more than 1 time
        """
        called = []

        @publisher('Test')
        def func1():
            called.append('func1')

        @publisher('Test')
        def func2():
            called.append('func2')

        @publisher('Test2')
        def func3():
            """another publisher for some other type
            """
            called.append('func3')

        @publisher
        def func4():
            """this should run for everything
            """
            called.append('func4')

        # be sure that the called is still empty
        self.assertEqual(called, [])

        # now run all publishers
        run_publishers()
        self.assertEqual(called, ['func4'])

    def test_callable_is_not_callable(self):
        """testing if the callable is not a callable will raise a TypeError
        """
        with self.assertRaises(TypeError) as cm:
            not_a_callable = 'this is not callable'
            register_publisher(not_a_callable, 'Test')

        self.assertEqual('str is not callable', str(cm.exception))

    def test_registering_to_multiple_types_with_lists(self):
        """testing if it is possible to register one publisher for multiple
        types
        """
        called = []

        @publisher(['Test', 'Test2'])
        def func1():
            called.append('func1')

        @publisher(['Test', 'Test3'])
        def func2():
            called.append('func2')

        @publisher(['Test2', 'Test3'])
        def func3():
            """another publisher for some other type
            """
            called.append('func3')

        @publisher
        def func4():
            """this should run for everything
            """
            called.append('func4')

        # be sure that the called is still empty
        self.assertEqual(called, [])

        # now run all publishers
        called = []
        run_publishers('Test')
        self.assertEqual(called, ['func4', 'func1', 'func2'])

        called = []
        run_publishers('Test2')
        self.assertEqual(called, ['func4', 'func1', 'func3'])

        called = []
        run_publishers('Test3')
        self.assertEqual(called, ['func4', 'func2', 'func3'])
