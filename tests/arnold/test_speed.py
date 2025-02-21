# -*- coding: utf-8 -*-
"""Tests the speed of the base85 encode operation."""

import time
import re
from struct import pack, unpack

from anima.render.arnold import base85


if __name__ == "__main__":
    repeat = 1
    num_of_data = 50000000

    print(f"Repetition              : {repeat}")
    print(f"Number of Data          : {num_of_data}")

    start = time.time()
    data = b"".join([pack(b"<I", i) for i in range(num_of_data)])
    end = time.time()
    generating_data = end - start
    print(f"Generating data         : {generating_data:.3f} seconds")

    start = time.time()
    unpacked_data = unpack(b"<%sI" % (len(data) // 4), data)
    end = time.time()
    unpacking_data = end - start
    print(f"length of unpacked data : {len(unpacked_data)}")
    print(f"Unpacking data          : {unpacking_data:.3f} seconds")

    print("******** NORMAL ********")
    start = time.time()
    normal_encoded_data = base85.arnold_b85_encode(data)
    end = time.time()
    encode_duration = end - start
    print(f"Encoding {repeat:3d} times took : {encode_duration:.3f} seconds")
    print(f"Averaging               : {encode_duration / repeat:.3f} seconds")

    print("**** MULTI-THREADED ****")
    start = time.time()
    thread_encoded_data = base85.arnold_b85_encode_multithreaded(data)
    end = time.time()
    encode_duration = end - start
    print(f"Encoding {repeat:3d} times took : {encode_duration:.3f} seconds")
    print(f"Averaging               : {encode_duration / repeat:.3f} seconds")

    assert normal_encoded_data == thread_encoded_data

    print("************************")
    print("Test Regex vs List Append")
    print("Splitting with RegEx")
    start = time.time()
    regex_splitted_data = re.sub(b"(.{500})", b"\\1\n", normal_encoded_data, 0)
    end = time.time()
    print(f"Using RegEx             : {end - start:.3f} seconds")

    print("Splitting with List Appends")
    start = time.time()
    list_splitted_data = []
    for i in range(0, len(normal_encoded_data), 500):
        list_splitted_data.append(normal_encoded_data[i : i + 500])
    list_splitted_data = b"\n".join(list_splitted_data)
    end = time.time()
    print(f"Using List Append       : {end - start:.3f} seconds")
