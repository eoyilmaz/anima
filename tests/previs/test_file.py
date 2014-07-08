# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import unittest
from anima.env.mayaEnv.extension import File


class FileTestCase(unittest.TestCase):
    """tests the anima.previs.File class
    """

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
