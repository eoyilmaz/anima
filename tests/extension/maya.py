# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import unittest
import pymel
import anima.extension.maya


class AttributeExtensionsTester(unittest.TestCase):
    """tests anima.extensions.maya
    """
    def setUp(self):
        """setup test
        """
        pymel.core.newFile(force=1)

    def test_next_available_extension_is_working_properly(self):
        """testing if Attribute.next_available extension is working properly
        """
        self.assertIsNotNone(
            pymel.core.general.Attribute.next_available
        )

    def test_next_available_with_no_previous_connections(self):
        """testing if Attribute.next_available will work properly for an array
        attribute with no previous connections
        """
        sequence_manager = pymel.core.ls(type=pymel.core.nt.SequenceManager)[0]

        attr = sequence_manager.sequences.next_available

        self.assertIsInstance(
            attr,
            pymel.core.general.Attribute
        )

        self.assertEqual(
            sequence_manager.sequences[0],
            sequence_manager.sequences.next_available
        )

    def test_next_available_with_no_multi_attribute(self):
        """testing if the attribute itself will be returned when it is not an
        multi attribute
        """
        time = pymel.core.ls(type=pymel.core.nt.Time)[0]
        self.assertEqual(
            time.outTime.next_available,
            time.outTime
        )

    def test_next_available_with_all_connected_attribute(self):
        """testing if the next available attribute will be returned when no
        empty plugs are present
        """
        sequence_manager = pymel.core.ls(type=pymel.core.nt.SequenceManager)[0]
        # connect new sequences
        seq1 = pymel.core.createNode('sequence')
        seq2 = pymel.core.createNode('sequence')
        seq3 = pymel.core.createNode('sequence')

        seq1.message >> sequence_manager.sequences[0]
        seq2.message >> sequence_manager.sequences[1]
        seq3.message >> sequence_manager.sequences[2]

        attr = sequence_manager.sequences.next_available
        self.assertIsInstance(
            attr,
            pymel.core.general.Attribute
        )
        self.assertEqual(
            3,
            sequence_manager.sequences.next_available.index()
        )
