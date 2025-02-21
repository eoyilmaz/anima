# -*- coding: utf-8 -*-

import unittest
from anima.edit import DurationMixin


class DurationAttrMixinTestCase(unittest.TestCase):
    """tests the anima.previs.DurationMixin class"""

    def test_duration_argument_skipped(self):
        """default value will be used when the duration argument
        is skipped
        """
        d = DurationMixin()
        self.assertEqual(d.duration, 0)

    def test_duration_argument_is_not_an_integer(self):
        """a TypeError will be raised when the duration argument is
        not an integer
        """
        with self.assertRaises(TypeError) as cm:
            DurationMixin(duration="not an integer")

        self.assertEqual(
            cm.exception.message,
            "DurationMixin.duration should be an non-negative float, not str",
        )

    def test_duration_attribute_is_not_an_integer(self):
        """a TypeError will be raised when the duration attribute is
        not set to a integer value
        """
        d = DurationMixin(duration=10)
        with self.assertRaises(TypeError) as cm:
            d.duration = "not an integer"

        self.assertEqual(
            cm.exception.message,
            "DurationMixin.duration should be an non-negative float, not str",
        )

    def test_duration_argument_is_negative(self):
        """a ValueError will be raised when the duration argument is
        negative
        """
        with self.assertRaises(ValueError) as cm:
            DurationMixin(duration=-10)

        self.assertEqual(
            cm.exception.message,
            "DurationMixin.duration should be an non-negative float",
        )

    def test_duration_attribute_is_negative(self):
        """a ValueError will be raised when the duration attribute
        is set to a negative value
        """
        d = DurationMixin(duration=10)

        with self.assertRaises(ValueError) as cm:
            d.duration = -10

        self.assertEqual(
            cm.exception.message,
            "DurationMixin.duration should be an non-negative float",
        )

    def test_duration_argument_is_working_properly(self):
        """duration argument value is correctly passed to the
        duration attribute
        """
        d = DurationMixin(duration=10)
        self.assertEqual(10, d.duration)

    def test_duration_attribute_is_working_properly(self):
        """duration attribute is working properly"""
        d = DurationMixin(duration=10)
        d.duration = 15
        self.assertEqual(15, d.duration)
