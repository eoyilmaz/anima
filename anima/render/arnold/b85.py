#!/usr/bin/env python

#
# This is the MIT License
# http://www.opensource.org/licenses/mit-license.php
#
# Copyright (c) 2008 Nick Galbreath
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

#import psyco
#psyco.full()

#gsCharToInt = {'!': 62, '#': 63, '%': 65, '$': 64, '&': 66, ')': 68, '(': 67,
#               '+': 70, '*': 69, '-': 71, '1': 1, '0': 0, '3': 3, '2': 2,
#               '5': 5, '4': 4, '7': 7, '6': 6, '9': 9, '8': 8, ';': 72,
#               '=': 74, '<': 73, '?': 76, '>': 75, 'A': 10, '@': 77, 'C': 12,
#               'B': 11, 'E': 14, 'D': 13, 'G': 16, 'F': 15, 'I': 18, 'H': 17,
#               'K': 20, 'J': 19, 'M': 22, 'L': 21, 'O': 24, 'N': 23, 'Q': 26,
#               'P': 25, 'S': 28, 'R': 27, 'U': 30, 'T': 29, 'W': 32, 'V': 31,
#               'Y': 34, 'X': 33, 'Z': 35, '_': 79, '^': 78, 'a': 36, '`': 80,
#               'c': 38, 'b': 37, 'e': 40, 'd': 39, 'g': 42, 'f': 41, 'i': 44,
#               'h': 43, 'k': 46, 'j': 45, 'm': 48, 'l': 47, 'o': 50, 'n': 49,
#               'q': 52, 'p': 51, 's': 54, 'r': 53, 'u': 56, 't': 55, 'w': 58,
#               'v': 57, 'y': 60, 'x': 59, '{': 81, 'z': 61, '}': 83, '|': 82,
#               '~': 84}

#gsIntToChar = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C',
#               'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
#               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c',
#               'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
#               'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '!', '#', '$',
#               '%', '&', '(', ')', '*', '+', '-', ';', '<', '=', '>', '?', '@',
#               '^', '_', '`', '{', '|', '}', '~']


# doesn't matter if it is big or little endian
gsCharToInt = {'%': 1, '$': 0, "'": 3, '&': 2, ')': 5, '(': 4, '+': 7, '*': 6,
               '-': 9, ',': 8, '/': 11, '.': 10, '1': 13, '0': 12, '3': 15,
               '2': 14, '5': 17, '4': 16, '7': 19, '6': 18, '9': 21, '8': 20,
               ';': 23, ':': 22, '=': 25, '<': 24, '?': 27, '>': 26, 'A': 29,
               '@': 28, 'C': 31, 'B': 30, 'E': 33, 'D': 32, 'G': 35, 'F': 34,
               'I': 37, 'H': 36, 'K': 39, 'J': 38, 'M': 41, 'L': 40, 'O': 43,
               'N': 42, 'Q': 45, 'P': 44, 'S': 47, 'R': 46, 'U': 49, 'T': 48,
               'W': 51, 'V': 50, 'Y': 53, 'X': 52, '[': 55, 'Z': 54, ']': 57,
               '\\': 56, '_': 59, '^': 58, 'a': 61, '`': 60, 'c': 63, 'b': 62,
               'e': 65, 'd': 64, 'g': 67, 'f': 66, 'i': 69, 'h': 68, 'k': 71,
               'j': 70, 'm': 73, 'l': 72, 'o': 75, 'n': 74, 'q': 77, 'p': 76,
               's': 79, 'r': 78, 'u': 81, 't': 80, 'w': 83, 'v': 82, 'x': 84}

gsIntToChar = ['$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0',
               '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=',
               '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
               'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
               'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c',
               'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
               'q', 'r', 's', 't', 'u', 'v', 'w', 'x']

from struct import unpack, pack
# covert 4 characters into 5
def b85_encode(s):
    parts = []
    numchunks = len(s) // 4
    format = '!' + str(numchunks) + 'I'
    for x in unpack(format, s):
        # network order (big endian), 32-bit unsigned integer
        # note: x86 is little endian
        parts.append(gsIntToChar(x // 52200625))
        parts.append(gsIntToChar((x // 614125) % 85))
        parts.append(gsIntToChar((x // 7225) % 85))
        parts.append(gsIntToChar((x // 85) % 85))
        parts.append(gsIntToChar(x % 85))
    return ''.join(parts)

#
# MAY be 10-20% faster, when running on pysco
#   certainly 2x SLOWER when running normally.
#
# also does not use the 'struct' module which may be desirable
# to some
#
def b85_encode2(s):
    parts = []
    parts_append = parts.append
    mChr = chr
    for i in xrange(0, len(s), 4):
        chunk = s[i:i + 4]
        x = ord(chunk[3]) + 256 * (
            ord(chunk[2]) + 256 * (ord(chunk[1]) + 256 * ord(chunk[0])))

        # network order (big endian), 32-bit unsigned integer
        # note: x86 is little endian
        parts.append(mChr(x // 52200625 + 33))
        parts.append(mChr((x // 614125) % 85 + 33))
        parts.append(mChr((x // 7225) % 85 + 33))
        parts.append(mChr((x // 85) % 85 + 33))
        parts.append(mChr(x % 85 + 33))
    return ''.join(parts)

# convert 5 characters to 4
def b85_decode(s):
    parts = []
    parts_append = parts.append
    mChr = chr
    for i in xrange(0, len(s), 5):
        bsum = 0;
        for j in xrange(0, 5):
            val = gsCharToInt[s[i + j]]
            bsum = 85 * bsum + val
        tmp = pack('!I', bsum)
        parts_append(tmp)
        #parts += tmp 
        #parts += unpack('cccc', tmp)
    return ''.join(parts)

# convert 5 characters to 4
def b85_decode2(s):
    parts = []
    for i in xrange(0, len(s), 5):
        bsum = 0;
        for j in xrange(0, 5):
            val = gsCharToInt[ord(s[i + j])]
            bsum = 85 * bsum + val
        parts.append(chr((bsum >> 24) & 0xff))
        parts.append(chr((bsum >> 16) & 0xff))
        parts.append(chr((bsum >> 8) & 0xff))
        parts.append(chr(bsum & 0xff))

    return ''.join(parts)


import unittest


class B85Test(unittest.TestCase):
    def testDecode1(self):
        s = b85_decode('!!!!#')
        self.assertEquals(4, len(s))
        self.assertEquals(0, ord(s[0]))
        self.assertEquals(0, ord(s[1]))
        self.assertEquals(0, ord(s[2]))
        self.assertEquals(1, ord(s[3]))

        e = b85_encode(s)
        self.assertEquals('!!!!#', e)


def mapper(data_in, corresponding_numbers):
    """maps the lut entries
    """
    # special case replace 'z's with '!!!!!'
    data = data_in.replace('z', '!!!!!').strip()

    # half encode to base85, without using a lut
    half_encoded = []
    for i in xrange(0, len(corresponding_numbers)):
        # get the unencoded base85 of the
        # integer corresponding of the float number
        unencoded_base85 = unpack('I', pack('f', corresponding_numbers[i]))[0]
        half_encoded.append(unencoded_base85 // 52200625)
        half_encoded.append((unencoded_base85 // 614125) % 85)
        half_encoded.append((unencoded_base85 // 7225) % 85)
        half_encoded.append((unencoded_base85 // 85) % 85)
        half_encoded.append(unencoded_base85 % 85)

    #print half_encoded
    #print data
    #print len(half_encoded)
    #print len(data)

    lut = {}
    for i in range(len(half_encoded)):
        lut[data[i]] = half_encoded[i]

    return lut


def automapper(numbers):
    data = open('/home/eoyilmaz/tmp/binData3', 'r').read().strip()
    return mapper(data, numbers)


if __name__ == '__main__':
    from time import clock
    #unittest.main()

    s = '!!!!#' * 10

    t0 = clock()
    for i in xrange(1000000):
        b85_decode(s)
    t1 = clock()
    print "decode v1", t1 - t0

    t0 = clock()
    for i in xrange(1000000):
        b85_decode2(s)
    t1 = clock()
    print "decode v2", t1 - t0

    s = b85_decode('!!!!#' * 10)

    t0 = clock()
    for i in xrange(1000000):
        b85_encode(s)
    t1 = clock()
    print "encode v1", t1 - t0

    t0 = clock()
    for i in xrange(1000000):
        b85_encode2(s)
    t1 = clock()
    print "encode v2", t1 - t0


