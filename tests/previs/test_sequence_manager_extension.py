# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import unittest
import os
import pymel.core
from anima.previs import (SequenceManagerExtension, SequencerExtension,
                          ShotExtension, Sequence, Media, Video, Track, Clip,
                          File)


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

    def test_to_edl_is_working_properly(self):
        """testing if to_edl method is working properly
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

    def test_generate_sequence_structure_returns_a_sequence_instance(self):
        """testing if generate_sequence_structure() method will return a
        Sequence instance
        """
        sm = pymel.core.PyNode('sequenceManager1')
        seq1 = sm.create_sequence('sequence1')

        shot1 = seq1.create_shot('shot1')
        shot1.output.set('/tmp/shot1.mov')

        shot2 = seq1.create_shot('shot2')
        shot2.output.set('/tmp/shot2.mov')

        result = sm.generate_sequence_structure()
        self.assertIsInstance(
            result,
            Sequence
        )

    def test_set_shot_name_template_is_working_properly(self):
        """testing if set_shot_name_template() is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        self.assertFalse(sm.hasAttr('shot_name_template'))
        test_template = '<Sequence>_<Shot>_<Version>'
        sm.set_shot_name_template(test_template)
        self.assertTrue(sm.hasAttr('shot_name_template'))
        self.assertEqual(sm.shot_name_template.get(), test_template)

    def test_get_shot_name_template_is_working_properly(self):
        """testing if set_shot_name_template() is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        self.assertFalse(sm.hasAttr('shot_name_template'))
        test_template = '<Sequence>_<Shot>_<Version>'
        sm.set_shot_name_template(test_template)
        self.assertTrue(sm.hasAttr('shot_name_template'))
        self.assertEqual(sm.get_shot_name_template(), test_template)

    def test_get_shot_name_template_will_create_shot_name_template_attribute_if_missing(self):
        """testing if set_shot_name_template() will create the
        shot_name_template attribute if missing
        """
        sm = pymel.core.PyNode('sequenceManager1')
        self.assertFalse(sm.hasAttr('shot_name_template'))
        result = sm.get_shot_name_template()
        self.assertTrue(sm.hasAttr('shot_name_template'))
        self.assertEqual(result, '<Sequence>_<Shot>_<Version>')

    def test_set_version_is_working_properly(self):
        """testing if set_version() is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        self.assertFalse(sm.hasAttr('version'))
        test_version = 'v001'
        sm.set_version(test_version)
        self.assertTrue(sm.hasAttr('version'))
        self.assertEqual(sm.version.get(), test_version)

    def test_get_version_is_working_properly(self):
        """testing if set_version() is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        self.assertFalse(sm.hasAttr('version'))
        test_version = 'v001'
        sm.set_version(test_version)
        self.assertTrue(sm.hasAttr('version'))
        self.assertEqual(sm.get_version(), test_version)

    def test_get_version_will_create_attribute_if_missing(self):
        """testing if get_version() will create the missing version attribute
        """
        sm = pymel.core.PyNode('sequenceManager1')
        self.assertFalse(sm.hasAttr('version'))
        result = sm.get_version()
        self.assertTrue(sm.hasAttr('version'))
        self.assertEqual(result, '')

    def test_generate_sequence_structure_is_working_properly(self):
        """testing if generate_sequence_structure() method is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        sm.set_shot_name_template('<Sequence>_<Shot>_<Version>')
        sm.set_version('v001')
        seq1 = sm.create_sequence('SEQ001_HSNI_003')

        shot1 = seq1.create_shot('0010')
        shot1.startFrame.set(0)
        shot1.endFrame.set(24)
        shot1.sequenceStartFrame.set(0)
        shot1.track.set(0)
        shot1.output.set('/tmp/SEQ001_HSNI_003_0010_v001.mov')
        shot1.handle.set(10)

        shot2 = seq1.create_shot('0020')
        shot2.startFrame.set(10)
        shot2.endFrame.set(35)
        shot2.sequenceStartFrame.set(25)
        shot2.track.set(0)
        shot2.output.set('/tmp/SEQ001_HSNI_003_0020_v001.mov')
        shot2.handle.set(15)

        shot3 = seq1.create_shot('0030')
        shot3.startFrame.set(25)
        shot3.endFrame.set(50)
        shot3.sequenceStartFrame.set(45)
        shot3.track.set(1)
        shot3.output.set('/tmp/SEQ001_HSNI_003_0030_v001.mov')
        shot3.handle.set(20)

        seq = sm.generate_sequence_structure()
        self.assertIsInstance(seq, Sequence)

        self.assertEqual('24', seq.timebase)
        self.assertEqual('00:00:00:00', seq.timecode)
        self.assertEqual(False, seq.ntsc)

        media = seq.media
        self.assertIsInstance(media, Media)

        video = media.video
        self.assertIsInstance(video, Video)
        self.assertIsNone(media.audio)

        self.assertEqual(len(video.tracks), 2)

        track1 = video.tracks[0]
        self.assertIsInstance(track1, Track)
        self.assertEqual(len(track1.clips), 2)
        self.assertEqual(track1.enabled, True)

        track2 = video.tracks[1]
        self.assertIsInstance(track2, Track)
        self.assertEqual(len(track2.clips), 1)
        self.assertEqual(track2.enabled, True)

        clip1 = track1.clips[0]
        self.assertIsInstance(clip1, Clip)
        self.assertEqual(clip1.type, 'Video')
        self.assertEqual(clip1.id, 'SEQ001_HSNI_003_0010_v001')
        self.assertEqual(clip1.name, '0010')
        self.assertEqual(clip1.in_, 0)   # startFrame
        self.assertEqual(clip1.out, 24)  # endFrame
        self.assertEqual(clip1.start, 0)  # sequenceStartFrame
        self.assertEqual(clip1.end, 24)  # sequenceEndFrame

        clip2 = track1.clips[1]
        self.assertIsInstance(clip2, Clip)
        self.assertEqual(clip2.type, 'Video')
        self.assertEqual(clip2.id, 'SEQ001_HSNI_003_0020_v001')
        self.assertEqual(clip2.name, '0020')
        self.assertEqual(clip2.in_, 10)   # startFrame
        self.assertEqual(clip2.out, 35)  # endFrame
        self.assertEqual(clip2.start, 25)  # sequenceStartFrame
        self.assertEqual(clip2.end, 50)  # sequenceEndFrame

        clip3 = track2.clips[0]
        self.assertIsInstance(clip3, Clip)
        self.assertEqual(clip3.type, 'Video')
        self.assertEqual(clip3.id, 'SEQ001_HSNI_003_0030_v001')
        self.assertEqual(clip3.name, '0030')
        self.assertEqual(clip3.in_, 25)   # startFrame
        self.assertEqual(clip3.out, 50)  # endFrame
        self.assertEqual(clip3.start, 45)  # sequenceStartFrame
        self.assertEqual(clip3.end, 70)  # sequenceEndFrame

        file1 = clip1.file
        self.assertIsInstance(file1, File)
        self.assertEqual(file1.name, 'SEQ001_HSNI_003_0010_v001.mov')
        self.assertEqual(file1.pathurl, '/tmp/SEQ001_HSNI_003_0010_v001.mov')
        self.assertEqual(file1.duration, 45)  # including handles

        file2 = clip2.file
        self.assertIsInstance(file2, File)
        self.assertEqual(file2.name, 'SEQ001_HSNI_003_0020_v001.mov')
        self.assertEqual(file2.pathurl, '/tmp/SEQ001_HSNI_003_0020_v001.mov')
        self.assertEqual(file2.duration, 56)  # including handles

        file3 = clip3.file
        self.assertIsInstance(file3, File)
        self.assertEqual(file3.name, 'SEQ001_HSNI_003_0030_v001.mov')
        self.assertEqual(file3.pathurl, '/tmp/SEQ001_HSNI_003_0030_v001.mov')
        self.assertEqual(file3.duration, 66)  # including handles
