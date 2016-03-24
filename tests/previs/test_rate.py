# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import unittest
from anima.edit import Rate


class RateTestCase(unittest.TestCase):
    """tests the anima.previs.Rate class
    """

    def test_timebase_argument_skipped(self):
        """testing if the default value will be used when the timebase argument
        is skipped
        """
        r = Rate()
        self.assertEqual(r.timebase, '25')

    def test_timebase_argument_is_None(self):
        """testing if the timebase attribute value will be set to the default
        value if the timebase argument is None
        """
        r = Rate(timebase=None)
        self.assertEqual(r.timebase, '25')

    def test_timebase_attribute_is_set_to_None(self):
        """testing if the timebase attribute value will be set to the default
        value if it is set to None
        """
        r = Rate(timebase='25')
        r.timebase = None
        self.assertEqual(r.timebase, '25')

    def test_timebase_argument_is_not_a_str_value(self):
        """testing if a TypeError will be raised when the timebase argument is
        not a string value
        """
        with self.assertRaises(TypeError) as cm:
            Rate(timebase=24)

        self.assertEqual(
            cm.exception.message,
            'Rate.timebase should be a str, not int'
        )

    def test_timebase_attribute_is_not_a_str(self):
        """testing if a TypeError will be raised when the timebase attribute is
        not set to a str
        """
        r = Rate(timebase='12')
        with self.assertRaises(TypeError) as cm:
            r.timebase = 15

        self.assertEqual(
            cm.exception.message,
            'Rate.timebase should be a str, not int'
        )

    def test_timebase_argument_is_working_properly(self):
        """testing if the timebase argument value is correctly passed to the
        timebase attribute
        """
        r = Rate(timebase='12')
        self.assertEqual('12', r.timebase)

    def test_timebase_attribute_is_working_properly(self):
        """testing if the timebase attribute is working properly
        """
        r = Rate(timebase='12')
        r.timebase = '15'
        self.assertEqual('15', r.timebase)

    def test_ntsc_argument_is_skipped(self):
        """testing if the ntsc attribute will be False if the ntsc argument is
        skipped
        """
        r = Rate()
        self.assertFalse(r.ntsc)

    def test_ntsc_argument_is_None(self):
        """testing if the ntsc attribute will be False if the ntsc argument is
        None
        """
        r = Rate()
        self.assertFalse(r.ntsc)

    def test_ntsc_attribute_is_set_to_None(self):
        """testing if the ntsc attribute value will be False if it is set to
        None
        """
        r = Rate(ntsc=True)
        self.assertTrue(r.ntsc)
        r.ntsc = None
        self.assertFalse(r.ntsc)

    def test_ntsc_argument_is_not_a_bool_value(self):
        """testing if a TypeError will be raised when the ntsc argument is not
        a bool
        """
        with self.assertRaises(TypeError) as cm:
            r = Rate(ntsc='not a bool value')

        self.assertEqual(
            str(cm.exception),
            'Rate.ntsc should be a bool value, not str'
        )

    def test_ntsc_attribute_is_set_to_a_non_bool_value(self):
        """testing if a TypeError will be raised when the ntsc attribute is set
        to a non bool value
        """
        r = Rate(ntsc=True)
        with self.assertRaises(TypeError) as cm:
            r.ntsc = 'not a bool value'

        self.assertEqual(
            str(cm.exception),
            'Rate.ntsc should be a bool value, not str'
        )

    def test_ntsc_argument_is_working_properly(self):
        """testing if the ntsc argument value is properly passed to the ntsc
        attribute
        """
        r = Rate(ntsc=True)
        self.assertEqual(r.ntsc, True)

    def test_ntsc_attribute_is_working_properly(self):
        """testing if the ntsc attribute is working properly
        """
        r = Rate(ntsc=True)
        self.assertEqual(r.ntsc, True)
        r.ntsc = False
        self.assertEqual(r.ntsc, False)

    def test_to_xml_method_is_working_properly(self):
        """testing if the to_xml() method is working properly
        """
        r = Rate(timebase='25', ntsc=False)
        self.assertEqual(
            r.to_xml(),
            """<rate>
  <timebase>25</timebase>
  <ntsc>FALSE</ntsc>
</rate>"""
        )

    def test_from_xml_method_is_working_properly(self):
        """testing if the from_xml() method is working properly
        """
        r = Rate(timebase='24', ntsc=False)

        from xml.etree import ElementTree
        rate_node = ElementTree.Element('rate')
        timebase_node = ElementTree.SubElement(rate_node, 'timebase')
        timebase_node.text = '25'
        ntsc_node = ElementTree.SubElement(rate_node, 'ntsc')
        ntsc_node.text = 'TRUE'

        r.from_xml(rate_node)

        self.assertEqual(r.timebase, '25')
        self.assertEqual(r.ntsc, True)
