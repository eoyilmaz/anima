# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import unittest2
from anima.previs import File


class FileTestCase(unittest2.TestCase):
    """tests the anima.previs.File class
    """

    def test_duration_argument_skipped(self):
        """testing if the default value will be used when the duration argument
        is skipped
        """
        f = File()
        self.assertEqual(f.duration, 0)

    def test_duration_argument_is_not_an_integer(self):
        """testing if a TypeError will be raised when the duration argument is
        not an integer
        """
        with self.assertRaises(TypeError) as cm:
            File(duration='not an integer')

        self.assertEqual(
            cm.exception.message,
            'File.duration should be an non-negative float, not str'
        )

    def test_duration_attribute_is_not_an_integer(self):
        """testing if a TypeError will be raised when the duration attribute is
        not set to a integer value
        """
        f = File(duration=10)
        with self.assertRaises(TypeError) as cm:
            f.duration = 'not an integer'

        self.assertEqual(
            cm.exception.message,
            'File.duration should be an non-negative float, not str'
        )

    def test_duration_argument_is_negative(self):
        """testing if a ValueError will be raised when the duration argument is
        negative
        """
        with self.assertRaises(ValueError) as cm:
            File(duration=-10)

        self.assertEqual(
            cm.exception.message,
            'File.duration should be an non-negative float'
        )

    def test_duration_attribute_is_negative(self):
        """testing if a ValueError will be raised when the duration attribute
        is set to a negative value
        """
        f = File(duration=10)

        with self.assertRaises(ValueError) as cm:
            f.duration = -10

        self.assertEqual(
            cm.exception.message,
            'File.duration should be an non-negative float'
        )

    def test_duration_argument_is_working_properly(self):
        """testing if the duration argument value is correctly passed to the
        duration attribute
        """
        f = File(duration=10)
        self.assertEqual(10, f.duration)

    def test_duration_attribute_is_working_properly(self):
        """testing if the duration attribute is working properly
        """
        f = File(duration=10)
        f.duration = 15
        self.assertEqual(15, f.duration)

    def test_name_argument_is_skipped(self):
        """testing if the default value will be used when the name argument is
        skipped
        """
        f = File()
        self.assertEqual('', f.name)

    def test_name_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the name argument is not
        a string instance
        """
        with self.assertRaises(TypeError) as cm:
            File(name=123)

        self.assertEqual(
            cm.exception.message,
            'File.name should be a string, not int'
        )

    def test_name_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the name attribute is set
        to a value other than a string
        """
        f = File(name='shot1')
        with self.assertRaises(TypeError) as cm:
            f.name = 123

        self.assertEqual(
            cm.exception.message,
            'File.name should be a string, not int'
        )

    def test_name_argument_is_working_properly(self):
        """testing if the name argument value is correctly passed to the name
        attribute
        """
        f = File(name='shot2')
        self.assertEqual('shot2', f.name)

    def test_name_attribute_is_working_properly(self):
        """testing if the name attribute value can be correctly changed
        """
        f = File(name='shot1')
        test_value = 'shot2'
        self.assertNotEqual(test_value, f.name)
        f.name = test_value
        self.assertEqual(test_value, f.name)

    def test_pathurl_argument_is_skipped(self):
        """testing if the default value will be used when the pathurl argument is
        skipped
        """
        f = File()
        self.assertEqual('', f.pathurl)

    def test_pathurl_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the pathurl argument is not
        a string instance
        """
        with self.assertRaises(TypeError) as cm:
            File(pathurl=123)

        self.assertEqual(
            cm.exception.message,
            'File.pathurl should be a string, not int'
        )

    def test_pathurl_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the pathurl attribute is set
        to a value other than a string
        """
        f = File(pathurl='shot1')
        with self.assertRaises(TypeError) as cm:
            f.pathurl = 123

        self.assertEqual(
            cm.exception.message,
            'File.pathurl should be a string, not int'
        )

    def test_pathurl_argument_is_working_properly(self):
        """testing if the pathurl argument value is correctly passed to the pathurl
        attribute
        """
        f = File(pathurl='shot2')
        self.assertEqual('shot2', f.pathurl)

    def test_pathurl_attribute_is_working_properly(self):
        """testing if the pathurl attribute value can be correctly changed
        """
        f = File(pathurl='shot1')
        test_value = 'shot2'
        self.assertNotEqual(test_value, f.pathurl)
        f.pathurl = test_value
        self.assertEqual(test_value, f.pathurl)









    def test_to_xml_method_is_working_properly(self):
        """testing if the to xml method is working properly
        """
        f = File()
        f.duration = 34.0
        f.name = 'shot2'
        f.pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot2.mov'

        expected_xml = \
            """<file>
  <duration>34.0</duration>
  <name>shot2</name>
  <pathurl>file:///home/eoyilmaz/maya/projects/default/data/shot2.mov</pathurl>
</file>"""

        self.assertEqual(
            expected_xml,
            f.to_xml()
        )

    def test_to_xml_method_is_working_properly_with_tab_with_argument(self):
        """testing if the to xml method is working properly
        """
        f = File()
        f.duration = 34.0
        f.name = 'shot2'
        f.pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot2.mov'

        expected_xml = \
            """  <file>
    <duration>34.0</duration>
    <name>shot2</name>
    <pathurl>file:///home/eoyilmaz/maya/projects/default/data/shot2.mov</pathurl>
  </file>"""

        self.assertEqual(
            expected_xml,
            f.to_xml(indentation=2, pre_indent=2)
        )

    def test_from_xml_method_is_working_properly(self):
        """testing if the from_xml method will fill object attributes from the
        given xml node
        """
        from xml.etree import ElementTree
        file_node = ElementTree.Element('file')
        duration_node = ElementTree.SubElement(file_node, 'duration')
        duration_node.text = '30.0'
        name_node = ElementTree.SubElement(file_node, 'name')
        name_node.text = 'shot'
        pathurl_node = ElementTree.SubElement(file_node, 'pathurl')

        pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot.mov'
        pathurl_node.text = pathurl

        f = File()
        # test starting condition
        self.assertEqual(0.0, f.duration)
        self.assertEqual('', f.name)
        self.assertEqual('', f.pathurl)

        f.from_xml(file_node)
        self.assertEqual(30.0, f.duration)
        self.assertEqual('shot', f.name)
        self.assertEqual(pathurl, f.pathurl)
