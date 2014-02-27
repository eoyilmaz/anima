# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os

import unittest
from anima.previs import Sequencer, Sequence, Media, Video, Track, Clip, File


class SequencerTestCase(unittest.TestCase):
    """tests the anima.animation.Sequencer class
    """

    def setUp(self):
        """set up the test
        """
        pass

    def test_from_xml_path_argument_skipped(self):
        """testing if a TypeError will be raised when the path argument is
        skipped
        """
        s = Sequencer()
        with self.assertRaises(TypeError) as cm:
            s.from_xml()

        self.assertEqual(
            cm.exception.message,
            'from_xml() takes exactly 2 arguments (1 given)'
        )

    def test_from_xml_path_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the path argument is not
        a string
        """
        s = Sequencer()
        with self.assertRaises(TypeError) as cm:
            s.from_xml(30)

        self.assertEqual(
            cm.exception.message,
            'path argument in Sequencer.from_xml should be a string, not int'
        )

    def test_from_xml_path_argument_is_not_a_valid_path(self):
        """testing if a IOError will be raised when the path argument is not
        a valid path
        """
        s = Sequencer()
        with self.assertRaises(IOError) as cm:
            s.from_xml('not a valid path')

        self.assertEqual(
            cm.exception.message,
            'Please supply a valid path to an XML file!'
        )

    def test_from_xml_returns_a_Sequence_instance(self):
        """testing if from_xml method will return a Sequence instance
        """
        s = Sequencer()
        sequence = s.from_xml('./test_data/test_v003.xml')
        self.assertIsInstance(sequence, Sequence)

    def test_from_xml_returns_a_Seqeunce_with_correct_hierarchy(self):
        """testing if from_xml method will return a Sequence instance with
        correct hierarchy
        """
        path = os.path.abspath('./test_data/test_v003.xml')

        s = Sequencer()
        sequence = s.from_xml(path)
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
        s = Sequencer()
        with self.assertRaises(TypeError) as cm:
            s.to_xml()

        self.assertEqual(
            cm.exception.message,
            'to_xml() takes at least 2 arguments (1 given)'
        )

    def test_to_xml_seq_argument_is_not_a_sequence_instance(self):
        """Testing if a TypeError will be raised when the seq argument in
        to_xml method is not a Sequence instance
        """
        s = Sequencer()
        with self.assertRaises(TypeError) as cm:
            s.to_xml(12)

        self.assertEqual(
            cm.exception.message,
            '"seq" argument in Sequencer.to_xml should be an instance of'
            'anima.previs.Sequence, not int'
        )

    def test_to_xml_returns_a_proper_xml_content_from_given_sequence_instance(self):
        """testing if a proper string will be returned from Sequencer.to_xml
        when a Sequence is given with seq argument
        """
        path = os.path.abspath('./test_data/test_v003.xml')

        s = Sequencer()
        sequence = s.from_xml(path)

        self.assertIsInstance(sequence, Sequence)

        result = s.to_xml(sequence)
        with open(path) as f:
            expected = f.read()

        self.assertEqual(expected, result)


class SequencerMayaTestCase(unittest.TestCase):
    """Tests Sequencer with Maya
    """

    @classmethod
    def setUpClass(cls):
        """setup test in class level
        """
        # start maya
        import pymel.core
        pymel.core.newFile(force=True)

    def setUp(self):
        """
        """
        import pymel.core
        pymel.core.newFile(force=True)

        # create a couple of shots
        self.shot1 = pymel.core.shot()
        self.shot2 = pymel.core.shot()
        self.shot3 = pymel.core.shot()

    def test__setup(self):
        """testing test setup
        """
        import pymel.core
        shots = pymel.core.ls(type=pymel.core.nt.Shot)
        self.assertEqual(3, len(shots))
        self.assertIsInstance(shots[0], pymel.core.nt.Shot)
        self.assertIsInstance(shots[1], pymel.core.nt.Shot)
        self.assertIsInstance(shots[2], pymel.core.nt.Shot)

    def test_set_shot_handles_shots_argument_is_not_a_list(self):
        """testing if a TypeError will be raised when the shots argument is
        not a list
        """
        self.fail('test is not implemented yet')

    def test_set_shot_handles_shots_argument_is_not_a_list_of_Shot_instances(self):
        """testing if a TypeError will be raised when the shots list is not a
        list of Shot instances
        """
        self.fail('test is not implemented yte')

    def test_set_shot_handles_handle_argument_skipped(self):
        """testing if the default value (10) will be used when the handle
        attribute is skipped
        """
        self.fail('test is not implemented yet')

    def test_set_shot_handles_handle_argument_is_not_an_integer(self):
        """testing if a TypeError will be raised when the handle argument is
        not an integer
        """
        self.fail('test is not implemented yet')

    def test_set_shot_handles_handle_argument_is_working_properly(self):
        """testing if the handle argument value is correctly used in
        set_shot_handles() method
        """
        self.fail('test is not implemented yet')

    def test_set_shot_handles_handle_argument_is_negative(self):
        """testing if a ValueError will be raised when the handle argument
        value is a negative integer
        """
        self.fail('test is not implemented yet')

    def test_set_shot_handles_will_create_handle_attribute(self):
        """testing if set_shot_handles method will create handle integer
        attribute
        """
        self.fail('test is not implemented yet')

    def test_set_shot_handles_will_be_able_to_set_handle_values_when_there_is_already_a_handle_attribute_defined(self):
        """testing if set_shot_handle method will still be able to set the
        handle attribute value even there is a handle attribute defined
        previously
        """
        self.fail('test is not implemented yet')
