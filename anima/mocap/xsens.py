# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from collections import namedtuple

# Data containers
Header = namedtuple(
    'Header',
    ['sample_counter', 'datagram_counter', 'num_items', 'timecode',
     'charID', 'extra_data']
)
Euler = namedtuple(
    'Euler',
    ['segment_ID', 'tx', 'ty', 'tz', 'rx', 'ry', 'rz']
)

Quaternion = namedtuple(
    'Quaternion',
    ['segment_ID', 'tx', 'ty', 'tz', 'q1', 'q2', 'q3', 'q4']
)

TimeCode = namedtuple('TimeCode', 'tc')

# Formats

header_data_format = '!IBBIc7s'
euler_data_format = '!i6f'
quaternion_data_format = '!i7f'


class XSensListener(object):
    """Network listener and parser for XSens data
    """

    def listen(self, host='localhost', port=9763, timeout=2):
        """listens and prints XSens stream
        """
        import struct
        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(timeout)
        s.bind((host, port))

        while True:
            data = s.recv(2048)
            packages = data.split('MXTP')
            for package in packages:
                packet_type_id = package[:2]

                raw_data = package[2:]

                header = raw_data[:18]  # excluding the MXTP01 ID String

                if len(header) < 18:
                    continue

                header_data = Header._make(
                    struct.unpack(header_data_format, header)
                )

                # parse the rest of the data by package type
                raw_pose_data = raw_data[18:]
                pose_data = []
                if packet_type_id == '01':
                    # euler data
                    chunks = map(''.join, zip(*[iter(raw_pose_data)] * 28))
                    for chunk in chunks:
                        unpacked_data = struct.unpack(euler_data_format, chunk)
                        euler_data = Euler._make(unpacked_data)
                        pose_data.append(euler_data)

                elif packet_type_id == '02':
                    # quaternion data
                    # euler data
                    chunks = map(''.join, zip(*[iter(raw_pose_data)] * 32))
                    for chunk in chunks:
                        unpacked_data = struct.unpack(quaternion_data_format, chunk)
                        quaternion_data = Quaternion._make(unpacked_data)
                        pose_data.append(quaternion_data)

                elif packet_type_id == '25':
                    # TimeCode
                    pose_data.append(TimeCode._make(raw_pose_data))

                yield ([header_data, pose_data])

                # elif packet_type_id == '03':
                #     print('Pose data - MVN Optical marker set 1')
                #     print(raw_pose_data)
                #
                # elif packet_type_id == '04':
                #     print('Pose data - Motion Grid Tag data (Deprecated)')
                #     print(raw_pose_data)
                #
                # elif packet_type_id == '05':
                #     print('Pose data - Unity3D')
                #     print(raw_pose_data)
                #
                # elif packet_type_id == '10':
                #     print('Pose data - Scale Information (Deprecated)')
                #     print(raw_pose_data)
                #
                # elif packet_type_id == '1!':
                #     print('Pose data - Prop Information (Deprecated)')
                #     print(raw_pose_data)
                #
                # elif packet_type_id == '12':
                #     print('Character Information -> meta data')
                #     print(raw_pose_data)
                #
                # elif packet_type_id == '13':
                #     print('Character Information -> Scaling Information')
                #     print(raw_pose_data)
                #
                # elif packet_type_id == '20':
                #     print('Joint Angle data')
                #     print(raw_pose_data)
                #
                # elif packet_type_id == '21':
                #     print('Linear Segment Kinematics')
                #     print(raw_pose_data)
                #
                # elif packet_type_id == '22':
                #     print('Angular Segment Kinematics')
                #     print(raw_pose_data)
                #
                # elif packet_type_id == '23':
                #     print('Motion Tracker Kinematics')
                #     print(raw_pose_data)
                #
                # elif packet_type_id == '24':
                #     print('Center Of Mass')
                #     print(raw_pose_data)


class XSensStore(object):
    """Stores XSens data in a file
    """

    def __init__(self, output_file_fullpath=''):
        self.output_file_fullpath = output_file_fullpath

    def store(self, stream):
        """Stores the data until the stream ends

        :param stream:
        :return:
        """
        with open(self.output_file_fullpath, 'wb'):
            while stream:
                pass


class XSensGenerator(object):
    """Generates XSens compatible data

    :param source: A generator, if None, a random sequence will be generated.
    """

    def __init__(self, source=None, fps=240, generate_euler=True,
                 generate_quaternion=True):
        self.source = source
        self.fps = fps
        self.generate_euler = generate_euler
        self.generate_quaternion = generate_quaternion

    def generate(self):
        """generate data
        """
        import time
        for data in self.source:
            time.sleep(1.0/self.fps)
            yield data

    def _random_sequence_generator(self):
        """generates random data
        """
        pass