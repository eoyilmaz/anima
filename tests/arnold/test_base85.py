# -*- coding: utf-8 -*-

from anima.render.arnold import base85
import struct
import pytest


@pytest.mark.parametrize(
    "raw_data, encoded_data",
    [
        (struct.pack(b"f", 2), b"8TFfd"),
        (struct.pack(b"f", 3.484236717224121), b"8^RH("),
    ],
)
def test_arnold_b85_encode_is_working_properly(raw_data, encoded_data):
    """testing if arnold_b85_encode is working properly"""
    assert encoded_data == base85.arnold_b85_encode(raw_data)


@pytest.mark.parametrize(
    "raw_data, encoded_data",
    [
        (struct.pack(b"f", 0.0), b"z"),
        (struct.pack(b"ffff", 0.0, 0.0, 3.484236717224121, 0.0), b"zz8^RH(z"),
    ],
)
def test_arnold_b85_encode_packs_zeros_properly(raw_data, encoded_data):
    """testing if arnold_b85_encode is packing zeros properly"""
    assert encoded_data == base85.arnold_b85_encode(raw_data)


@pytest.mark.parametrize(
    "raw_data, encoded_data",
    [
        (struct.pack(b"f", 1.0), b"y"),
        (struct.pack(b"ffff", 1.0, 1.0, 3.484236717224121, 1.0), b"yy8^RH(y"),
    ],
)
def test_arnold_b85_encode_packs_ones_properly(raw_data, encoded_data):
    """testing if arnold_b85_encode is packing ones properly"""
    assert encoded_data == base85.arnold_b85_encode(raw_data)


@pytest.mark.parametrize(
    "raw_data, encoded_data",
    [
        (struct.pack(b"f", 2), b"8TFfd"),
        (struct.pack(b"f", 3.484236717224121), b"8^RH("),
    ],
)
def test_arnold_b85_decode_is_working_properly(raw_data, encoded_data):
    """testing if arnold_b85_decode is working properly"""
    assert raw_data == base85.arnold_b85_decode(encoded_data)


@pytest.mark.parametrize(
    "raw_data, encoded_data",
    [
        (struct.pack(b"f", 0.0), b"z"),
        (struct.pack(b"ffff", 0.0, 0.0, 3.484236717224121, 0.0), b"zz8^RH(z"),
    ],
)
def test_arnold_b85_decode_unpacks_zeros_properly(raw_data, encoded_data):
    """testing if arnold_b85_decode is unpacking zeros properly"""
    assert raw_data == base85.arnold_b85_decode(encoded_data)


@pytest.mark.parametrize(
    "raw_data, encoded_data",
    [
        (struct.pack(b"f", 1.0), b"y"),
        (struct.pack(b"ffff", 1.0, 1.0, 3.484236717224121, 1.0), b"yy8^RH(y"),
    ],
)
def test_arnold_b85_decode_unpacks_ones_properly(raw_data, encoded_data):
    """testing if arnold_b85_decode is unpacking zeros properly"""
    assert raw_data == base85.arnold_b85_decode(encoded_data)


@pytest.mark.parametrize(
    "raw_data, encoded_data, format_template",
    [
        # b85UINT
        (
            [
                0,
                1,
                9,
                8,
                1,
                2,
                10,
                9,
                2,
                3,
                11,
                10,
                3,
                4,
                12,
                11,
                4,
                5,
                13,
                12,
                5,
                6,
                14,
                13,
                6,
                7,
                15,
                14,
            ],
            b"&UOP6&psb:'7Bt>'Rg1B'n6CF(4ZUJ(P)gN",
            b"%sB",
        ),
        # b85POINT2
        (
            [
                0,
                0.75,
                0.0625,
                0.75,
                0.125,
                0.75,
                0.1875,
                0.75,
                0.25,
                0.75,
                0.3125,
                0.75,
                0.375,
                0.75,
                0.4375,
                0.75,
                0,
                1,
                0.0625,
                1,
                0.125,
                1,
                0.1875,
                1,
                0.25,
                1,
                0.3125,
                1,
                0.375,
                1,
                0.4375,
                1,
            ],
            b"z8?r5N7e-P78?r5N7reTb8?r5N8$W,M8?r5N8+HY88?r5N8.koX8"
            b"?r5N82:0x8?r5N85]GC8?r5Nzy7e-P7y7reTby8$W,My8+HY8y8."
            b"koXy82:0xy85]GCy",
            b"%sf",
        ),
        # b85POINT
        (
            list(range(48)),
            b"zy8TFfd8[8>O8b)k:8eM,Z8hpC%8l>YE8oaoe8qI%u8s0108tl<@"
            b"8vSGP8x:R`9$v]p9&]i+9(Dt;9)8OC9*,*K9*tZS9+h5[9,[ec9-"
            b"O@k9.Bps9/6L&90*'.90rW691f2>92YbF93M=N94@mV954H^96'x"
            b"f96L;j96pSn97?kr97d.v983G%98W_)99&w-99K:199oR59:>j99"
            b":c-=9;2EA9;V]E9<%uI9<J8M",
            b"%sf",
        ),
    ],
)
def test_arnold_b85_encoding_real_world_data(raw_data, encoded_data, format_template):
    """testing encoding with some real world data"""
    data_format = format_template % str(len(raw_data)).encode()
    assert encoded_data == base85.arnold_b85_encode(struct.pack(data_format, *raw_data))
    assert raw_data == list(
        struct.unpack(
            format_template % str(len(raw_data)).encode(),
            base85.arnold_b85_decode(encoded_data),
        )
    )
