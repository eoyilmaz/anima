# -*- coding: utf-8 -*-
import os
import unittest

# prepare for test
os.environ['ANIMA_TEST_SETUP'] = ""

from anima.env import mayaEnv  # to setup maya extensions
import pymel.core


class ShotExtensionTestCase(unittest.TestCase):
    """tests the anima.previs.ShotExtension class
    """

    def setUp(self):
        """set the test up
        """
        pymel.core.newFile(force=True)
        # create a test shot
        self.shot = pymel.core.createNode('shot')

    def test_set_handle_handle_argument_skipped(self):
        """testing if the default value (15) will be used when the handle
        attribute is skipped
        """
        self.shot.set_handle()
        self.assertEqual(
            self.shot.handle.get(), 15
        )

    def test_set_handle_handle_argument_is_not_an_integer(self):
        """testing if a TypeError will be raised when the handle argument is
        not an integer
        """
        with self.assertRaises(TypeError) as cm:
            self.shot.set_handle(handle='not an integer')

        self.assertEqual(
            cm.exception.message,
            '"handle" argument in Shot.set_handle() should be a '
            'non negative integer, not str'
        )

    def test_set_handle_handle_argument_is_working_properly(self):
        """testing if the handle argument value is correctly used in
        set_handle() method
        """
        test_handle = 120
        self.shot.set_handle(handle=test_handle)
        self.assertEqual(
            self.shot.handle.get(), test_handle
        )

    def test_set_handle_handle_argument_is_negative(self):
        """testing if a ValueError will be raised when the handle argument
        value is a negative integer
        """
        with self.assertRaises(ValueError) as cm:
            self.shot.set_handle(handle=-10)

        self.assertEqual(
            cm.exception.message,
            '"handle" argument in Shot.set_handle() should be a non negative '
            'integer, not -10'
        )

    def test_set_handle_will_create_handle_attribute(self):
        """testing if set_handle method will create handle integer attribute
        """
        self.shot.set_handle(handle=100)
        self.assertTrue(self.shot.hasAttr('handle'))
        self.assertEqual(self.shot.handle.get(), 100)

    def test_set_handle_will_be_able_to_set_handle_value_when_there_is_already_a_handle_attribute_defined(self):
        """testing if set_handle method will still be able to set the handle
        attribute value even there is a handle attribute defined previously
        """
        self.shot.addAttr('handle', at='short', k=True, min=0)
        self.shot.set_handle(handle=100)
        self.assertEqual(self.shot.handle.get(), 100)

    def test_sequence_property_is_working_properly(self):
        """testing if the sequence property is working properly
        """
        seq = pymel.core.createNode('sequencer')
        shot1 = seq.create_shot('shot1')
        self.assertEqual(
            seq,
            shot1.sequence
        )

    def test_mute_method_is_working_properly(self):
        """testing if mute() is working properly
        """
        shot1 = pymel.core.createNode('shot')
        self.assertFalse(
            pymel.core.shot(shot1, q=1, mute=True)
        )
        shot1.mute()
        self.assertTrue(
            pymel.core.shot(shot1, q=1, mute=True)
        )

    def test_unmute_method_is_working_properly(self):
        """testing if unmute() is working properly
        """
        shot1 = pymel.core.createNode('shot')
        shot1.mute()
        self.assertTrue(
            pymel.core.shot(shot1, q=1, mute=True)
        )
        shot1.unmute()
        self.assertFalse(
            pymel.core.shot(shot1, q=1, mute=True)
        )

    def test_set_output_is_working_properly(self):
        """testing if set_output method is working properly
        """
        shot1 = pymel.core.createNode('shot')
        self.assertFalse(shot1.hasAttr('output'))
        test_value = '/tmp/output.mov'
        shot1.set_output(test_value)
        self.assertTrue(shot1.hasAttr('output'))
        self.assertEqual(shot1.output.get(), test_value)

    def test_get_output_is_working_properly(self):
        """testing if get_output method is working properly
        """
        shot1 = pymel.core.createNode('shot')
        self.assertFalse(shot1.hasAttr('output'))
        test_value = '/tmp/output.mov'
        shot1.set_output(test_value)
        self.assertTrue(shot1.hasAttr('output'))
        self.assertEqual(shot1.get_output(), test_value)

    def test_get_output_will_create_the_attribute(self):
        """testing if get_output method will create the attribute if missing
        """
        shot1 = pymel.core.createNode('shot')
        self.assertFalse(shot1.hasAttr('output'))
        result = shot1.get_output()
        self.assertTrue(shot1.hasAttr('output'))
        self.assertEqual(result, '')

    def test_include_handles_is_working_properly(self):
        """testing if include_handles() method is working properly
        """
        shot1 = pymel.core.createNode('shot')
        shot1.set_handle(10)
        shot1.startFrame.set(10)
        shot1.endFrame.set(20)
        shot1.sequenceStartFrame.set(25)

        with shot1.include_handles:
            self.assertEqual(shot1.startFrame.get(), 0)
            self.assertEqual(shot1.endFrame.get(), 30)
            self.assertEqual(shot1.sequenceStartFrame.get(), 15)
            self.assertEqual(shot1.sequenceEndFrame.get(), 45)

        self.assertEqual(shot1.startFrame.get(), 10)
        self.assertEqual(shot1.endFrame.get(), 20)
        self.assertEqual(shot1.sequenceStartFrame.get(), 25)
        self.assertEqual(shot1.sequenceEndFrame.get(), 35)

    def test_include_handles_will_not_change_track_of_the_shot(self):
        """testing if include_handles() method will not change the shots track
        """
        sm = pymel.core.PyNode('sequenceManager1')
        seq = sm.create_sequence('seq1')

        shot1 = seq.create_shot('shot1')
        shot1.set_handle(10)
        shot1.startFrame.set(0)
        shot1.endFrame.set(24)
        shot1.sequenceStartFrame.set(0)
        shot1.track.set(1)

        shot2 = seq.create_shot('shot2')
        shot2.set_handle(10)
        shot2.startFrame.set(0)
        shot2.endFrame.set(24)
        shot2.sequenceStartFrame.set(25)
        shot2.track.set(1)

        shot3 = seq.create_shot('shot3')
        shot3.set_handle(10)
        shot3.startFrame.set(0)
        shot3.endFrame.set(24)
        shot3.sequenceStartFrame.set(50)
        shot3.track.set(1)

        self.assertEqual(shot1.track.get(), 1)
        self.assertEqual(shot2.track.get(), 1)
        self.assertEqual(shot3.track.get(), 1)

        with shot1.include_handles:
            pass

        with shot2.include_handles:
            pass

        with shot3.include_handles:
            pass

        self.assertEqual(shot1.track.get(), 1)
        self.assertEqual(shot2.track.get(), 1)
        self.assertEqual(shot3.track.get(), 1)

    def test_duration_property_is_working_properly(self):
        """testing if the duration property is working properly
        """
        shot1 = pymel.core.createNode('shot')
        shot1.set_handle(10)
        shot1.startFrame.set(10)
        shot1.endFrame.set(20)
        shot1.sequenceStartFrame.set(25)

        self.assertEqual(shot1.duration, 11)

    def test_full_shot_name_property_is_working_properly(self):
        """testing if the full_shot_name property is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        sm.set_shot_name_template('<Sequence>_<Shot>_<Version>')
        sm.set_version('v001')

        seq1 = sm.create_sequence('SEQ001_HSNI_003')
        shot1 = seq1.create_shot('0010')
        shot2 = seq1.create_shot('0020')

        self.assertEqual(shot1.full_shot_name, 'SEQ001_HSNI_003_0010_v001')
        self.assertEqual(shot2.full_shot_name, 'SEQ001_HSNI_003_0020_v001')

        # change template and test again
        sm.set_shot_name_template('<Shot>_<Version>')
        self.assertEqual(shot1.full_shot_name, '0010_v001')
        self.assertEqual(shot2.full_shot_name, '0020_v001')
