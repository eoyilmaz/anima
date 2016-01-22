# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import unittest

# prepare for test
os.environ['ANIMA_TEST_SETUP'] = ""

from pymel import core as pm

from anima.env.mayaEnv.render_slicer import RenderSlicer


class RenderSlicerTester(unittest.TestCase):
    """test the ``anima.env.mayaEnv.render_slicer.RenderSlicer`` class
    """

    def setUp(self):
        """setup the test
        """
        # create a new scene
        pm.newFile(force=True)
        # create a render camera
        self.camera = pm.nt.Camera()

    def test_camera_argument_is_None(self):
        """testing if setting the camera argument to None will raise a
        TypeError
        """
        with self.assertRaises(TypeError) as cm:
            RenderSlicer(camera=None)

        self.assertEqual(
            str(cm.exception),
            'Please supply a Maya camera'
        )

    def test_camera_attribute_is_set_to_None(self):
        """testing if setting the camera attribute to None will raise a
        TypeError
        """
        rs = RenderSlicer(camera=self.camera)
        with self.assertRaises(TypeError) as cm:
            rs.camera = None

        self.assertEqual(
            str(cm.exception),
            'Please supply a Maya camera'
        )

    def test_camera_argument_is_not_camera(self):
        """testing if a TypeError will be raised when the camera argument value
        is not a Maya camera object
        """
        with self.assertRaises(TypeError) as cm:
            RenderSlicer(camera='not a maya camera')

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.camera should be a Maya camera, not str'
        )

    def test_camera_attribute_is_set_to_a_non_camera_object(self):
        """testing if setting the camera attribute to a non camera object will
        raise a TypeError
        """
        rs = RenderSlicer(camera=self.camera)
        with self.assertRaises(TypeError) as cm:
            rs.camera = 'not a maya camera'

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.camera should be a Maya camera, not str'
        )

    def test_slices_in_x_argument_is_skipped(self):
        """testing if the slices_in_x attribute will be set to the default
        value if the slices_in_x argument is skipped
        """
        rs = RenderSlicer(camera=self.camera)
        self.assertEqual(rs.slices_in_x, 5)

    def test_slices_in_x_argument_is_None(self):
        """testing if a TypeError will be raised if the slices_in_x argument is
        None
        """
        with self.assertRaises(TypeError) as cm:
            RenderSlicer(camera=self.camera, slices_in_x=None)

        self.assertEqual(
            str(cm.exception),
            "RenderSlicer.slices_in_x should be a non-zero positive integer, "
            "not NoneType"
        )

    def test_slices_in_x_attribute_is_set_to_None(self):
        """testing if a TypeError will be raised when the slices_in_x attribute
        is set to None
        """
        rs = RenderSlicer(camera=self.camera)
        with self.assertRaises(TypeError) as cm:
            rs.slices_in_x = None

        self.assertEqual(
            str(cm.exception),
            "RenderSlicer.slices_in_x should be a non-zero positive integer, "
            "not NoneType"
        )

    def test_slices_in_x_argument_is_not_an_integer(self):
        """testing if a TypeError will be raised if the slices_in_x argument is
        not an integer
        """
        with self.assertRaises(TypeError) as cm:
            RenderSlicer(camera=self.camera, slices_in_x='not an integer')

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.slices_in_x should be a non-zero positive integer, '
            'not str'
        )

    def test_slices_in_x_attribute_is_set_to_a_value_other_than_an_integer(self):
        """testing if a TypeError will be tested if the slices_in_x attribute
        is set to a value other than an integer
        """
        rs = RenderSlicer(camera=self.camera)
        with self.assertRaises(TypeError) as cm:
            rs.slices_in_x = 'not an integer'

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.slices_in_x should be a non-zero positive integer, '
            'not str'
        )

    def test_slices_in_x_argument_is_zero(self):
        """testing if a ValueError will be raised if the slices_in_x argument
        is zero
        """
        with self.assertRaises(ValueError) as cm:
            RenderSlicer(camera=self.camera, slices_in_x=0)

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.slices_in_x should be a non-zero positive integer'
        )

    def test_slices_in_x_attribute_is_zero(self):
        """testing if a ValueError will be raised when the slices_in_x
        attribute is set to zero
        """
        rs = RenderSlicer(camera=self.camera)
        with self.assertRaises(ValueError) as cm:
            rs.slices_in_x = 0

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.slices_in_x should be a non-zero positive integer'
        )

    def test_slices_in_x_argument_is_smaller_than_1(self):
        """testing if a ValueError will be raised if the slices_in_x argument
        value is smaller than 1
        """
        with self.assertRaises(ValueError) as cm:
            RenderSlicer(camera=self.camera, slices_in_x=-1)

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.slices_in_x should be a non-zero positive integer'
        )

    def test_slices_in_x_attribute_is_smaller_than_1(self):
        """testing if a ValueError will be raised when the slices_in_x
        attribute is set to a value smaller than 1
        """
        rs = RenderSlicer(camera=self.camera)
        with self.assertRaises(ValueError) as cm:
            rs.slices_in_x = 0

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.slices_in_x should be a non-zero positive integer'
        )

    def test_slices_in_x_argument_is_working_properly(self):
        """testing if the slices_in_x argument value is correctly passed to the
        slices_in_x attribute
        """
        test_value = 1001
        rs = RenderSlicer(camera=self.camera, slices_in_x=test_value)
        self.assertEqual(rs.slices_in_x, test_value)

    def test_slices_in_x_attribute_is_working_properly(self):
        """testing if the slices_in_x attribute is properly working
        """
        test_value = 1001
        rs = RenderSlicer(camera=self.camera, slices_in_x=12)
        self.assertNotEqual(rs.slices_in_x, test_value)
        rs.slices_in_x = test_value
        self.assertEqual(rs.slices_in_x, test_value)

    def test_slices_in_y_argument_is_skipped(self):
        """testing if the slices_in_y attribute will be set to the default
        value if the slices_in_y argument is skipped
        """
        rs = RenderSlicer(camera=self.camera)
        self.assertEqual(rs.slices_in_y, 5)

    def test_slices_in_y_argument_is_None(self):
        """testing if a TypeError will be raised if the slices_in_y argument is
        None
        """
        with self.assertRaises(TypeError) as cm:
            RenderSlicer(camera=self.camera, slices_in_y=None)

        self.assertEqual(
            str(cm.exception),
            "RenderSlicer.slices_in_y should be a non-zero positive integer, "
            "not NoneType"
        )

    def test_slices_in_y_attribute_is_set_to_None(self):
        """testing if a TypeError will be raised when the slices_in_y attribute
        is set to None
        """
        rs = RenderSlicer(camera=self.camera)
        with self.assertRaises(TypeError) as cm:
            rs.slices_in_y = None

        self.assertEqual(
            str(cm.exception),
            "RenderSlicer.slices_in_y should be a non-zero positive integer, "
            "not NoneType"
        )

    def test_slices_in_y_argument_is_not_an_integer(self):
        """testing if a TypeError will be raised if the slices_in_y argument is
        not an integer
        """
        with self.assertRaises(TypeError) as cm:
            RenderSlicer(camera=self.camera, slices_in_y='not an integer')

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.slices_in_y should be a non-zero positive integer, '
            'not str'
        )

    def test_slices_in_y_attribute_is_set_to_a_value_other_than_an_integer(self):
        """testing if a TypeError will be tested if the slices_in_y attribute
        is set to a value other than an integer
        """
        rs = RenderSlicer(camera=self.camera)
        with self.assertRaises(TypeError) as cm:
            rs.slices_in_y = 'not an integer'

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.slices_in_y should be a non-zero positive integer, '
            'not str'
        )

    def test_slices_in_y_argument_is_zero(self):
        """testing if a ValueError will be raised if the slices_in_y argument
        is zero
        """
        with self.assertRaises(ValueError) as cm:
            RenderSlicer(camera=self.camera, slices_in_y=0)

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.slices_in_y should be a non-zero positive integer'
        )

    def test_slices_in_y_attribute_is_zero(self):
        """testing if a ValueError will be raised when the slices_in_y
        attribute is set to zero
        """
        rs = RenderSlicer(camera=self.camera)
        with self.assertRaises(ValueError) as cm:
            rs.slices_in_y = 0

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.slices_in_y should be a non-zero positive integer'
        )

    def test_slices_in_y_argument_is_smaller_than_1(self):
        """testing if a ValueError will be raised if the slices_in_y argument
        value is smaller than 1
        """
        with self.assertRaises(ValueError) as cm:
            RenderSlicer(camera=self.camera, slices_in_y=-1)

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.slices_in_y should be a non-zero positive integer'
        )

    def test_slices_in_y_attribute_is_smaller_than_1(self):
        """testing if a ValueError will be raised when the slices_in_y
        attribute is set to a value smaller than 1
        """
        rs = RenderSlicer(camera=self.camera)
        with self.assertRaises(ValueError) as cm:
            rs.slices_in_y = 0

        self.assertEqual(
            str(cm.exception),
            'RenderSlicer.slices_in_y should be a non-zero positive integer'
        )

    def test_slices_in_y_argument_is_working_properly(self):
        """testing if the slices_in_y argument value is correctly passed to the
        slices_in_y attribute
        """
        test_value = 1001
        rs = RenderSlicer(camera=self.camera, slices_in_y=test_value)
        self.assertEqual(rs.slices_in_y, test_value)

    def test_slices_in_y_attribute_is_working_properly(self):
        """testing if the slices_in_y attribute is properly working
        """
        test_value = 1001
        rs = RenderSlicer(camera=self.camera, slices_in_y=12)
        self.assertNotEqual(rs.slices_in_y, test_value)
        rs.slices_in_y = test_value
        self.assertEqual(rs.slices_in_y, test_value)

    def test_do_slice_will_create_data_attributes_on_camera(self):
        """testing if calling the do_slice() method will create the data
        attributes on the camera
        """
        rs = RenderSlicer(camera=self.camera, slices_in_x=10, slices_in_y=20)
        rs.do_slice()

        self.assertTrue(rs.camera.hasAttr('isSliced'))
        self.assertTrue(rs.camera.hasAttr('nonSlicedResolutionX'))
        self.assertTrue(rs.camera.hasAttr('nonSlicedResolutionY'))
        self.assertTrue(rs.camera.hasAttr('slicesInX'))
        self.assertTrue(rs.camera.hasAttr('slicesInY'))

    def test_do_slice_will_set_the_data_attributes_on_camera(self):
        """testing if calling the do_slice() method will set the data
        attributes properly on camera
        """
        # check the scene render resolution first
        dres = pm.PyNode('defaultResolution')
        dres.width.set(960)
        dres.height.set(540)

        rs = RenderSlicer(camera=self.camera, slices_in_x=10, slices_in_y=20)
        rs.do_slice()

        self.assertEqual(rs.camera.isSliced.get(), True)
        self.assertEqual(rs.camera.nonSlicedResolutionX.get(), 960)
        self.assertEqual(rs.camera.nonSlicedResolutionY.get(), 540)
        self.assertEqual(rs.camera.slicesInX.get(), 10)
        self.assertEqual(rs.camera.slicesInY.get(), 20)

    def test_do_slice_will_work_on_previously_sliced_camera(self):
        """testing if the calling do_slice() method will also work with a
        previously sliced camera
        """
        self.fail('test is not implemented yet')

    def test_do_slice_will_set_the_render_resolution(self):
        """testing if calling do_slice() method will set the render resolution
        """
        # check the scene render resolution first
        dres = pm.PyNode('defaultResolution')
        dres.width.set(960)
        dres.height.set(540)

        rs = RenderSlicer(camera=self.camera, slices_in_x=10, slices_in_y=20)
        rs.do_slice()

        self.assertEqual(dres.width.get(), 96)
        self.assertEqual(dres.height.get(), 27)

    def test_do_slice_will_set_the_pan_zoom_enabled_attribute_of_the_camera(self):
        """testing if calling the do_slice() method will set the panZoomEnabled
        attribute of the camera
        """
        rs = RenderSlicer(camera=self.camera, slices_in_x=10, slices_in_y=20)
        rs.do_slice()
        self.assertEqual(self.camera.panZoomEnabled.get(), True)

    def test_do_slice_will_set_the_render_pan_zoom_attribute_of_the_camera(self):
        """testing if calling the do_slice() method will set the renderPanZoom
        attribute of the camera
        """
        rs = RenderSlicer(camera=self.camera, slices_in_x=10, slices_in_y=20)
        rs.do_slice()
        self.assertEqual(self.camera.renderPanZoom.get(), True)

    def test_do_slice_will_set_the_horizontal_pan_attribute_of_the_camera_properly(self):
        """testing if calling the do_slice() method will set the horizontalPan
        attribute of the camera properly
        """
        rs = RenderSlicer(camera=self.camera, slices_in_x=2, slices_in_y=3)
        rs.do_slice()
        expected_values = [
            -0.35433, 0.35433, -0.35433, 0.35433, -0.35433, 0.35433
        ]
        for i in range(6):
            pm.currentTime(i)
            self.assertAlmostEqual(
                self.camera.horizontalPan.get(),
                expected_values[i]
            )

    def test_do_slice_will_set_the_vertical_pan_attribute_of_the_camera_properly(self):
        """testing if calling the do_slice() method will set the verticalPan
        attribute of the camera properly
        """
        rs = RenderSlicer(camera=self.camera, slices_in_x=2, slices_in_y=3)
        rs.do_slice()
        expected_values = [
            -0.2657475, -0.2657475, 0, 0, 0.2657475, 0.2657475
        ]
        for i in range(6):
            pm.currentTime(i)
            self.assertAlmostEqual(
                self.camera.verticalPan.get(),
                expected_values[i]
            )

    def test_do_slice_will_set_the_zoom_attribute_of_the_camera_properly(self):
        """testing if calling the do_slice() method will set the zoom attribute
        of the camera properly
        """
        rs = RenderSlicer(camera=self.camera, slices_in_x=2, slices_in_y=3)
        rs.do_slice()
        self.assertAlmostEqual(self.camera.zoom.get(), 0.5)

    def test_do_slice_will_set_the_vertical_film_aperture_of_the_camera_properly(self):
        """testing if calling the do_slice() method will set the
        verticalFilmAperture attribute of the camera properly
        """
        rs = RenderSlicer(camera=self.camera, slices_in_x=2, slices_in_y=3)
        rs.do_slice()
        self.assertAlmostEqual(
            self.camera.verticalFilmAperture.get(),
            0.7972425
        )

    def test_do_slice_will_un_slice_if_the_scene_has_a_silced_camera(self):
        """testing if calling the do_slice() method will un-slice the scene if
        there is a previously sliced camera
        """
        self.fail('test is not implemented yet')
