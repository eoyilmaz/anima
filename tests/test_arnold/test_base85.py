# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
# 
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima.render.arnold import base85
import unittest2
import struct

class Base85TestCase(unittest2.TestCase):
    """tests the base85 module
    """

    def setup(self):
        """setup the test
        """
        pass

    def test_arnold_b85_encode_is_working_properly(self):
        """testing if arnold_b85_encode is working properly
        """
        raw_data = [
            struct.pack('f', 1),
            struct.pack('f', 3.484236717224121),
        ]

        encoded_data = [
            '8Fcb9',
            '8^RH(',
        ]

        for i in range(len(raw_data)):
            self.assertEqual(
                encoded_data[i],
                base85.arnold_b85_encode(raw_data[i])
            )

    def test_arnold_b85_encode_packs_zeros_properly(self):
        """testing if arnold_b85_encode is packing zeros properly
        """
        raw_data = [
            struct.pack('f', 0.0),
            struct.pack('ffff', 0.0, 0.0, 3.484236717224121, 0.0) 
        ]

        encoded_data = [
            'z',
            'zz8^RH(z'
        ]

        for i in range(len(raw_data)):
            self.assertEqual(
                encoded_data[i],
                base85.arnold_b85_encode(raw_data[i])
            )

    def test_arnold_b85_decode_is_working_properly(self):
        """testing if arnold_b85_decode is working properly
        """
        raw_data = [
            struct.pack('f', 1),
            struct.pack('f', 3.484236717224121),
        ]

        encoded_data = [
            '8Fcb9',
            '8^RH(',
        ]

        for i in range(len(raw_data)):
            self.assertEqual(
                raw_data[i],
                base85.arnold_b85_decode(encoded_data[i])
            )

    def test_arnold_b85_decode_unpacks_zeros_properly(self):
        """testing if arnold_b85_decode is unpacking zeros properly
        """
        raw_data = [
            struct.pack('f', 0.0),
            struct.pack('ffff', 0.0, 0.0, 3.484236717224121, 0.0) 
        ]

        encoded_data = [
            'z',
            'zz8^RH(z'
        ]

        for i in range(len(raw_data)):
            self.assertEqual(
                raw_data[i],
                base85.arnold_b85_decode(encoded_data[i])
            )

