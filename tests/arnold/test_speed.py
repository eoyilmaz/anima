# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Tests the speed of the base85 encode operation
"""
import time
import multiprocessing
import re

from anima.render.arnold import base85
from struct import pack, unpack

repeat = 1
num_of_data = 50000000

print('Repetition              : %s' % repeat)
print('Number of Data          : %s' % num_of_data)

start = time.time()
data = ''.join([pack('<I', i) for i in range(num_of_data)])
end = time.time()
generating_data = end - start
print('Generating data         : %.3f seconds' % generating_data)

start = time.time()
unpacked_data = unpack('<%sI' % (len(data) // 4), data)
end = time.time()
unpacking_data = end - start
print('length of unpacked data : %s' % len(unpacked_data))
print('Unpacking data          : %.3f seconds' % unpacking_data)

print('******** NORMAL ********')
start = time.time()
normal_encoded_data = base85.arnold_b85_encode(data)
end = time.time()
encode_duration = end - start
print('Encoding %3i times took : %.3f seconds' % (repeat, encode_duration))
print('Averaging               : %.3f seconds' % (encode_duration / repeat))


print('********  FAST  ********')
start = time.time()

number_of_threads = 8
p = multiprocessing.Pool(number_of_threads)
number_of_chunks = len(data) // 4
chunk_per_thread = number_of_chunks / number_of_threads
split_per_char = chunk_per_thread * 4
thread_data = []
for i in range(0, len(data), split_per_char):
    thread_data.append(data[i:i + split_per_char])


thread_encoded_data = ''.join(p.map(base85.arnold_b85_encode, thread_data))

end = time.time()
encode_duration = end - start
print('Encoding %3i times took : %.3f seconds' % (repeat, encode_duration))
print('Averaging               : %.3f seconds' % (encode_duration / repeat))

assert normal_encoded_data == thread_encoded_data

print('****************************************')
print('Test Splitting vs Appending')
print('Splitting with RegEx')
start = time.time()
regex_splitted_data = re.sub("(.{500})", "\\1\n", normal_encoded_data, 0)
end = time.time()
print('Using RegEx             : %.3f seconds' % (end - start))

print('Splitting with List Appends')
start = time.time()
list_splitted_data = []
for i in range(0, len(normal_encoded_data), 500):
    list_splitted_data.append(normal_encoded_data[i:i + 500])
list_splitted_data = '\n'.join(list_splitted_data)
end = time.time()
print('Using List Append       : %.3f seconds' % (end - start))

print(len(regex_splitted_data))
print(len(list_splitted_data))
assert regex_splitted_data == list_splitted_data

