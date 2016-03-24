# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import unittest
from anima.edit import Clip, File, Rate


class ClipTestCase(unittest.TestCase):
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
            'Clip.id should be a string or unicode, not int'
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
            'Clip.id should be a string or unicode, not int'
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
        f.duration = 34
        f.name = 'shot2'
        f.pathurl = 'file://localhost/home/eoyilmaz/maya/projects/default/data/shot2.mov'

        c = Clip()
        c.id = 'shot2'
        c.start = 1
        c.end = 35
        c.name = 'shot2'
        c.enabled = True
        c.duration = 34
        c.in_ = 0
        c.out = 34
        c.file = f

        expected_xml = \
            """<clipitem id="shot2">
  <end>35</end>
  <name>shot2</name>
  <enabled>True</enabled>
  <start>1</start>
  <in>0</in>
  <duration>34</duration>
  <out>34</out>
  <file id="shot2.mov">
    <duration>34</duration>
    <name>shot2</name>
    <pathurl>file://localhost/home/eoyilmaz/maya/projects/default/data/shot2.mov</pathurl>
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
        end_node.text = '65'
        name_node = ElementTree.SubElement(clip_node, 'name')
        name_node.text = 'shot'
        enabled_node = ElementTree.SubElement(clip_node, 'enabled')
        enabled_node.text = 'True'
        start_node = ElementTree.SubElement(clip_node, 'start')
        start_node.text = '35'
        in_node = ElementTree.SubElement(clip_node, 'in')
        in_node.text = '0'
        duration_node = ElementTree.SubElement(clip_node, 'duration')
        duration_node.text = '30'
        out_node = ElementTree.SubElement(clip_node, 'out')
        out_node.text = '30'

        file_node = ElementTree.SubElement(clip_node, 'file')
        duration_node = ElementTree.SubElement(file_node, 'duration')
        duration_node.text = '30'
        name_node = ElementTree.SubElement(file_node, 'name')
        name_node.text = 'shot'
        pathurl_node = ElementTree.SubElement(file_node, 'pathurl')

        pathurl = 'file://localhost/home/eoyilmaz/maya/projects/default/data/shot.mov'
        pathurl_node.text = pathurl

        c = Clip()
        c.from_xml(clip_node)
        self.assertEqual(65, c.end)
        self.assertEqual('shot', c.name)
        self.assertEqual(True, c.enabled)
        self.assertEqual(35, c.start)
        self.assertEqual(0, c.in_)
        self.assertEqual(30, c.duration)
        self.assertEqual(30, c.out)

        f = c.file
        self.assertEqual(30, f.duration)
        self.assertEqual('shot', f.name)
        self.assertEqual(pathurl, f.pathurl)

    def test_from_xml_method_is_working_properly_with_no_file(self):
        """testing if the from_xml method will fill object attributes from the
        given xml node even there is no file node inside
        """
        from xml.etree import ElementTree
        clip_node = ElementTree.Element('clipitem', attrib={'id': 'shot'})
        end_node = ElementTree.SubElement(clip_node, 'end')
        end_node.text = '65'
        name_node = ElementTree.SubElement(clip_node, 'name')
        name_node.text = 'shot'
        enabled_node = ElementTree.SubElement(clip_node, 'enabled')
        enabled_node.text = 'True'
        start_node = ElementTree.SubElement(clip_node, 'start')
        start_node.text = '35'
        in_node = ElementTree.SubElement(clip_node, 'in')
        in_node.text = '0'
        duration_node = ElementTree.SubElement(clip_node, 'duration')
        duration_node.text = '30'
        out_node = ElementTree.SubElement(clip_node, 'out')
        out_node.text = '30'

        c = Clip()
        c.from_xml(clip_node)
        self.assertEqual(65, c.end)
        self.assertEqual('shot', c.name)
        self.assertEqual(True, c.enabled)
        self.assertEqual(35, c.start)
        self.assertEqual(0, c.in_)
        self.assertEqual(30, c.duration)
        self.assertEqual(30, c.out)

    def test_rate_argument_is_skipped(self):
        """testing if the rate attribute value will be a Rate instance with
        default timebase value if the rate argument is skipped
        """
        c = Clip()
        self.assertIsNone(c.rate)

    def test_rate_argument_is_None(self):
        """testing if the rate attribute will be None if the rate argument is
        None
        """
        c = Clip(rate=None)
        rate = c.rate
        self.assertIsNone(rate)

    def tst_rate_attribute_is_None(self):
        """testing if the rate attribute can be set to None
        """
        from anima.edit import Rate
        r = Rate(timebase='24', ntsc=False)
        c = Clip(rate=r)
        self.assertIsNotNone(c.rate)
        c.rate = None
        self.assertIsNone(c.rate)

    def test_rate_attribute_is_None_to_xml_is_working_properly(self):
        """testing if the rate attribute will not be included int the xml
        output if it is None
        """
        f = File()
        f.duration = 34
        f.name = 'shot2'
        f.pathurl = 'file://localhost/home/eoyilmaz/maya/projects/default/data/shot2.mov'

        c = Clip()
        c.id = 'shot2'
        c.start = 1
        c.end = 35
        c.name = 'shot2'
        c.enabled = True
        c.duration = 34
        c.in_ = 0
        c.out = 34
        c.file = f
        c.rate = None

        expected_xml = \
            """<clipitem id="shot2">
  <end>35</end>
  <name>shot2</name>
  <enabled>True</enabled>
  <start>1</start>
  <in>0</in>
  <duration>34</duration>
  <out>34</out>
  <file id="shot2.mov">
    <duration>34</duration>
    <name>shot2</name>
    <pathurl>file://localhost/home/eoyilmaz/maya/projects/default/data/shot2.mov</pathurl>
  </file>
</clipitem>"""

        self.maxDiff = None
        self.assertEqual(
            expected_xml,
            c.to_xml()
        )

    def test_rate_attribute_is_valid_to_xml_is_working_properly(self):
        """testing if the rate attribute will be included int the xml output if
        it is not None
        """
        f = File()
        f.duration = 34
        f.name = 'shot2'
        f.pathurl = 'file://localhost/home/eoyilmaz/maya/projects/default/data/shot2.mov'

        c = Clip()
        c.id = 'shot2'
        c.start = 1
        c.end = 35
        c.name = 'shot2'
        c.enabled = True
        c.duration = 34
        c.in_ = 0
        c.out = 34
        c.file = f
        c.rate = Rate(timebase='25')

        expected_xml = \
            """<clipitem id="shot2">
  <end>35</end>
  <name>shot2</name>
  <enabled>True</enabled>
  <start>1</start>
  <in>0</in>
  <duration>34</duration>
  <rate>
    <timebase>25</timebase>
    <ntsc>FALSE</ntsc>
  </rate>
  <out>34</out>
  <file id="shot2.mov">
    <duration>34</duration>
    <name>shot2</name>
    <pathurl>file://localhost/home/eoyilmaz/maya/projects/default/data/shot2.mov</pathurl>
  </file>
</clipitem>"""

        self.maxDiff = None
        self.assertEqual(
            expected_xml,
            c.to_xml()
        )


        # def test_in_is_bigger_than_out_will_be_converted_to_negative_values(self):
    #     """testing if setting the in smaller than out will convert the in to
    #     a negative value
    #     """
    #     c = Clip()
    #     c.in_ = 2073577
    #     c.out = 191
    # 
    #     self.assertEqual(c.in_, -23)
