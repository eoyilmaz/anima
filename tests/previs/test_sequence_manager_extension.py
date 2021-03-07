# -*- coding: utf-8 -*-

import unittest
import os

# prepare for test
os.environ['ANIMA_TEST_SETUP'] = ""
from anima.env import mayaEnv  # to setup maya extensions

import pymel.core
from anima.edit import Sequence, Media, Video, Track, Clip, File


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

    def test_from_xml_generates_correct_sequencer_hierarchy(self):
        """testing if from_xml method will generate Sequences and shots
        correctly
        """
        path = os.path.abspath('./test_data/test_v001.xml')

        sm = pymel.core.PyNode('sequenceManager1')
        sm.from_xml(path)

        sequences = sm.sequences.get()
        self.assertEqual(len(sequences), 1)

        sequencer = sequences[0]
        self.assertIsInstance(sequencer, pymel.core.nt.Sequencer)

        self.assertEqual(sequencer.duration, 111)
        self.assertEqual(sequencer.sequence_name.get(), 'SEQ001_HSNI_003')

        # check scene fps
        self.assertEqual(pymel.core.currentUnit(q=1, t=1), 'film')

        # check timecode
        time = pymel.core.PyNode('time1')
        self.assertEqual(time.timecodeProductionStart.get(), 0.0)

        shots = sequencer.shots.get()
        self.assertEqual(len(shots), 3)

        shot1 = shots[0]
        shot2 = shots[1]
        shot3 = shots[2]

        self.assertEqual('0010', shot1.shotName.get())
        self.assertEqual(1024, shot1.wResolution.get())
        self.assertEqual(778, shot1.hResolution.get())
        self.assertEqual(1, shot1.track.get())
        self.assertEqual(1.0, shot1.sequenceStartFrame.get())
        self.assertEqual(34.0, shot1.sequenceEndFrame.get())
        self.assertEqual(34.0, shot1.duration)
        self.assertEqual(10.0, shot1.startFrame.get())
        self.assertEqual(43.0, shot1.endFrame.get())
        self.assertEqual(
            '/tmp/SEQ001_HSNI_003_0010_v001.mov',
            shot1.output.get()
        )

        # Clip2
        self.assertEqual('0020', shot2.shotName.get())
        self.assertEqual(1024, shot2.wResolution.get())
        self.assertEqual(778, shot2.hResolution.get())
        self.assertEqual(1, shot2.track.get())
        self.assertEqual(35.0, shot2.sequenceStartFrame.get())
        self.assertEqual(65.0, shot2.sequenceEndFrame.get())
        self.assertEqual(31.0, shot2.duration)
        self.assertEqual(10.0, shot2.startFrame.get())
        self.assertEqual(40.0, shot2.endFrame.get())
        self.assertEqual(
            '/tmp/SEQ001_HSNI_003_0020_v001.mov',
            shot2.output.get()
        )

        # Clip3
        self.assertEqual('0030', shot3.shotName.get())
        self.assertEqual(1024, shot3.wResolution.get())
        self.assertEqual(778, shot3.hResolution.get())
        self.assertEqual(1, shot3.track.get())
        self.assertEqual(66.0, shot3.sequenceStartFrame.get())
        self.assertEqual(111.0, shot3.sequenceEndFrame.get())
        self.assertEqual(46.0, shot3.duration)
        self.assertEqual(10.0, shot3.startFrame.get())
        self.assertEqual(55.0, shot3.endFrame.get())
        self.assertEqual(
            '/tmp/SEQ001_HSNI_003_0030_v001.mov',
            shot3.output.get()
        )

    def test_from_xml_updates_sequencer_hierarchy_with_shots_expanded_and_contracted(self):
        """testing if from_xml method will update Sequences and shots
        correctly with the xml file
        """
        path = os.path.abspath('./test_data/test_v002.xml')

        sm = pymel.core.PyNode('sequenceManager1')
        sm.set_version('v001')
        seq = sm.create_sequence('SEQ001_HSNI_003')

        shot1 = seq.create_shot('0010')
        shot1.startFrame.set(0)
        shot1.endFrame.set(33)
        shot1.sequenceStartFrame.set(1)
        shot1.output.set('/tmp/SEQ001_HSNI_003_0010_v001.mov')
        shot1.handle.set(10)
        shot1.track.set(1)

        shot2 = seq.create_shot('0020')
        shot2.startFrame.set(34)
        shot2.endFrame.set(64)
        shot2.sequenceStartFrame.set(35)
        shot2.output.set('/tmp/SEQ001_HSNI_003_0020_v001.mov')
        shot2.handle.set(10)
        shot2.track.set(1)

        shot3 = seq.create_shot('0030')
        shot3.startFrame.set(65)
        shot3.endFrame.set(110)
        shot3.sequenceStartFrame.set(66)
        shot3.output.set('/tmp/SEQ001_HSNI_003_0030_v001.mov')
        shot3.handle.set(10)
        shot3.track.set(1)

        self.assertEqual(shot1.track.get(), 1)
        self.assertEqual(shot2.track.get(), 1)
        self.assertEqual(shot3.track.get(), 1)

        # now update it with test_v002.xml
        sm.from_xml(path)

        # check shot data
        self.assertEqual('0010', shot1.shotName.get())
        self.assertEqual(1, shot1.track.get())
        self.assertEqual(1.0, shot1.sequenceStartFrame.get())
        self.assertEqual(54.0, shot1.sequenceEndFrame.get())
        self.assertEqual(-10.0, shot1.startFrame.get())
        self.assertEqual(43.0, shot1.endFrame.get())

        # Clip2
        self.assertEqual('0020', shot2.shotName.get())
        self.assertEqual(1, shot2.track.get())
        self.assertEqual(55.0, shot2.sequenceStartFrame.get())
        self.assertEqual(75.0, shot2.sequenceEndFrame.get())
        self.assertEqual(44.0, shot2.startFrame.get())
        self.assertEqual(64.0, shot2.endFrame.get())

        # Clip3
        self.assertEqual('0030', shot3.shotName.get())
        self.assertEqual(1, shot3.track.get())
        self.assertEqual(76.0, shot3.sequenceStartFrame.get())
        self.assertEqual(131.0, shot3.sequenceEndFrame.get())
        self.assertEqual(65.0, shot3.startFrame.get())
        self.assertEqual(120.0, shot3.endFrame.get())

    def test_from_edl_updates_sequencer_hierarchy_with_shots_expanded_and_contracted(self):
        """testing if from_edl method will update Sequences and shots
        correctly with the edl file
        """
        path = os.path.abspath('./test_data/test_v002.edl')

        sm = pymel.core.PyNode('sequenceManager1')
        sm.set_version('v001')
        seq = sm.create_sequence('SEQ001_HSNI_003')

        shot1 = seq.create_shot('0010')
        shot1.startFrame.set(0)
        shot1.endFrame.set(33)
        shot1.sequenceStartFrame.set(1)
        shot1.output.set('/tmp/SEQ001_HSNI_003_0010_v001.mov')
        shot1.handle.set(10)
        shot1.track.set(1)

        shot2 = seq.create_shot('0020')
        shot2.startFrame.set(34)
        shot2.endFrame.set(64)
        shot2.sequenceStartFrame.set(35)
        shot2.output.set('/tmp/SEQ001_HSNI_003_0020_v001.mov')
        shot2.handle.set(10)
        shot2.track.set(1)

        shot3 = seq.create_shot('0030')
        shot3.startFrame.set(65)
        shot3.endFrame.set(110)
        shot3.sequenceStartFrame.set(66)
        shot3.output.set('/tmp/SEQ001_HSNI_003_0030_v001.mov')
        shot3.handle.set(10)
        shot3.track.set(1)

        self.assertEqual(shot1.track.get(), 1)
        self.assertEqual(shot2.track.get(), 1)
        self.assertEqual(shot3.track.get(), 1)

        # now update it with test_v002.xml
        sm.from_edl(path)

        # check shot data
        self.assertEqual('0010', shot1.shotName.get())
        self.assertEqual(1, shot1.track.get())
        self.assertEqual(1.0, shot1.sequenceStartFrame.get())
        self.assertEqual(54.0, shot1.sequenceEndFrame.get())
        self.assertEqual(-10.0, shot1.startFrame.get())
        self.assertEqual(43.0, shot1.endFrame.get())

        # Clip2
        self.assertEqual('0020', shot2.shotName.get())
        self.assertEqual(1, shot2.track.get())
        self.assertEqual(55.0, shot2.sequenceStartFrame.get())
        self.assertEqual(76.0, shot2.sequenceEndFrame.get())
        self.assertEqual(44.0, shot2.startFrame.get())
        self.assertEqual(65.0, shot2.endFrame.get())

        # Clip3
        self.assertEqual('0030', shot3.shotName.get())
        self.assertEqual(1, shot3.track.get())
        self.assertEqual(77.0, shot3.sequenceStartFrame.get())
        self.assertEqual(133.0, shot3.sequenceEndFrame.get())
        self.assertEqual(65.0, shot3.startFrame.get())
        self.assertEqual(121.0, shot3.endFrame.get())

    def test_from_edl_updates_sequencer_hierarchy_with_shots_used_more_than_one_times(self):
        """testing if from_edl method will update Sequences and shots correctly
        with shot are used more than once
        """
        path = os.path.abspath('./test_data/test_v004.edl')

        sm = pymel.core.PyNode('sequenceManager1')
        sm.set_version('v001')
        seq = sm.create_sequence('SEQ001_HSNI_003')

        shot1 = seq.create_shot('0010')
        shot1.startFrame.set(0)
        shot1.endFrame.set(33)
        shot1.sequenceStartFrame.set(1)
        shot1.output.set('/tmp/SEQ001_HSNI_003_0010_v001.mov')
        shot1.handle.set(10)
        shot1.track.set(1)

        shot2 = seq.create_shot('0020')
        shot2.startFrame.set(34)
        shot2.endFrame.set(64)
        shot2.sequenceStartFrame.set(35)
        shot2.output.set('/tmp/SEQ001_HSNI_003_0020_v001.mov')
        shot2.handle.set(10)
        shot2.track.set(1)

        shot3 = seq.create_shot('0030')
        shot3.startFrame.set(65)
        shot3.endFrame.set(110)
        shot3.sequenceStartFrame.set(66)
        shot3.output.set('/tmp/SEQ001_HSNI_003_0030_v001.mov')
        shot3.handle.set(10)
        shot3.track.set(1)

        # set a camera for shot4
        shot3.set_camera('persp')

        self.assertEqual(shot1.track.get(), 1)
        self.assertEqual(shot2.track.get(), 1)
        self.assertEqual(shot3.track.get(), 1)

        # now update it with test_v002.xml
        sm.from_edl(path)

        # check if there are 4 shots
        self.assertEqual(4, len(seq.shots.get()))

        # check shot data
        self.assertEqual('0010', shot1.shotName.get())
        self.assertEqual(1, shot1.track.get())
        self.assertEqual(1.0, shot1.sequenceStartFrame.get())
        self.assertEqual(54.0, shot1.sequenceEndFrame.get())
        self.assertEqual(-10.0, shot1.startFrame.get())
        self.assertEqual(43.0, shot1.endFrame.get())

        # Clip2
        self.assertEqual('0020', shot2.shotName.get())
        self.assertEqual(1, shot2.track.get())
        self.assertEqual(55.0, shot2.sequenceStartFrame.get())
        self.assertEqual(76.0, shot2.sequenceEndFrame.get())
        self.assertEqual(44.0, shot2.startFrame.get())
        self.assertEqual(65.0, shot2.endFrame.get())

        # Clip3
        self.assertEqual('0030', shot3.shotName.get())
        self.assertEqual(1, shot3.track.get())
        self.assertEqual(77.0, shot3.sequenceStartFrame.get())
        self.assertEqual(133.0, shot3.sequenceEndFrame.get())
        self.assertEqual(65.0, shot3.startFrame.get())
        self.assertEqual(121.0, shot3.endFrame.get())

        # Clip4
        # there should be an extra shot
        shot4 = seq.shots.get()[-1]
        self.assertEqual('0030', shot4.shotName.get())
        self.assertEqual(1, shot4.track.get())
        self.assertEqual(133.0, shot4.sequenceStartFrame.get())
        self.assertEqual(189.0, shot4.sequenceEndFrame.get())
        self.assertEqual(65.0, shot4.startFrame.get())
        self.assertEqual(121.0, shot4.endFrame.get())

        # check if their cameras also the same
        self.assertEqual(
            shot3.get_camera(),
            shot4.get_camera()
        )

    def test_from_xml_updates_sequencer_hierarchy_with_shots_removed(self):
        """testing if from_xml method will update Sequences and shots
        correctly with the xml file
        """
        path = os.path.abspath('./test_data/test_v003.xml')

        sm = pymel.core.PyNode('sequenceManager1')
        sm.set_version('v001')
        seq = sm.create_sequence('SEQ001_HSNI_003')

        shot1 = seq.create_shot('0010')
        shot1.startFrame.set(0)
        shot1.endFrame.set(33)
        shot1.sequenceStartFrame.set(1)
        shot1.output.set('/tmp/SEQ001_HSNI_003_0010_v001.mov')
        shot1.handle.set(10)
        shot1.track.set(1)

        shot2 = seq.create_shot('0020')
        shot2.startFrame.set(34)
        shot2.endFrame.set(64)
        shot2.sequenceStartFrame.set(35)
        shot2.output.set('/tmp/SEQ001_HSNI_003_0020_v001.mov')
        shot2.handle.set(10)
        shot2.track.set(1)

        shot3 = seq.create_shot('0030')
        shot3.startFrame.set(65)
        shot3.endFrame.set(110)
        shot3.sequenceStartFrame.set(66)
        shot3.output.set('/tmp/SEQ001_HSNI_003_0030_v001.mov')
        shot3.handle.set(10)
        shot3.track.set(1)

        self.assertEqual(shot1.track.get(), 1)
        self.assertEqual(shot2.track.get(), 1)
        self.assertEqual(shot3.track.get(), 1)

        # now update it with test_v002.xml
        sm.from_xml(path)

        # we should have 2 shots only
        self.assertEqual(2, len(seq.shots.get()))

        # check shot data
        self.assertEqual('0010', shot1.shotName.get())
        self.assertEqual(1, shot1.track.get())
        self.assertEqual(1.0, shot1.sequenceStartFrame.get())
        self.assertEqual(54.0, shot1.sequenceEndFrame.get())
        self.assertEqual(-10.0, shot1.startFrame.get())
        self.assertEqual(43.0, shot1.endFrame.get())

        # Clip2
        # removed

        # Clip3
        self.assertEqual('0030', shot3.shotName.get())
        self.assertEqual(1, shot3.track.get())
        self.assertEqual(55.0, shot3.sequenceStartFrame.get())
        self.assertEqual(110.0, shot3.sequenceEndFrame.get())
        self.assertEqual(65.0, shot3.startFrame.get())
        self.assertEqual(120.0, shot3.endFrame.get())

    def test_to_xml_will_generate_proper_xml_string(self):
        """testing if a proper xml compatible string will be generated with
        to_xml() method
        """
        path = os.path.abspath('./test_data/test_v001.xml')

        sm = pymel.core.PyNode('sequenceManager1')
        sm.set_shot_name_template('<Sequence>_<Shot>_<Version>')
        sm.set_version('v001')

        seq1 = sm.create_sequence('SEQ001_HSNI_003')

        shot1 = seq1.create_shot('0010')
        shot1.startFrame.set(0)
        shot1.endFrame.set(33)
        shot1.sequenceStartFrame.set(1)
        shot1.output.set('/tmp/SEQ001_HSNI_003_0010_v001.mov')
        shot1.handle.set(10)
        shot1.track.set(1)

        shot2 = seq1.create_shot('0020')
        shot2.startFrame.set(34)
        shot2.endFrame.set(64)
        shot2.sequenceStartFrame.set(35)
        shot2.output.set('/tmp/SEQ001_HSNI_003_0020_v001.mov')
        shot2.handle.set(10)
        shot2.track.set(1)

        shot3 = seq1.create_shot('0030')
        shot3.startFrame.set(65)
        shot3.endFrame.set(110)
        shot3.sequenceStartFrame.set(66)
        shot3.output.set('/tmp/SEQ001_HSNI_003_0030_v001.mov')
        shot3.handle.set(10)
        shot3.track.set(1)

        self.assertEqual(shot1.track.get(), 1)
        self.assertEqual(shot2.track.get(), 1)
        self.assertEqual(shot3.track.get(), 1)

        result = sm.to_xml()
        with open(path) as f:
            expected = f.read()

        self.maxDiff = None
        self.assertEqual(expected, result)

    def test_create_sequence_is_working_properly(self):
        """testing if create_sequence is working properly
        """
        seq = self.sm.create_sequence()
        self.assertEqual(seq.type(), 'sequencer')

        self.maxDiff = None
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
        seq1 = self.sm.create_sequence('sequence1')
        seq1.create_shot('shot1')
        seq1.create_shot('shot2')
        seq1.create_shot('shot3')

        l = self.sm.to_edl()
        self.assertIsInstance(
            l,
            edl.List
        )

    def test_to_edl_will_generate_a_proper_edl_content(self):
        """testing if to_edl will generate a proper edl content
        """
        edl_path = os.path.abspath('./test_data/test_v001.edl')

        sm = pymel.core.PyNode('sequenceManager1')
        sm.set_version('v001')

        sm = pymel.core.PyNode('sequenceManager1')
        sm.set_shot_name_template('<Sequence>_<Shot>_<Version>')
        sm.set_version('v001')

        seq1 = sm.create_sequence('SEQ001_HSNI_003')

        shot1 = seq1.create_shot('0010')
        shot1.startFrame.set(0)
        shot1.endFrame.set(33)
        shot1.sequenceStartFrame.set(1)
        shot1.output.set('/tmp/SEQ001_HSNI_003_0010_v001.mov')
        shot1.handle.set(10)
        shot1.track.set(1)

        shot2 = seq1.create_shot('0020')
        shot2.startFrame.set(34)
        shot2.endFrame.set(64)
        shot2.sequenceStartFrame.set(35)
        shot2.output.set('/tmp/SEQ001_HSNI_003_0020_v001.mov')
        shot2.handle.set(10)
        shot2.track.set(1)

        shot3 = seq1.create_shot('0030')
        shot3.startFrame.set(65)
        shot3.endFrame.set(110)
        shot3.sequenceStartFrame.set(66)
        shot3.output.set('/tmp/SEQ001_HSNI_003_0030_v001.mov')
        shot3.handle.set(10)
        shot3.track.set(1)

        self.assertEqual(shot1.track.get(), 1)
        self.assertEqual(shot2.track.get(), 1)
        self.assertEqual(shot3.track.get(), 1)

        l = sm.to_edl()
        result = l.to_string()

        with open(edl_path) as f:
            expected_edl_content = f.read()

        self.assertEqual(
            expected_edl_content,
            result
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

    def test_generate_sequence_structure_will_generate_sequences_and_shots_with_correct_number_of_tracks(self):
        """testing if a proper sequence structure will be generated by using
        the generate_sequence_structure() method with correct number of tracks
        """
        path = os.path.abspath('./test_data/test_v001.xml')

        sm = pymel.core.PyNode('sequenceManager1')
        sm.from_xml(path)

        seq1 = sm.sequences.get()[0]
        shots = seq1.shots.get()
        shot1 = shots[0]
        shot2 = shots[1]
        shot3 = shots[2]

        self.assertEqual(shot1.track.get(), 1)
        self.assertEqual(shot2.track.get(), 1)
        self.assertEqual(shot3.track.get(), 1)

        seq = sm.generate_sequence_structure()

        tracks = seq.media.video.tracks
        self.assertEqual(len(tracks), 1)
        track1 = tracks[0]

        clips = track1.clips
        self.assertEqual(len(clips), 3)

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

    def test_set_task_name_is_working_properly(self):
        """testing if set_task_name() is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        self.assertFalse(sm.hasAttr('task_name'))
        test_task_name = 'Animation'
        sm.set_task_name(test_task_name)
        self.assertTrue(sm.hasAttr('task_name'))
        self.assertEqual(sm.task_name.get(), test_task_name)

    def test_get_task_name_is_working_properly(self):
        """testing if set_task_name() is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        self.assertFalse(sm.hasAttr('task_name'))
        test_task_name = 'Animation'
        sm.set_task_name(test_task_name)
        self.assertTrue(sm.hasAttr('task_name'))
        self.assertEqual(sm.get_task_name(), test_task_name)

    def test_get_task_name_will_create_attribute_if_missing(self):
        """testing if get_task_name() will create the missing task_name attribute
        """
        sm = pymel.core.PyNode('sequenceManager1')
        self.assertFalse(sm.hasAttr('task_name'))
        result = sm.get_task_name()
        self.assertTrue(sm.hasAttr('task_name'))
        self.assertEqual(result, '')

    def test_set_take_name_is_working_properly(self):
        """testing if set_take_name() is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        self.assertFalse(sm.hasAttr('take_name'))
        test_take_name = 'Main'
        sm.set_take_name(test_take_name)
        self.assertTrue(sm.hasAttr('take_name'))
        self.assertEqual(sm.take_name.get(), test_take_name)

    def test_get_take_name_is_working_properly(self):
        """testing if set_take_name() is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        self.assertFalse(sm.hasAttr('take_name'))
        test_take_name = 'Main'
        sm.set_take_name(test_take_name)
        self.assertTrue(sm.hasAttr('take_name'))
        self.assertEqual(sm.get_take_name(), test_take_name)

    def test_get_take_name_will_create_attribute_if_missing(self):
        """testing if get_take_name() will create the missing take_name attribute
        """
        sm = pymel.core.PyNode('sequenceManager1')
        self.assertFalse(sm.hasAttr('take_name'))
        result = sm.get_take_name()
        self.assertTrue(sm.hasAttr('take_name'))
        self.assertEqual(result, '')

    def test_generate_sequence_structure_is_working_properly(self):
        """testing if generate_sequence_structure() method is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        from anima.env import mayaEnv
        mayaEnv.Maya.set_fps(fps=24)

        sm.set_shot_name_template('<Sequence>_<Shot>_<Version>')
        sm.set_version('v001')
        seq1 = sm.create_sequence('SEQ001_HSNI_003')

        shot1 = seq1.create_shot('0010')
        shot1.startFrame.set(0)
        shot1.endFrame.set(24)
        shot1.sequenceStartFrame.set(0)
        shot1.track.set(1)
        shot1.output.set('/tmp/SEQ001_HSNI_003_0010_v001.mov')
        shot1.handle.set(10)

        shot2 = seq1.create_shot('0020')
        shot2.startFrame.set(10)
        shot2.endFrame.set(35)
        shot2.sequenceStartFrame.set(25)
        shot2.track.set(1)
        shot2.output.set('/tmp/SEQ001_HSNI_003_0020_v001.mov')
        shot2.handle.set(15)

        shot3 = seq1.create_shot('0030')
        shot3.startFrame.set(25)
        shot3.endFrame.set(50)
        shot3.sequenceStartFrame.set(45)
        shot3.track.set(2)
        shot3.output.set('/tmp/SEQ001_HSNI_003_0030_v001.mov')
        shot3.handle.set(20)

        seq = sm.generate_sequence_structure()
        self.assertIsInstance(seq, Sequence)

        rate = seq.rate
        self.assertEqual('24', rate.timebase)
        self.assertEqual(False, rate.ntsc)

        self.assertEqual('00:00:00:00', seq.timecode)
        self.assertEqual(False, seq.ntsc)

        media = seq.media
        self.assertIsInstance(media, Media)

        video = media.video
        self.assertIsInstance(video, Video)
        self.assertIsNone(media.audio)

        self.assertEqual(2, len(video.tracks))

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
        self.assertEqual('Video', clip1.type)
        self.assertEqual('SEQ001_HSNI_003_0010_v001', clip1.id)
        self.assertEqual('SEQ001_HSNI_003_0010_v001', clip1.name)
        self.assertEqual(10, clip1.in_)   # handle
        self.assertEqual(35, clip1.out)  # handle + duration
        self.assertEqual(0, clip1.start)  # sequenceStartFrame
        self.assertEqual(25, clip1.end)  # sequenceEndFrame + 1

        clip2 = track1.clips[1]
        self.assertIsInstance(clip2, Clip)
        self.assertEqual('Video', clip2.type)
        self.assertEqual('SEQ001_HSNI_003_0020_v001', clip2.id)
        self.assertEqual('SEQ001_HSNI_003_0020_v001', clip2.name)
        self.assertEqual(15, clip2.in_)   # handle
        self.assertEqual(41, clip2.out)  # handle + duration
        self.assertEqual(25, clip2.start)  # sequenceStartFrame
        self.assertEqual(51, clip2.end)  # sequenceEndFrame + 1

        clip3 = track2.clips[0]
        self.assertIsInstance(clip3, Clip)
        self.assertEqual('Video', clip3.type)
        self.assertEqual('SEQ001_HSNI_003_0030_v001', clip3.id)
        self.assertEqual('SEQ001_HSNI_003_0030_v001', clip3.name)
        self.assertEqual(20, clip3.in_)   # startFrame
        self.assertEqual(46, clip3.out)  # endFrame + 1
        self.assertEqual(45, clip3.start)  # sequenceStartFrame
        self.assertEqual(71, clip3.end)  # sequenceEndFrame + 1

        file1 = clip1.file
        self.assertIsInstance(file1, File)
        self.assertEqual('SEQ001_HSNI_003_0010_v001', file1.name)
        self.assertEqual('file://localhost/tmp/SEQ001_HSNI_003_0010_v001.mov',
                         file1.pathurl)
        self.assertEqual(45, file1.duration)  # including handles

        file2 = clip2.file
        self.assertIsInstance(file2, File)
        self.assertEqual('SEQ001_HSNI_003_0020_v001', file2.name)
        self.assertEqual('file://localhost/tmp/SEQ001_HSNI_003_0020_v001.mov',
                         file2.pathurl)
        self.assertEqual(56, file2.duration)  # including handles

        file3 = clip3.file
        self.assertIsInstance(file3, File)
        self.assertEqual('SEQ001_HSNI_003_0030_v001', file3.name)
        self.assertEqual('file://localhost/tmp/SEQ001_HSNI_003_0030_v001.mov',
                         file3.pathurl)
        self.assertEqual(66, file3.duration)  # including handles

