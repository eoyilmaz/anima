# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Anima Istanbul
#
# This module is part of anima-tools and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

from anima.rig.limb import Limb
from anima.rig.character import Character
import unittest


class LimbTest(unittest.TestCase):

    def test_name_argument_is_None(self):
        """testing if a TypeError will be raised when the name argument isNone."""
        self.assertRaises(TypeError, Limb("xxxxxx", Character()))

if __name__ == "__main__":
    unittest.main()
