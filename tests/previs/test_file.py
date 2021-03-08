# -*- coding: utf-8 -*-

import unittest
from anima.edit import File


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
        """testing if the pathurl argument value is correctly passed to the
        pathurl
        attribute
        """
        f = File(pathurl='shot2')
        self.assertEqual('file://localhost/shot2', f.pathurl)

    def test_pathurl_will_set_the_id_attribute(self):
        """testing if setting the pathurl attribute will also set the id
        attribute
        """
        f = File()
        self.assertEqual(f.id, '')
        f.pathurl = 'shot2'
        self.assertEqual(f.id, 'shot2')

    def test_pathurl_attribute_is_working_properly(self):
        """testing if the pathurl attribute value can be correctly changed
        """
        f = File(pathurl='shot1')
        test_value = 'shot2'
        expected_value = 'file://localhost/shot2'
        self.assertNotEqual(test_value, f.pathurl)
        f.pathurl = test_value
        self.assertEqual(expected_value, f.pathurl)

    def test_to_xml_method_is_working_properly(self):
        """testing if the to xml method is working properly
        """
        f = File()
        f.duration = 34
        f.name = 'shot2'
        f.pathurl = 'file://localhost/home/eoyilmaz/maya/projects/default/data/' \
                    'shot2.mov'

        expected_xml = \
            """<file id="shot2.mov">
  <duration>34</duration>
  <name>shot2</name>
  <pathurl>file://localhost/home/eoyilmaz/maya/projects/default/data/shot2.mov</pathurl>
</file>"""

        self.assertEqual(
            expected_xml,
            f.to_xml()
        )

    def test_to_xml_method_is_working_properly_with_tab_with_argument(self):
        """testing if the to xml method is working properly
        """
        f = File()
        f.duration = 34
        f.name = 'shot2'
        f.pathurl = 'file://localhost/home/eoyilmaz/maya/projects/default/' \
                    'data/shot2.mov'

        expected_xml = \
            """  <file id="shot2.mov">
    <duration>34</duration>
    <name>shot2</name>
    <pathurl>file://localhost/home/eoyilmaz/maya/projects/default/data/shot2.mov</pathurl>
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
        duration_node.text = '30'
        name_node = ElementTree.SubElement(file_node, 'name')
        name_node.text = 'shot'
        pathurl_node = ElementTree.SubElement(file_node, 'pathurl')

        pathurl = 'file://localhost/' \
                  'home/eoyilmaz/maya/projects/default/data/shot.mov'
        pathurl_node.text = pathurl

        f = File()
        # test starting condition
        self.assertEqual(0, f.duration)
        self.assertEqual('', f.name)
        self.assertEqual('', f.pathurl)

        f.from_xml(file_node)
        self.assertEqual(30, f.duration)
        self.assertEqual('shot', f.name)
        self.assertEqual(pathurl, f.pathurl)

    def test_id_is_generated_from_pathurl(self):
        """testing if the id attribute is generated from pathurl and it is
        equal to the file name
        """
        f = File(
            pathurl='file://localhost/S:/KKS/Sequences/SEQ001/001A_TNGE/Shots'
                    '/Seq001_001A_TNGE_0010/Comp/Outputs/Main/v001/exr/'
                    'KKS_Seq001_001A_TNGE_0010_Comp_Main_v001.%5B000-379%5D'
                    '.exr'
        )
        expected_result = 'KKS_Seq001_001A_TNGE_0010_Comp_Main_v001.' \
                          '[000-379].exr'
        self.assertEqual(expected_result, f.id)

    def test_id_after_a_second_call_to_to_xml_will_change_id_id(self):
        """testing if the id attribute will be changed to an element with just
        id attribute
        """
        f = File(
            pathurl='file://localhost/S:/KKS/Sequences/SEQ001/001A_TNGE/Shots'
                    '/Seq001_001A_TNGE_0010/Comp/Outputs/Main/v001/exr/'
                    'KKS_Seq001_001A_TNGE_0010_Comp_Main_v001.%5B000-379%5D'
                    '.exr'
        )
        # the first call
        call1 = f.to_xml()
        # the second call
        call2 = f.to_xml()
        # the third call
        call3 = f.to_xml()

        # now the first call should be different than the others
        self.assertNotEqual(call1, call2)
        # but the second and third call should be the same
        self.assertEqual(call2, call3)
        # and it should be a file element with just the id attribute
        self.assertEqual(
            call2,
            '<file id="%s"/>' % f.id
        )
