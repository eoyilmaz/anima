# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import unittest2
from anima.previs import Clip, File


class ClipTestCase(unittest2.TestCase):
    """tests the anima.previs.Clip class
    """

    def test_id_argument_skipped(self):
        """testing if the default value will be used when the id argument
        is skipped
        """
        self.fail('test is not implemented yet')

    def test_id_argument_is_not_an_string(self):
        """testing if a TypeError will be raised when the id argument is
        not an string
        """
        self.fail('test is not implemented yet')

    def test_id_attribute_is_not_an_string(self):
        """testing if a TypeError will be raised when the id attribute is
        not set to a string value
        """
        self.fail('test is not implemented yet')

    def test_id_argument_is_working_properly(self):
        """testing if the id argument value is correctly passed to the
        id attribute
        """
        self.fail('test is not implemented yet')

    def test_id_attribute_is_working_properly(self):
        """testing if the id attribute is working properly
        """
        self.fail('test is not implemented yet')

    def test_name_argument_is_skipped(self):
        """testing if the default value will be used when the name argument is
        skipped
        """
        self.fail('test is not implemented yet')

    def test_name_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the name argument is not
        a string instance
        """
        self.fail('test is not implemented yet')

    def test_name_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the name attribute is set
        to a value other than a string
        """
        self.fail('test is not implemented yet')

    def test_name_argument_is_working_properly(self):
        """testing if the name argument value is correctly passed to the name
        attribute
        """
        self.fail('test is not implemented yet')

    def test_name_attribute_is_working_properly(self):
        """testing if the name attribute value can be correctly changed
        """
        self.fail('test is not implemented yet')

    def test_to_xml_method_is_working_properly(self):
        """testing if the to xml method is working properly
        """
        f = File()
        f.duration = 34.0
        f.name = 'shot2'
        f.pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot2.mov'

        c = Clip()
        c.id = 'shot2'
        c.start = 1.0
        c.end = 35.0
        c.name = 'shot2'
        c.enabled = True
        c.duration = 34.0
        c.in_ = 0.0
        c.out = 34.0
        c.file = f

        expected_xml = \
            """<clipitem id="shot2">
  <end>35.0</end>
  <name>shot2</name>
  <enabled>True</enabled>
  <start>1.0</start>
  <in>0.0</in>
  <duration>34.0</duration>
  <out>34.0</out>
  <file>
    <duration>34.0</duration>
    <name>shot2</name>
    <pathurl>file:///home/eoyilmaz/maya/projects/default/data/shot2.mov</pathurl>
  </file>
</clipitem>"""

        self.assertEqual(
            expected_xml,
            c.to_xml()
        )
