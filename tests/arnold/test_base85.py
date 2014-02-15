# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
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
            struct.pack('f', 2),
            struct.pack('f', 3.484236717224121),
        ]

        encoded_data = [
            '8TFfd',
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

    def test_arnold_b85_encode_packs_ones_properly(self):
        """testing if arnold_b85_encode is packing ones properly
        """
        raw_data = [
            struct.pack('f', 1.0),
            struct.pack('ffff', 1.0, 1.0, 3.484236717224121, 1.0) 
        ]

        encoded_data = [
            'y',
            'yy8^RH(y'
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
            struct.pack('f', 2),
            struct.pack('f', 3.484236717224121),
        ]

        encoded_data = [
            '8TFfd',
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

    def test_arnold_b85_decode_unpacks_ones_properly(self):
        """testing if arnold_b85_decode is unpacking zeros properly
        """
        raw_data = [
            struct.pack('f', 1.0),
            struct.pack('ffff', 1.0, 1.0, 3.484236717224121, 1.0) 
        ]

        encoded_data = [
            'y',
            'yy8^RH(y'
        ]

        for i in range(len(raw_data)):
            self.assertEqual(
                raw_data[i],
                base85.arnold_b85_decode(encoded_data[i])
            )

    def test_arnold_b85_encoding_real_world_data(self):
        """testing encoding with some real world data
        """
        # b85UINT
        raw_data = [0, 1, 9, 8, 1, 2, 10, 9, 2, 3, 11, 10, 3, 4, 12, 11, 4, 5,
                    13, 12, 5, 6, 14, 13, 6, 7, 15, 14]
        encoded_data = "&UOP6&psb:'7Bt>'Rg1B'n6CF(4ZUJ(P)gN"
        data_format = '%sB' % len(raw_data)
        self.assertEqual(
            encoded_data,
            base85.arnold_b85_encode(struct.pack(data_format, *raw_data))
        )
        self.assertEqual(
            raw_data,
            list(struct.unpack('%sB' % len(raw_data),
                          base85.arnold_b85_decode(encoded_data)))
        )

        # b85POINT2
        raw_data = [0, 0.75, 0.0625, 0.75, 0.125, 0.75, 0.1875, 0.75, 0.25,
                    0.75, 0.3125, 0.75, 0.375, 0.75, 0.4375, 0.75, 0, 1,
                    0.0625, 1, 0.125, 1, 0.1875, 1, 0.25, 1, 0.3125, 1, 0.375,
                    1, 0.4375, 1]
        encoded_data = "z8?r5N7e-P78?r5N7reTb8?r5N8$W,M8?r5N8+HY88?r5N8.koX8" \
                       "?r5N82:0x8?r5N85]GC8?r5Nzy7e-P7y7reTby8$W,My8+HY8y8." \
                       "koXy82:0xy85]GCy"
        data_format = '%sf' % len(raw_data)
        self.assertEqual(
            encoded_data,
            base85.arnold_b85_encode(struct.pack(data_format, *raw_data))
        )
        self.assertEqual(
            raw_data,
            list(struct.unpack('%sf' % len(raw_data),
                          base85.arnold_b85_decode(encoded_data)))
        )

        # b85POINT
        raw_data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                    17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
                    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46,
                    47]
        encoded_data = "zy8TFfd8[8>O8b)k:8eM,Z8hpC%8l>YE8oaoe8qI%u8s0108tl<@" \
                       "8vSGP8x:R`9$v]p9&]i+9(Dt;9)8OC9*,*K9*tZS9+h5[9,[ec9-" \
                       "O@k9.Bps9/6L&90*'.90rW691f2>92YbF93M=N94@mV954H^96'x" \
                       "f96L;j96pSn97?kr97d.v983G%98W_)99&w-99K:199oR59:>j99" \
                       ":c-=9;2EA9;V]E9<%uI9<J8M"
        data_format = '%sf' % len(raw_data)
        self.assertEqual(
            encoded_data,
            base85.arnold_b85_encode(struct.pack(data_format, *raw_data))
        )
        self.assertEqual(
            raw_data,
            list(struct.unpack('%sf' % len(raw_data),
                               base85.arnold_b85_decode(encoded_data)))
        )
