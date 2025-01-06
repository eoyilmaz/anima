# -*- coding: utf-8 -*-

import struct


standard_set = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstu"
rfc1924_set = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~"
arnold_set = "$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwx"

LUTS = {
    "standard": {
        "byte_order": b"!",
        "char_to_int": dict(
            map(lambda x: (bytes(x, "utf-8"), standard_set.index(x)), standard_set)
        ),
        "int_to_char": list(map(lambda x: bytes(x, "utf-8"), standard_set)),
    },
    "rfc1924": {
        "byte_order": b"!",
        "char_to_int": dict(
            map(lambda x: (bytes(x, "utf-8"), rfc1924_set.index(x)), rfc1924_set)
        ),
        "int_to_char": list(map(lambda x: bytes(x, "utf-8"), rfc1924_set)),
    },
    "arnold": {
        "byte_order": b"<",
        "expansion_char": b"!",
        "special_values": {b"$$$$$": b"z", b"8Fcb9": b"y"},  # 0.0  # 1.0
        "char_to_int": dict(
            map(lambda x: (bytes(x, "utf-8"), arnold_set.index(x)), arnold_set)
        ),
        "int_to_char": list(map(lambda x: bytes(x, "utf-8"), arnold_set)),
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
    elif platform.system() in ["Linux", "Darwin"]:
        multiprocessing.set_executable("/usr/bin/python3")

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
