# -*- coding: utf-8 -*-

import unittest
from anima.edit import NameMixin


class NameAttrMixinTestCase(unittest.TestCase):
    """tests the anima.previs.NameMixin class
    """

    def test_name_argument_is_skipped(self):
        """testing if the default value will be used when the name argument is
        skipped
        """
        n = NameMixin()
        self.assertEqual('', n.name)

    def test_name_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the name argument is not
        a string instance
        """
        with self.assertRaises(TypeError) as cm:
            NameMixin(name=123)

        self.assertEqual(
            cm.exception.message,
            'NameMixin.name should be a string or unicode, not int'
        )

    def test_name_attribute_is_not_a_string(self):
        """testing if a TypeError will be raised when the name attribute is set
        to a value other than a string
        """
        n = NameMixin(name='shot1')
        with self.assertRaises(TypeError) as cm:
            n.name = 123

        self.assertEqual(
            cm.exception.message,
            'NameMixin.name should be a string or unicode, not int'
        )

    def test_name_argument_is_working_properly(self):
        """testing if the name argument value is correctly passed to the name
        attribute
        """
        n = NameMixin(name='shot2')
        self.assertEqual('shot2', n.name)

    def test_name_attribute_is_working_properly(self):
        """testing if the name attribute value can be correctly changed
        """
        n = NameMixin(name='shot1')
        test_value = 'shot2'
        self.assertNotEqual(test_value, n.name)
        n.name = test_value
        self.assertEqual(test_value, n.name)
