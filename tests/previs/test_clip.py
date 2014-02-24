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

    def test_id_argument_is_skipped(self):
        """testing if the default value will be used when the id argument is
        skipped
        """
        c = Clip()
        self.assertEqual('', c.id)

    def test_id_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the id argument is not
        a string instance
        """
        with self.assertRaises(TypeError) as cm:
            Clip(id=123)

        self.assertEqual(
            cm.exception.message,
            'Clip.id should be a string, not int'
        )

    def test_id_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the id attribute is set
        to a value other than a string
        """
        c = Clip(id='shot1')
        with self.assertRaises(TypeError) as cm:
            c.id = 123

        self.assertEqual(
            cm.exception.message,
            'Clip.id should be a string, not int'
        )

    def test_id_argument_is_working_properly(self):
        """testing if the id argument value is correctly passed to the id
        attribute
        """
        c = Clip(id='shot2')
        self.assertEqual('shot2', c.id)

    def test_id_attribute_is_working_properly(self):
        """testing if the id attribute value can be correctly changed
        """
        c = Clip(id='shot1')
        test_value = 'shot2'
        self.assertNotEqual(test_value, c.id)
        c.id = test_value
        self.assertEqual(test_value, c.id)

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

    def test_from_xml_method_is_working_properly(self):
        """testing if the from_xml method will fill object attributes from the
        given xml node
        """
        from xml.etree import ElementTree
        clip_node = ElementTree.Element('clipitem', attrib={'id': 'shot'})
        end_node = ElementTree.SubElement(clip_node, 'end')
        end_node.text = '65.0'
        name_node = ElementTree.SubElement(clip_node, 'name')
        name_node.text = 'shot'
        enabled_node = ElementTree.SubElement(clip_node, 'enabled')
        enabled_node.text = 'True'
        start_node = ElementTree.SubElement(clip_node, 'start')
        start_node.text = '35.0'
        in_node = ElementTree.SubElement(clip_node, 'in')
        in_node.text = '0.0'
        duration_node = ElementTree.SubElement(clip_node, 'duration')
        duration_node.text = '30.0'
        out_node = ElementTree.SubElement(clip_node, 'out')
        out_node.text = '30.0'

        file_node = ElementTree.SubElement(clip_node, 'file')
        duration_node = ElementTree.SubElement(file_node, 'duration')
        duration_node.text = '30.0'
        name_node = ElementTree.SubElement(file_node, 'name')
        name_node.text = 'shot'
        pathurl_node = ElementTree.SubElement(file_node, 'pathurl')

        pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot.mov'
        pathurl_node.text = pathurl

        c = Clip()
        c.from_xml(clip_node)
        self.assertEqual(65.0, c.end)
        self.assertEqual('shot', c.name)
        self.assertEqual(True, c.enabled)
        self.assertEqual(35.0, c.start)
        self.assertEqual(0.0, c.in_)
        self.assertEqual(30.0, c.duration)
        self.assertEqual(30.0, c.out)

        f = c.file
        self.assertEqual(30.0, f.duration)
        self.assertEqual('shot', f.name)
        self.assertEqual(pathurl, f.pathurl)
