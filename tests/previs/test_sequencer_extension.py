# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import unittest

# prepare for test
os.environ['ANIMA_TEST_SETUP'] = ""

from anima.env import mayaEnv  # to setup maya extensions

import pymel.core


class SequencerExtensionTestCase(unittest.TestCase):
    """tests the anima.animation.SequencerExtension class
    """

    def setUp(self):
        """set up the test
        """
        pymel.core.newFile(force=True)

    def test_set_shot_handles_method_is_working_properly(self):
        """testing if the set_shot_handles method is working properly
        """
        s = pymel.core.createNode('sequencer')
        shot1 = s.create_shot('shot1')
        shot2 = s.create_shot('shot2')
        shot3 = s.create_shot('shot3')

        self.assertEqual(
            [shot1, shot2, shot3],
            s.all_shots
        )

        self.assertNotEqual(shot1.handle.get(), 50)
        self.assertNotEqual(shot2.handle.get(), 50)
        self.assertNotEqual(shot3.handle.get(), 50)

        s.set_shot_handles(50)
        self.assertEqual(shot1.handle.get(), 50)
        self.assertEqual(shot2.handle.get(), 50)
        self.assertEqual(shot3.handle.get(), 50)

    def test_create_shot_is_working_properly(self):
        """testing if SequencerExtension.create_shot() is working properly
        """
        s = pymel.core.createNode('sequencer')
        shot = s.create_shot(name='Test Shot', handle=14)
        self.assertIsInstance(shot, pymel.core.nt.Shot)

        self.assertEqual(
            'shot1',
            shot.name()
        )

        self.assertEqual(
            'Test Shot',
            shot.shotName.get()
        )

        self.assertEqual(
            14,
            shot.handle.get()
        )

        self.assertEqual(
            s,
            shot.message.outputs()[0]
        )

    def test_all_shots_property_is_working_properly(self):
        """testing if the all_shots property is working properly
        """
        s = pymel.core.createNode('sequencer')
        s1 = s.create_shot('shot1')
        s2 = s.create_shot('shot2')
        s3 = s.create_shot('shot3')

        self.assertItemsEqual(
            [s1, s2, s3],
            s.all_shots
        )

    def test_add_shot_with_an_unconnected_shot(self):
        """testing if the add_shot method is working properly for an
        unconnected shot
        """
        s = pymel.core.createNode('sequencer')
        s1 = pymel.core.createNode('shot')
        s.add_shot(s1)

        self.assertEqual(
            [s1],
            s.all_shots,
        )

    def test_add_shot_will_add_handle_attributes_if_doesnt_exists(self):
        """testing if add_shot method will add the handle attributes if the
        given shot doesn't have it
        """
        s = pymel.core.createNode('sequencer')
        s1 = pymel.core.createNode('shot')
        self.assertFalse(
            s1.hasAttr('handle')
        )

        s.add_shot(s1)

        self.assertTrue(
            s1.hasAttr('handle')
        )

        self.assertTrue(
            10,
            s1.handle.get()
        )

    def test_add_shot_with_a_connected_shot(self):
        """testing if the add_shot method is working properly for a shot which
        is already connected to another sequence
        """
        s1 = pymel.core.createNode('sequencer')
        s2 = pymel.core.createNode('sequencer')

        shot1 = s1.create_shot('shot1')
        shot2 = s1.create_shot('shot2')

        shot3 = s2.create_shot('shot3')
        shot4 = s2.create_shot('shot4')

        self.assertEqual(
            [shot1, shot2],
            s1.all_shots
        )

        self.assertEqual(
            [shot3, shot4],
            s2.all_shots
        )

        s1.add_shot(shot3)
        self.assertEqual(
            [shot1, shot2, shot3],
            s1.all_shots
        )

        self.assertEqual(
            [shot4],
            s2.all_shots
        )

        s1.add_shot(shot4)
        self.assertEqual(
            [shot1, shot2, shot3, shot4],
            s1.all_shots
        )

        self.assertEqual(
            [],
            s2.all_shots
        )

    def test_set_sequence_name_is_working_properly(self):
        """testing if the set_sequence_name is working properly
        """
        s1 = pymel.core.createNode('sequencer')
        self.assertFalse(s1.hasAttr('sequence_name'))

        s1.set_sequence_name('Test Sequence')
        self.assertTrue(s1.hasAttr('sequence_name'))

        self.assertEqual(
            s1.sequence_name.get(),
            'Test Sequence'
        )

    def test_get_sequence_name_is_working_properly(self):
        """testing if the get_sequence_name is working properly
        """
        s1 = pymel.core.createNode('sequencer')
        self.assertFalse(s1.hasAttr('sequence_name'))

        s1.set_sequence_name('Test Sequence')
        self.assertTrue(s1.hasAttr('sequence_name'))

        self.assertEqual(
            s1.get_sequence_name(),
            'Test Sequence'
        )

    def test_get_sequence_name_will_create_sequence_name_attribute_if_missing(self):
        """testing if the get_sequence_name will create the attribute if it is
        missing
        """
        s1 = pymel.core.createNode('sequencer')
        self.assertFalse(s1.hasAttr('sequence_name'))

        result = s1.get_sequence_name()
        self.assertTrue(s1.hasAttr('sequence_name'))

        self.assertEqual(s1.get_sequence_name(), result)

    def test_mute_shots_is_working_properly(self):
        """testing if mute shot is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        seq1 = sm.create_sequence('sequence1')
        shot1 = seq1.create_shot('shot1')
        shot2 = seq1.create_shot('shot2')
        shot3 = seq1.create_shot('shot3')

        self.assertFalse(pymel.core.shot(shot1, q=1, mute=1))
        self.assertFalse(pymel.core.shot(shot2, q=1, mute=1))
        self.assertFalse(pymel.core.shot(shot3, q=1, mute=1))

        seq1.mute_shots()

        self.assertTrue(pymel.core.shot(shot1, q=1, mute=1))
        self.assertTrue(pymel.core.shot(shot2, q=1, mute=1))
        self.assertTrue(pymel.core.shot(shot3, q=1, mute=1))

    def test_unmute_shots_is_working_properly(self):
        """testing if mute shot is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        seq1 = sm.create_sequence('sequence1')
        shot1 = seq1.create_shot('shot1')
        shot2 = seq1.create_shot('shot2')
        shot3 = seq1.create_shot('shot3')

        self.assertFalse(pymel.core.shot(shot1, q=1, mute=1))
        self.assertFalse(pymel.core.shot(shot2, q=1, mute=1))
        self.assertFalse(pymel.core.shot(shot3, q=1, mute=1))

        seq1.mute_shots()
        self.assertTrue(pymel.core.shot(shot1, q=1, mute=1))
        self.assertTrue(pymel.core.shot(shot2, q=1, mute=1))
        self.assertTrue(pymel.core.shot(shot3, q=1, mute=1))

        seq1.unmute_shots()
        self.assertFalse(pymel.core.shot(shot1, q=1, mute=1))
        self.assertFalse(pymel.core.shot(shot2, q=1, mute=1))
        self.assertFalse(pymel.core.shot(shot3, q=1, mute=1))

    def test_duration_property_is_working_properly(self):
        """testing if the duration property is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        seq1 = sm.create_sequence('sequence1')

        shot1 = seq1.create_shot('shot1')
        shot1.startFrame.set(10)
        shot1.endFrame.set(20)
        shot1.sequenceStartFrame.set(10)
        shot1.sequenceEndFrame.set(20)

        shot2 = seq1.create_shot('shot2')
        shot2.startFrame.set(11)
        shot2.endFrame.set(21)
        shot2.sequenceStartFrame.set(31)
        shot2.sequenceEndFrame.set(41)

        shot3 = seq1.create_shot('shot3')
        shot3.startFrame.set(51)
        shot3.endFrame.set(61)
        shot3.sequenceStartFrame.set(71)
        shot3.sequenceEndFrame.set(81)

        self.assertEqual(seq1.duration, 72)

    def test_manager_property_is_working_properly(self):
        """testing if manager property is working properly
        """
        sm = pymel.core.PyNode('sequenceManager1')
        seq1 = sm.create_sequence('SEQ001_HSNI_003')
        self.assertEqual(sm, seq1.manager)
