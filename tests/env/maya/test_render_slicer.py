# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Anima Istanbul
#
# This module is part of anima-tools and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

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

    def test_slices_in_x_attribute_is_working_properly(self):
        """testing if the slices_in_x attribute is properly working
        """
        test_value = 1001
        rs = RenderSlicer(camera=self.camera)
        self.assertNotEqual(rs.slices_in_x, test_value)
        rs.slices_in_x = test_value
        self.assertEqual(rs.slices_in_x, test_value)

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

    def test_slices_in_y_attribute_is_working_properly(self):
        """testing if the slices_in_y attribute is properly working
        """
        test_value = 1001
        rs = RenderSlicer(camera=self.camera)
        self.assertNotEqual(rs.slices_in_y, test_value)
        rs.slices_in_y = test_value
        self.assertEqual(rs.slices_in_y, test_value)

    def test_slice_will_create_data_attributes_on_camera(self):
        """testing if calling the slice() method will create the data
        attributes on the camera
        """
        rs = RenderSlicer(camera=self.camera)
        rs.slice(10, 20)

        self.assertTrue(rs.camera.hasAttr('isSliced'))
        self.assertTrue(rs.camera.hasAttr('nonSlicedResolutionX'))
        self.assertTrue(rs.camera.hasAttr('nonSlicedResolutionY'))
        self.assertTrue(rs.camera.hasAttr('slicesInX'))
        self.assertTrue(rs.camera.hasAttr('slicesInY'))

    def test_slice_will_set_the_data_attributes_on_camera(self):
        """testing if calling the slice() method will set the data
        attributes properly on camera
        """
        # check the scene render resolution first
        dres = pm.PyNode('defaultResolution')
        dres.width.set(960)
        dres.height.set(540)

        rs = RenderSlicer(camera=self.camera)
        rs.slice(10, 20)

        self.assertEqual(rs.camera.isSliced.get(), True)
        self.assertEqual(rs.camera.nonSlicedResolutionX.get(), 960)
        self.assertEqual(rs.camera.nonSlicedResolutionY.get(), 540)
        self.assertEqual(rs.camera.slicesInX.get(), 10)
        self.assertEqual(rs.camera.slicesInY.get(), 20)

    def test_slice_will_work_on_previously_sliced_camera(self):
        """testing if the calling slice() method will also work with a
        previously sliced camera
        """
        dres = pm.PyNode('defaultResolution')
        dres.width.set(960)
        dres.height.set(540)

        rs = RenderSlicer(camera=self.camera)
        rs.slice(10, 10)
        self.assertEqual(dres.width.get(), 96)
        self.assertEqual(dres.height.get(), 54)

        rs2 = RenderSlicer(camera=self.camera)
        rs2.slice(5, 5)
        self.assertEqual(dres.width.get(), 192)
        self.assertEqual(dres.height.get(), 108)

    def test_slice_will_set_the_render_resolution(self):
        """testing if calling slice() method will set the render resolution
        """
        # check the scene render resolution first
        dres = pm.PyNode('defaultResolution')
        dres.width.set(960)
        dres.height.set(540)

        rs = RenderSlicer(camera=self.camera)
        rs.slice(10, 20)

        self.assertEqual(dres.width.get(), 96)
        self.assertEqual(dres.height.get(), 27)

    def test_slice_will_set_the_pan_zoom_enabled_attribute_of_the_camera(self):
        """testing if calling the slice() method will set the panZoomEnabled
        attribute of the camera
        """
        rs = RenderSlicer(camera=self.camera)
        rs.slice(10, 20)
        self.assertEqual(self.camera.panZoomEnabled.get(), True)

    def test_slice_will_set_the_render_pan_zoom_attribute_of_the_camera(self):
        """testing if calling the slice() method will set the renderPanZoom
        attribute of the camera
        """
        rs = RenderSlicer(camera=self.camera)
        rs.slice(10, 20)
        self.assertEqual(self.camera.renderPanZoom.get(), True)

    def test_slice_will_set_the_horizontal_pan_attribute_of_the_camera_properly(self):
        """testing if calling the slice() method will set the horizontalPan
        attribute of the camera properly
        """
        rs = RenderSlicer(camera=self.camera)
        rs.slice(2, 3)
        expected_values = [
            -0.35433, 0.35433, -0.35433, 0.35433, -0.35433, 0.35433
        ]
        for i in range(6):
            pm.currentTime(i)
            self.assertAlmostEqual(
                self.camera.horizontalPan.get(),
                expected_values[i]
            )

    def test_slice_will_set_the_vertical_pan_attribute_of_the_camera_properly(self):
        """testing if calling the slice() method will set the verticalPan
        attribute of the camera properly
        """
        rs = RenderSlicer(camera=self.camera)
        rs.slice(2, 3)
        expected_values = [
            -0.2657475, -0.2657475, 0, 0, 0.2657475, 0.2657475
        ]
        for i in range(6):
            pm.currentTime(i)
            self.assertAlmostEqual(
                self.camera.verticalPan.get(),
                expected_values[i]
            )

    def test_slice_will_set_the_zoom_attribute_of_the_camera_properly(self):
        """testing if calling the slice() method will set the zoom attribute
        of the camera properly
        """
        rs = RenderSlicer(camera=self.camera)
        rs.slice(2, 3)
        self.assertAlmostEqual(self.camera.zoom.get(), 0.5)

    def test_slice_will_set_the_vertical_film_aperture_of_the_camera_properly(self):
        """testing if calling the slice() method will set the
        verticalFilmAperture attribute of the camera properly
        """
        rs = RenderSlicer(camera=self.camera)
        rs.slice(2, 3)
        self.assertAlmostEqual(
            self.camera.verticalFilmAperture.get(),
            0.7972425
        )

    def test_slice_will_un_slice_the_same_camera(self):
        """testing if calling the slice() method will un-slice the camera if
        it is already sliced
        """
        # check the scene render resolution first
        dres = pm.PyNode('defaultResolution')
        dres.width.set(960)
        dres.height.set(540)

        rs = RenderSlicer(camera=self.camera)
        rs.slice(10, 10)

        # check the render resolution
        self.assertEqual(dres.width.get(), 96)
        self.assertEqual(dres.height.get(), 54)

        # create a new camera and slice again
        rs2 = RenderSlicer(camera=self.camera)
        rs2.slice(5, 5)

        # check the resolution
        self.assertEqual(dres.width.get(), 192)
        self.assertEqual(dres.height.get(), 108)

    def test_slice_will_un_slice_if_the_scene_has_a_silced_camera(self):
        """testing if calling the slice() method will un-slice the scene if
        there is a previously sliced camera
        """
        # check the scene render resolution first
        dres = pm.PyNode('defaultResolution')
        dres.width.set(960)
        dres.height.set(540)

        rs = RenderSlicer(camera=self.camera)
        rs.slice(10, 10)

        # check the render resolution
        self.assertEqual(dres.width.get(), 96)
        self.assertEqual(dres.height.get(), 54)

        # create a new camera and slice again
        cam = pm.nt.Camera()
        rs2 = RenderSlicer(camera=cam)
        rs2.slice(5, 5)

        # check the resolution
        self.assertEqual(dres.width.get(), 192)
        self.assertEqual(dres.height.get(), 108)

    def test_slice_will_set_the_pixel_aspect_to_1(self):
        """testing if the slice() method will set the render pixel aspect to 1
        """
        dres = pm.PyNode('defaultResolution')
        dres.width.set(1920)
        dres.height.set(1080)
        dres.pixelAspect.set(2.5)

        rs = RenderSlicer(self.camera)
        rs.slice(10, 10)

        self.assertEqual(dres.pixelAspect.get(), 1)
        self.assertEqual(dres.width.get(), 192)
        self.assertEqual(dres.height.get(), 108)

    def test_unslice_will_set_the_pixel_aspect_to_1(self):
        """testing if the unslice() method will set the pixel aspect to 1
        """
        dres = pm.PyNode('defaultResolution')
        dres.width.set(1920)
        dres.height.set(1080)
        dres.pixelAspect.set(2.5)

        rs = RenderSlicer(self.camera)
        rs.slice(10, 10)
        rs.unslice()

        self.assertEqual(dres.pixelAspect.get(), 1)
        self.assertEqual(dres.width.get(), 1920)
        self.assertEqual(dres.height.get(), 1080)

    def test_unslice_scene_will_set_the_pixel_aspect_to_1(self):
        """testing if the unslice_scene() method will set the pixel aspect to 1
        """
        dres = pm.PyNode('defaultResolution')
        dres.width.set(1920)
        dres.height.set(1080)
        dres.pixelAspect.set(1.0)

        rs = RenderSlicer(self.camera)
        rs.slice(10, 10)
        rs.unslice_scene()

        self.assertEqual(dres.pixelAspect.get(), 1)
        self.assertEqual(dres.width.get(), 1920)
        self.assertEqual(dres.height.get(), 1080)

    def test_unslice_will_restore_original_render_resolution(self):
        """unslice will restore the original render resolution
        """
        dres = pm.PyNode('defaultResolution')
        dres.width.set(960)
        dres.height.set(540)

        rs = RenderSlicer(camera=self.camera)
        rs.slice(10, 10)

        self.assertEqual(dres.width.get(), 96)
        self.assertEqual(dres.height.get(), 54)

        rs.unslice()
        self.assertEqual(dres.width.get(), 960)
        self.assertEqual(dres.height.get(), 540)

    def test_unslice_will_set_the_is_sliced_attribute_of_the_camera_correctly(self):
        """testing if unslice() method will set the isSliced attribute of the
        camera correctly
        """
        rs = RenderSlicer(camera=self.camera)
        rs.slice(10, 10)

        self.assertTrue(self.camera.isSliced.get())

        rs.unslice()
        self.assertFalse(self.camera.isSliced.get())

    def test_unslice_will_set_the_is_sliced_attribute_correctly(self):
        """testing if unslice() method will set the is_sliced attribute\
        correctly
        """
        rs = RenderSlicer(camera=self.camera)
        rs.slice(10, 10)

        self.assertTrue(rs.is_sliced)

        rs.unslice()
        self.assertFalse(rs.is_sliced)

    def test_init_with_a_sliced_camera(self):
        """testing if initializing with a pre-sliced camera will work properly
        """
        dres = pm.PyNode('defaultResolution')
        dres.width.set(1000)
        dres.height.set(1000)

        rs = RenderSlicer(camera=self.camera)
        rs.slice(10, 10)

        rs2 = RenderSlicer(camera=self.camera)
        self.assertEqual(rs2.is_sliced, True)
        self.assertEqual(rs2.slices_in_x, 10)
        self.assertEqual(rs2.slices_in_y, 10)
        # self.assertEqual(rs2.original_resolution, 1000)