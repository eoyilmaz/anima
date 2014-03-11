# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import unittest
import os
import pymel
from anima.previs import SequenceManagerExtension, Sequence, Media, Video, \
    Track, Clip, File


class SequenceManagerTestCase(unittest.TestCase):
    """tests the SequenceManagerExtension class
    """

    def setUp(self):
        """set up the test
        """
        # create a new scene and get the sequenceManager in the scene
        pymel.core.newFile(force=True)
        self.sm = pymel.core.PyNode('sequenceManager1')

    def test_from_xml_path_argument_skipped(self):
        """testing if a TypeError will be raised when the path argument is
        skipped
        """
        sm = pymel.core.PyNode('sequenceManager1')
        with self.assertRaises(TypeError) as cm:
            sm.from_xml()

        self.assertEqual(
            cm.exception.message,
            'from_xml() takes exactly 2 arguments (1 given)'
        )

    def test_from_xml_path_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the path argument is not
        a string
        """
        sm = pymel.core.PyNode('sequenceManager1')
        with self.assertRaises(TypeError) as cm:
            sm.from_xml(30)

        self.assertEqual(
            cm.exception.message,
            'path argument in SequenceManager.from_xml should be a string, '
            'not int'
        )

    def test_from_xml_path_argument_is_not_a_valid_path(self):
        """testing if a IOError will be raised when the path argument is not
        a valid path
        """
        sm = pymel.core.PyNode('sequenceManager1')
        with self.assertRaises(IOError) as cm:
            sm.from_xml('not a valid path')

        self.assertEqual(
            cm.exception.message,
            'Please supply a valid path to an XML file!'
        )

    def test_from_xml_returns_a_Sequence_instance(self):
        """testing if from_xml method will return a Sequence instance
        """
        sm = pymel.core.PyNode('sequenceManager1')
        sequence = sm.from_xml('./test_data/test_v003.xml')
        self.assertIsInstance(sequence, Sequence)

    def test_from_xml_returns_a_Seqeunce_with_correct_hierarchy(self):
        """testing if from_xml method will return a Sequence instance with
        correct hierarchy
        """
        path = os.path.abspath('./test_data/test_v003.xml')

        sm = pymel.core.PyNode('sequenceManager1')
        sequence = sm.from_xml(path)
        self.assertIsInstance(sequence, Sequence)

        self.assertEqual(sequence.duration, 109)
        self.assertEqual(sequence.name, 'previs_edit_v001')
        self.assertEqual(sequence.timebase, '24')
        self.assertEqual(sequence.ntsc, False)
        self.assertEqual(sequence.timecode, '00:00:00:00')

        media = sequence.media
        self.assertIsInstance(media, Media)
        self.assertEqual(1, len(media.video))
        self.assertEqual(0, len(media.audio))

        video = media.video[0]

        self.assertIsInstance(video, Video)

        self.assertEqual(video.width, 1024)
        self.assertEqual(video.height, 778)

        self.assertEqual(1, len(video.tracks))

        track = video.tracks[0]

        self.assertIsInstance(track, Track)

        self.assertEqual(3, len(track.clips))
        self.assertEqual(False, track.locked)
        self.assertEqual(True, track.enabled)

        clip1 = track.clips[0]
        clip2 = track.clips[1]
        clip3 = track.clips[2]

        self.assertIsInstance(clip1, Clip)
        self.assertIsInstance(clip2, Clip)
        self.assertIsInstance(clip3, Clip)

        # Clip1
        self.assertEqual(clip1.id, 'shot2')
        self.assertEqual(clip1.name, 'shot2')
        self.assertEqual(clip1.enabled, True)
        self.assertEqual(clip1.start, 1.0)
        self.assertEqual(clip1.end, 35.0)
        self.assertEqual(clip1.duration, 34.0)
        self.assertEqual(clip1.in_, 0.0)
        self.assertEqual(clip1.out, 34.0)

        file1 = clip1.file
        self.assertIsInstance(file1, File)
        self.assertEqual(file1.duration, 34.0)
        self.assertEqual(file1.name, 'shot2')
        self.assertEqual(
            file1.pathurl,
            'file:///home/eoyilmaz/maya/projects/default/data/shot2.mov'
        )

        # Clip2
        self.assertEqual(clip2.id, 'shot')
        self.assertEqual(clip2.name, 'shot')
        self.assertEqual(clip2.enabled, True)
        self.assertEqual(clip2.start, 35.0)
        self.assertEqual(clip2.end, 65.0)
        self.assertEqual(clip2.duration, 30.0)
        self.assertEqual(clip2.in_, 0.0)
        self.assertEqual(clip2.out, 30.0)

        file2 = clip2.file
        self.assertIsInstance(file2, File)
        self.assertEqual(file2.duration, 30.0)
        self.assertEqual(file2.name, 'shot')
        self.assertEqual(
            file2.pathurl,
            'file:///home/eoyilmaz/maya/projects/default/data/shot.mov'
        )

        # Clip3
        self.assertEqual(clip3.id, 'shot1')
        self.assertEqual(clip3.name, 'shot1')
        self.assertEqual(clip3.enabled, True)
        self.assertEqual(clip3.start, 65.0)
        self.assertEqual(clip3.end, 110.0)
        self.assertEqual(clip3.duration, 45.0)
        self.assertEqual(clip3.in_, 0.0)
        self.assertEqual(clip3.out, 45.0)

        file3 = clip3.file
        self.assertIsInstance(file3, File)
        self.assertEqual(file3.duration, 45.0)
        self.assertEqual(file3.name, 'shot1')
        self.assertEqual(
            file3.pathurl,
            'file:///home/eoyilmaz/maya/projects/default/data/shot1.mov'
        )

    def test_to_xml_seq_argument_skipped(self):
        """testing if a TypeError will be raised when the seq argument is
        skipped
        """
        sm = pymel.core.PyNode('sequenceManager1')
        with self.assertRaises(TypeError) as cm:
            sm.to_xml()

        self.assertEqual(
            cm.exception.message,
            'Please supply at least one of "path" or "seq" arguments'
        )

    def test_to_xml_seq_argument_is_not_a_sequence_instance(self):
        """Testing if a TypeError will be raised when the seq argument in
        to_xml method is not a Sequence instance
        """
        sm = pymel.core.PyNode('sequenceManager1')
        with self.assertRaises(TypeError) as cm:
            sm.to_xml(seq=12)

        self.assertEqual(
            cm.exception.message,
            '"seq" argument in SequenceManager.to_xml should be an instance of'
            'anima.previs.Sequence, not int'
        )

    def test_to_xml_returns_a_proper_xml_content_from_given_sequence_instance(self):
        """testing if a proper string will be returned from SequencerExtension.to_xml
        when a Sequence is given with seq argument
        """
        path = os.path.abspath('./test_data/test_v003.xml')

        sm = pymel.core.PyNode('sequenceManager1')
        sequence = sm.from_xml(path)

        self.assertIsInstance(sequence, Sequence)

        result = sm.to_xml(seq=sequence)
        with open(path) as f:
            expected = f.read()

        self.assertEqual(expected, result)

    def test_create_sequence_is_working_properly(self):
        """testing if create_sequence is working properly
        """
        seq = self.sm.create_sequence()
        self.assertEqual(seq.type(), 'sequencer')

        self.assertEqual(self.sm, seq.message.connections()[0])

    def test_create_sequence_is_properly_setting_the_sequence_name(self):
        """testing if create_sequence is working properly
        """
        seq = self.sm.create_sequence('Test Sequence')
        self.assertEqual(
            'Test Sequence',
            seq.sequence_name.get()
        )

    def test_to_xml_is_working_properly(self):
        """testing if to_xml method is working properly
        """
        import edl
        # create a sequence
        seq1 = self.sm.create_sequence()
        seq1.create_shot('shot1')
        seq1.create_shot('shot2')
        seq1.create_shot('shot3')

        l = self.sm.to_edl()
        self.assertIsInstance(
            l,
            edl.List
        )
