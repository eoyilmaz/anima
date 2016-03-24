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
import pymel.core as pm


class AttributeExtensionsTester(unittest.TestCase):
    """tests anima.extensions.maya
    """
    def setUp(self):
        """setup test
        """
        pm.newFile(force=1)

    def test_next_available_extension_is_working_properly(self):
        """testing if Attribute.next_available extension is working properly
        """
        self.assertIsNotNone(
            pm.general.Attribute.next_available
        )

    def test_next_available_with_no_previous_connections(self):
        """testing if Attribute.next_available will work properly for an array
        attribute with no previous connections
        """
        sequence_manager = pm.ls(type=pm.nt.SequenceManager)[0]

        attr = sequence_manager.sequences.next_available

        self.assertIsInstance(
            attr,
            pm.general.Attribute
        )

        self.assertEqual(
            sequence_manager.sequences[0],
            sequence_manager.sequences.next_available
        )

    def test_next_available_with_no_multi_attribute(self):
        """testing if the attribute itself will be returned when it is not an
        multi attribute
        """
        time = pm.ls(type=pm.nt.Time)[0]
        self.assertEqual(
            time.outTime.next_available,
            time.outTime
        )

    def test_next_available_with_all_connected_attribute(self):
        """testing if the next available attribute will be returned when no
        empty plugs are present
        """
        sequence_manager = pm.ls(type=pm.nt.SequenceManager)[0]
        # connect new sequences
        seq1 = pm.createNode('sequence')
        seq2 = pm.createNode('sequence')
        seq3 = pm.createNode('sequence')

        seq1.message >> sequence_manager.sequences[0]
        seq2.message >> sequence_manager.sequences[1]
        seq3.message >> sequence_manager.sequences[2]

        attr = sequence_manager.sequences.next_available
        self.assertIsInstance(
            attr,
            pm.general.Attribute
        )
        self.assertEqual(
            3,
            sequence_manager.sequences.next_available.index()
        )
