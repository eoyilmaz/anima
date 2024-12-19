# -*- coding: utf-8 -*-

import struct


LUTS = {
    "standard": {
        "byte_order": b"!",
        "char_to_int": {
            b"!": 0,
            b"#": 2,
            b'"': 1,
            b"%": 4,
            b"$": 3,
            b"'": 6,
            b"&": 5,
            b")": 8,
            b"(": 7,
            b"+": 10,
            b"*": 9,
            b"-": 12,
            b",": 11,
            b"/": 14,
            b".": 13,
            b"1": 16,
            b"0": 15,
            b"3": 18,
            b"2": 17,
            b"5": 20,
            b"4": 19,
            b"7": 22,
            b"6": 21,
            b"9": 24,
            b"8": 23,
            b";": 26,
            b":": 25,
            b"=": 28,
            b"<": 27,
            b"?": 30,
            b">": 29,
            b"A": 32,
            b"@": 31,
            b"C": 34,
            b"B": 33,
            b"E": 36,
            b"D": 35,
            b"G": 38,
            b"F": 37,
            b"I": 40,
            b"H": 39,
            b"K": 42,
            b"J": 41,
            b"M": 44,
            b"L": 43,
            b"O": 46,
            b"N": 45,
            b"Q": 48,
            b"P": 47,
            b"S": 50,
            b"R": 49,
            b"U": 52,
            b"T": 51,
            b"W": 54,
            b"V": 53,
            b"Y": 56,
            b"X": 55,
            b"[": 58,
            b"Z": 57,
            b"]": 60,
            b"\\": 59,
            b"_": 62,
            b"^": 61,
            b"a": 64,
            b"`": 63,
            b"c": 66,
            b"b": 65,
            b"e": 68,
            b"d": 67,
            b"g": 70,
            b"f": 69,
            b"i": 72,
            b"h": 71,
            b"k": 74,
            b"j": 73,
            b"m": 76,
            b"l": 75,
            b"o": 78,
            b"n": 77,
            b"q": 80,
            b"p": 79,
            b"s": 82,
            b"r": 81,
            b"u": 84,
            b"t": 83,
        },
        "int_to_char": [
            b"!",
            b'"',
            b"#",
            b"$",
            b"%",
            b"&",
            b"'",
            b"(",
            b")",
            b"*",
            b"+",
            b",",
            b"-",
            b".",
            b"/",
            b"0",
            b"1",
            b"2",
            b"3",
            b"4",
            b"5",
            b"6",
            b"7",
            b"8",
            b"9",
            b":",
            b";",
            b"<",
            b"=",
            b">",
            b"?",
            b"@",
            b"A",
            b"B",
            b"C",
            b"D",
            b"E",
            b"F",
            b"G",
            b"H",
            b"I",
            b"J",
            b"K",
            b"L",
            b"M",
            b"N",
            b"O",
            b"P",
            b"Q",
            b"R",
            b"S",
            b"T",
            b"U",
            b"V",
            b"W",
            b"X",
            b"Y",
            b"Z",
            b"[",
            b"\\",
            b"]",
            b"^",
            b"_",
            b"`",
            b"a",
            b"b",
            b"c",
            b"d",
            b"e",
            b"f",
            b"g",
            b"h",
            b"i",
            b"j",
            b"k",
            b"l",
            b"m",
            b"n",
            b"o",
            b"p",
            b"q",
            b"r",
            b"s",
            b"t",
            b"u",
        ],
    },
    "rfc1924": {
        "byte_order": b"!",
        "char_to_int": {
            b"0": 0,
            b"1": 1,
            b"2": 2,
            b"3": 3,
            b"4": 4,
            b"5": 5,
            b"6": 6,
            b"7": 7,
            b"8": 8,
            b"9": 9,
            b"A": 10,
            b"B": 11,
            b"C": 12,
            b"D": 13,
            b"E": 14,
            b"F": 15,
            b"G": 16,
            b"H": 17,
            b"I": 18,
            b"J": 19,
            b"K": 20,
            b"L": 21,
            b"M": 22,
            b"N": 23,
            b"O": 24,
            b"P": 25,
            b"Q": 26,
            b"R": 27,
            b"S": 28,
            b"T": 29,
            b"U": 30,
            b"V": 31,
            b"W": 32,
            b"X": 33,
            b"Y": 34,
            b"Z": 35,
            b"a": 36,
            b"b": 37,
            b"c": 38,
            b"d": 39,
            b"e": 40,
            b"f": 41,
            b"g": 42,
            b"h": 43,
            b"i": 44,
            b"j": 45,
            b"k": 46,
            b"l": 47,
            b"m": 48,
            b"n": 49,
            b"o": 50,
            b"p": 51,
            b"q": 52,
            b"r": 53,
            b"s": 54,
            b"t": 55,
            b"u": 56,
            b"v": 57,
            b"w": 58,
            b"x": 59,
            b"y": 60,
            b"z": 61,
            b"!": 62,
            b"#": 63,
            b"$": 64,
            b"%": 65,
            b"&": 66,
            b"(": 67,
            b")": 68,
            b"*": 69,
            b"+": 70,
            b"-": 71,
            b";": 72,
            b"<": 73,
            b"=": 74,
            b">": 75,
            b"?": 76,
            b"@": 77,
            b"^": 78,
            b"_": 79,
            b"`": 80,
            b"{": 81,
            b"|": 82,
            b"}": 83,
            b"~": 84,
        },
        "int_to_char": [
            b"0",
            b"1",
            b"2",
            b"3",
            b"4",
            b"5",
            b"6",
            b"7",
            b"8",
            b"9",
            b"A",
            b"B",
            b"C",
            b"D",
            b"E",
            b"F",
            b"G",
            b"H",
            b"I",
            b"J",
            b"K",
            b"L",
            b"M",
            b"N",
            b"O",
            b"P",
            b"Q",
            b"R",
            b"S",
            b"T",
            b"U",
            b"V",
            b"W",
            b"X",
            b"Y",
            b"Z",
            b"a",
            b"b",
            b"c",
            b"d",
            b"e",
            b"f",
            b"g",
            b"h",
            b"i",
            b"j",
            b"k",
            b"l",
            b"m",
            b"n",
            b"o",
            b"p",
            b"q",
            b"r",
            b"s",
            b"t",
            b"u",
            b"v",
            b"w",
            b"x",
            b"y",
            b"z",
            b"!",
            b"#",
            b"$",
            b"%",
            b"&",
            b"(",
            b")",
            b"*",
            b"+",
            b"-",
            b";",
            b"<",
            b"=",
            b">",
            b"?",
            b"@",
            b"^",
            b"_",
            b"`",
            b"{",
            b"|",
            b"}",
            b"~",
        ],
    },
    "arnold": {
        "byte_order": b"<",
        "expansion_char": b"!",
        "special_values": {b"$$$$$": b"z", b"8Fcb9": b"y"},  # 0.0  # 1.0
        "char_to_int": {
            b"%": 1,
            b"$": 0,
            b"'": 3,
            b"&": 2,
            b")": 5,
            b"(": 4,
            b"+": 7,
            b"*": 6,
            b"-": 9,
            b",": 8,
            b"/": 11,
            b".": 10,
            b"1": 13,
            b"0": 12,
            b"3": 15,
            b"2": 14,
            b"5": 17,
            b"4": 16,
            b"7": 19,
            b"6": 18,
            b"9": 21,
            b"8": 20,
            b";": 23,
            b":": 22,
            b"=": 25,
            b"<": 24,
            b"?": 27,
            b">": 26,
            b"A": 29,
            b"@": 28,
            b"C": 31,
            b"B": 30,
            b"E": 33,
            b"D": 32,
            b"G": 35,
            b"F": 34,
            b"I": 37,
            b"H": 36,
            b"K": 39,
            b"J": 38,
            b"M": 41,
            b"L": 40,
            b"O": 43,
            b"N": 42,
            b"Q": 45,
            b"P": 44,
            b"S": 47,
            b"R": 46,
            b"U": 49,
            b"T": 48,
            b"W": 51,
            b"V": 50,
            b"Y": 53,
            b"X": 52,
            b"[": 55,
            b"Z": 54,
            b"]": 57,
            b"\\": 56,
            b"_": 59,
            b"^": 58,
            b"a": 61,
            b"`": 60,
            b"c": 63,
            b"b": 62,
            b"e": 65,
            b"d": 64,
            b"g": 67,
            b"f": 66,
            b"i": 69,
            b"h": 68,
            b"k": 71,
            b"j": 70,
            b"m": 73,
            b"l": 72,
            b"o": 75,
            b"n": 74,
            b"q": 77,
            b"p": 76,
            b"s": 79,
            b"r": 78,
            b"u": 81,
            b"t": 80,
            b"w": 83,
            b"v": 82,
            b"x": 84,
        },
        "int_to_char": [
            b"$",
            b"%",
            b"&",
            b"'",
            b"(",
            b")",
            b"*",
            b"+",
            b",",
            b"-",
            b".",
            b"/",
            b"0",
            b"1",
            b"2",
            b"3",
            b"4",
            b"5",
            b"6",
            b"7",
            b"8",
            b"9",
            b":",
            b";",
            b"<",
            b"=",
            b">",
            b"?",
            b"@",
            b"A",
            b"B",
            b"C",
            b"D",
            b"E",
            b"F",
            b"G",
            b"H",
            b"I",
            b"J",
            b"K",
            b"L",
            b"M",
            b"N",
            b"O",
            b"P",
            b"Q",
            b"R",
            b"S",
            b"T",
            b"U",
            b"V",
            b"W",
            b"X",
            b"Y",
            b"Z",
            b"[",
            b"\\",
            b"]",
            b"^",
            b"_",
            b"`",
            b"a",
            b"b",
            b"c",
            b"d",
            b"e",
            b"f",
            b"g",
            b"h",
            b"i",
            b"j",
            b"k",
            b"l",
            b"m",
            b"n",
            b"o",
            b"p",
            b"q",
            b"r",
            b"s",
            b"t",
            b"u",
            b"v",
            b"w",
            b"x",
        ],
    },
}


def __b85_encode(data, lut, byte_order, special_values=None):
    """Encode the given bytes data in to Base85 using the given LUT.

    Args:
        data (bytes): A string which contains a string to be encoded in Base85.
        lut (dict): The lut to be used in encoding.
        byte_order (bytes): The byte order character for ``struct.unpack``.
        special_values (dict): If given, predefined special values are going to
            be replaced with corresponding special characters.

    Returns:
        bytes: The encoded bytes.
    """
    # pad data
    padding = (4 - len(data) % 4) % 4
    data = b"".join([data, b"\0" * padding])
    parts = []
    parts_append = parts.append
    number_of_chunks = len(data) // 4
    byte_format = b"%s%sI" % (byte_order, str(number_of_chunks).encode())
    unpack = struct.unpack
    for x in unpack(byte_format, data):
        # network order (big endian), 32-bit unsigned integer
        # note: x86 is little endian
        parts_append(lut[(x // 52200625)])
        parts_append(lut[(x // 614125) % 85])
        parts_append(lut[(x // 7225) % 85])
        parts_append(lut[(x // 85) % 85])
        parts_append(lut[x % 85])
    return_val = b"".join(parts)
    if special_values:
        for key in special_values.keys():
            return_val = return_val.replace(key, special_values[key])
            # return_val = special_values[key].join(return_val.split(key))
    return return_val


def __encode_multithreaded(f, data):
    """Run the given function with the given data in multi-threaded fashion.

    Args:
        f: The function
        data: The data.

    Returns:
        Any: The function result.
    """
    import multiprocessing
    import platform

    number_of_threads = int(multiprocessing.cpu_count() / 2)

    if platform.system() == "Windows":
        multiprocessing.set_executable("C:/Python27/pythonw.exe")
    elif platform.system() == "Linux":
        multiprocessing.set_executable("/usr/bin/python")

    p = multiprocessing.Pool(number_of_threads)

    number_of_chunks = len(data) // 4
    chunk_per_thread = int(number_of_chunks / number_of_threads)
    split_per_char = chunk_per_thread * 4

    thread_data = []
    for i in range(0, len(data), split_per_char):
        thread_data.append(data[i : i + split_per_char])

    data = b"".join(p.map(f, thread_data))
    p.close()
    return data


def rfc1924_b85_encode(data):
    """Encode the given string data in to Base85 using the RFC1924 LUT.

    Args:
        data (bytes): A string which contains a string to be encoded in Base85

    Returns:
        bytes: The encoded data.
    """
    lut = LUTS["rfc1924"]["int_to_char"]
    byte_order = LUTS["rfc1924"]["byte_order"]
    return __b85_encode(data, lut, byte_order)


def rfc1924_b85_encode_multithreaded(data):
    """Encode the given string data in to Base85 using the RFC1924 LUT.

    Args:
        data (bytes): A string which contains a string to be encoded in Base85.

    Returns:
        bytes: The encoded data.
    """
    return __encode_multithreaded(rfc1924_b85_encode, data)


def arnold_b85_encode(data):
    """Encode the given bytes data in to Base85 using the arnold LUT.

    Args:
        data (bytes): Bytes to be encoded in Base85.

    Returns:
        bytes: The encoded data.
    """
    lut = LUTS["arnold"]["int_to_char"]
    byte_order = LUTS["arnold"]["byte_order"]
    special_values = LUTS["arnold"]["special_values"]
    return __b85_encode(data, lut, byte_order, special_values=special_values)


def arnold_b85_encode_multithreaded(data):
    """Encode the given string data in to Base85 using arnold LUT.

    Args:
        data (bytes): String to be encoded in Base85.

    Returns:
        bytes: Encoded data.
    """
    return __encode_multithreaded(arnold_b85_encode, data)


def __b85_decode(data, lut, byte_order, special_values=None):
    """Decode the given string data by using the given LUT and byte order.

    Args:
        data (bytes): A string which contains the encoded data.
        lut (dict): A dict where the keys are encoded characters and the
            values are the integer correspondence of those characters and will
            be used to generate an integer number.
        byte_order (bytes): The byte order character for struct.pack.
        # unpack_z (bool): replaces character "z" with appropriate characters.
        #     for the "0 special case" (where it is not converted to a 5
        #     character string but "z").
    """
    if special_values:
        for key in special_values.keys():
            # if the data is massive, then we are using twice the memory
            # use key.join(data.split(special_values[key]))
            data = data.replace(special_values[key], key)
            # data = key.join(data.split(special_values[key]))

    parts = []
    parts_append = parts.append
    pack = struct.pack
    byte_format = b"%sI" % byte_order
    for i in range(0, len(data), 5):
        int_sum = (
            52200625 * lut[data[i : i + 1]]
            + 614125 * lut[data[i + 1 : i + 2]]
            + 7225 * lut[data[i + 2 : i + 3]]
            + 85 * lut[data[i + 3 : i + 4]]
            + lut[data[i + 4 : i + 5]]
        )
        parts_append(pack(byte_format, int_sum))
    return b"".join(parts)


def b85_decode(data):
    """Decode data by using the standard LUT and byte order (=big endian).

    Args:
        data (bytes): A string which contains the encoded data.
    """
    lut = LUTS["standard"]["char_to_int"]
    byte_order = LUTS["standard"]["byte_order"]
    return __b85_decode(data, lut, byte_order)


def rfc1924_b85_decode(data):
    """Decode data by using the RFC1924 LUT and byte order (=big endian).

    Args:
        data (bytes): A string which contains the encoded data.
    """
    lut = LUTS["rfc1924"]["char_to_int"]
    byte_order = LUTS["rfc1924"]["byte_order"]
    return __b85_decode(data, lut, byte_order)


def arnold_b85_decode(data):
    """Decode the given data by using the Arnold LUT and byte order(=big endian).

    Args:
        data (bytes): A string which contains the encoded data

    Returns:
        bytes: Decoded data.
    """
    lut = LUTS["arnold"]["char_to_int"]
    byte_order = LUTS["arnold"]["byte_order"]
    special_values = LUTS["arnold"]["special_values"]
    return __b85_decode(data, lut, byte_order, special_values)
    # return __b85_decode(data, lut, byte_order)


def mapper(encoded_data, raw_data, special_values=None):
    """Create a lut for known Base85 encoding.

    Args:
        encoded_data (str): The path of the encoded file.
        raw_data (list): A list of raw data, showing the unencoded data.
        special_values (dict): A dictionary containing special values.
    """
    data = encoded_data
    if special_values:
        # special case replace 'z's with '!!!!!'
        data = encoded_data
        for key in special_values.keys():
            data = data.replace(special_values[key], key)

    # half encode to base85, without using a lut
    half_encoded = []
    unpack = struct.unpack
    pack = struct.pack
    for i in range(0, len(raw_data)):
        # get the unencoded base85 of the
        # integer corresponding of the float number
        unencoded_base85 = unpack("I", pack("f", raw_data[i]))[0]
        half_encoded.append(unencoded_base85 // 52200625)
        half_encoded.append((unencoded_base85 // 614125) % 85)
        half_encoded.append((unencoded_base85 // 7225) % 85)
        half_encoded.append((unencoded_base85 // 85) % 85)
        half_encoded.append(unencoded_base85 % 85)

    lut = {}
    for i in range(len(half_encoded)):
        lut[data[i]] = half_encoded[i]

    return lut


def auto_mapper(encoded_data_path, raw_data):
    """Create a lut for known Base85 encoding.

    Args:
        encoded_data_path (string): The path of the encoded file.
        raw_data (list): A list of raw numbers, showing the unencoded data.
    """
    data = open(encoded_data_path, "r").read().strip()
    return mapper(data, raw_data)
