# -*- coding: utf-8 -*-

from anima.rig.limb import Limb
from anima.rig.character import Character
import unittest


class LimbTest(unittest.TestCase):

    def test_name_argument_is_None(self):
        """testing if a TypeError will be raised when the name argument isNone."""
        self.assertRaises(TypeError, Limb("xxxxxx", Character()))

if __name__ == "__main__":
    unittest.main()
