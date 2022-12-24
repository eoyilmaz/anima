# -*- coding: utf-8 -*-
"""Tests for the ``anima.dcc.mayaEnv.render_slicer.RenderSlicer`` class."""

import pytest

from anima.dcc.mayaEnv.render import RenderSlicer


@pytest.fixture(scope="function")
def prepare_scene(create_pymel):
    """Set up the tests."""
    pm = create_pymel
    # create a new scene
    pm.newFile(force=True)
    # create a render camera
    camera = pm.nt.Camera()
    yield camera


def test_camera_argument_is_None(prepare_scene):
    """testing if setting the camera argument to None will raise a TypeError"""
    with pytest.raises(TypeError) as cm:
        RenderSlicer(camera=None)

    assert str(cm.value) == "Please supply a Maya camera"


def test_camera_attribute_is_set_to_None(prepare_scene):
    """testing if setting the camera attribute to None will raise a TypeError."""
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    with pytest.raises(TypeError) as cm:
        rs.camera = None

    assert str(cm.value) == "Please supply a Maya camera"


def test_camera_argument_is_not_camera(prepare_scene):
    """testing if a TypeError will be raised when the camera argument value is not a
    Maya camera object.
    """
    with pytest.raises(TypeError) as cm:
        RenderSlicer(camera="not a maya camera")

    assert str(cm.value) == "RenderSlicer.camera should be a Maya camera, not str"


def test_camera_attribute_is_set_to_a_non_camera_object(prepare_scene):
    """testing if setting the camera attribute to a non camera object will
    raise a TypeError
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    with pytest.raises(TypeError) as cm:
        rs.camera = "not a maya camera"

    assert str(cm.value) == "RenderSlicer.camera should be a Maya camera, not str"


def test_slices_in_x_attribute_is_set_to_None(prepare_scene):
    """testing if a TypeError will be raised when the slices_in_x attribute
    is set to None
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    with pytest.raises(TypeError) as cm:
        rs.slices_in_x = None

    assert (
        str(cm.value)
        == "RenderSlicer.slices_in_x should be a non-zero positive integer, not NoneType"
    )


def test_slices_in_x_attribute_is_set_to_a_value_other_than_an_integer(prepare_scene):
    """testing if a TypeError will be tested if the slices_in_x attribute
    is set to a value other than an integer
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    with pytest.raises(TypeError) as cm:
        rs.slices_in_x = "not an integer"

    assert (
        str(cm.value)
        == "RenderSlicer.slices_in_x should be a non-zero positive integer, "
        "not str"
    )


def test_slices_in_x_attribute_is_zero(prepare_scene):
    """testing if a ValueError will be raised when the slices_in_x
    attribute is set to zero
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    with pytest.raises(ValueError) as cm:
        rs.slices_in_x = 0

    assert (
        str(cm.value)
        == "RenderSlicer.slices_in_x should be a non-zero positive integer"
    )


def test_slices_in_x_attribute_is_smaller_than_1(prepare_scene):
    """testing if a ValueError will be raised when the slices_in_x
    attribute is set to a value smaller than 1
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    with pytest.raises(ValueError) as cm:
        rs.slices_in_x = 0

    assert (
        str(cm.value)
        == "RenderSlicer.slices_in_x should be a non-zero positive integer"
    )


def test_slices_in_x_attribute_is_working_properly(prepare_scene):
    """testing if the slices_in_x attribute is properly working"""
    camera = prepare_scene
    test_value = 1001
    rs = RenderSlicer(camera=camera)
    assert rs.slices_in_x != test_value
    rs.slices_in_x = test_value
    assert rs.slices_in_x == test_value


def test_slices_in_y_attribute_is_set_to_None(prepare_scene):
    """testing if a TypeError will be raised when the slices_in_y attribute
    is set to None
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    with pytest.raises(TypeError) as cm:
        rs.slices_in_y = None

    assert (
        str(cm.value)
        == "RenderSlicer.slices_in_y should be a non-zero positive integer, not NoneType"
    )


def test_slices_in_y_attribute_is_set_to_a_value_other_than_an_integer(prepare_scene):
    """testing if a TypeError will be tested if the slices_in_y attribute
    is set to a value other than an integer
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    with pytest.raises(TypeError) as cm:
        rs.slices_in_y = "not an integer"

    assert (
        str(cm.value)
        == "RenderSlicer.slices_in_y should be a non-zero positive integer, "
        "not str",
    )


def test_slices_in_y_attribute_is_zero(prepare_scene):
    """testing if a ValueError will be raised when the slices_in_y
    attribute is set to zero
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    with pytest.raises(ValueError) as cm:
        rs.slices_in_y = 0

    assert (
        str(cm.value)
        == "RenderSlicer.slices_in_y should be a non-zero positive integer",
    )


def test_slices_in_y_attribute_is_smaller_than_1(prepare_scene):
    """testing if a ValueError will be raised when the slices_in_y
    attribute is set to a value smaller than 1
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    with pytest.raises(ValueError) as cm:
        rs.slices_in_y = 0

    assert (
        str(cm.value)
        == "RenderSlicer.slices_in_y should be a non-zero positive integer"
    )


def test_slices_in_y_attribute_is_working_properly(prepare_scene):
    """testing if the slices_in_y attribute is properly working"""
    camera = prepare_scene
    test_value = 1001
    rs = RenderSlicer(camera=camera)
    assert rs.slices_in_y != test_value
    rs.slices_in_y = test_value
    assert rs.slices_in_y == test_value


def test_slice_will_create_data_attributes_on_camera(prepare_scene):
    """testing if calling the slice() method will create the data
    attributes on the camera
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    rs.slice(10, 20)

    assert rs.camera.hasAttr("isSliced")
    assert rs.camera.hasAttr("nonSlicedResolutionX")
    assert rs.camera.hasAttr("nonSlicedResolutionY")
    assert rs.camera.hasAttr("slicesInX")
    assert rs.camera.hasAttr("slicesInY")


def test_slice_will_set_the_data_attributes_on_camera(prepare_scene, create_pymel):
    """testing if calling the slice() method will set the data
    attributes properly on camera
    """
    # check the scene render resolution first
    camera = prepare_scene
    pm = create_pymel
    dres = pm.PyNode("defaultResolution")
    dres.width.set(960)
    dres.height.set(540)

    rs = RenderSlicer(camera=camera)
    rs.slice(10, 20)

    assert rs.camera.isSliced.get() is True
    assert rs.camera.nonSlicedResolutionX.get() == 960
    assert rs.camera.nonSlicedResolutionY.get() == 540
    assert rs.camera.slicesInX.get() == 10
    assert rs.camera.slicesInY.get() == 20


def test_slice_will_work_on_previously_sliced_camera(prepare_scene, create_pymel):
    """testing if the calling slice() method will also work with a
    previously sliced camera
    """
    camera = prepare_scene
    pm = create_pymel
    dres = pm.PyNode("defaultResolution")
    dres.width.set(960)
    dres.height.set(540)

    rs = RenderSlicer(camera=camera)
    rs.slice(10, 10)
    assert dres.width.get() == 96
    assert dres.height.get() == 54

    rs2 = RenderSlicer(camera=camera)
    rs2.slice(5, 5)
    assert dres.width.get() == 192
    assert dres.height.get() == 108


def test_slice_will_set_the_render_resolution(prepare_scene, create_pymel):
    """testing if calling slice() method will set the render resolution"""
    # check the scene render resolution first
    pm = create_pymel
    camera = prepare_scene
    dres = pm.PyNode("defaultResolution")
    dres.width.set(960)
    dres.height.set(540)

    rs = RenderSlicer(camera=camera)
    rs.slice(10, 20)

    assert dres.width.get() == 96
    assert dres.height.get() == 27


def test_slice_will_set_the_pan_zoom_enabled_attribute_of_the_camera(
    prepare_scene, create_pymel
):
    """testing if calling the slice() method will set the panZoomEnabled
    attribute of the camera
    """
    pm = create_pymel
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    rs.slice(10, 20)
    assert camera.panZoomEnabled.get()


def test_slice_will_set_the_render_pan_zoom_attribute_of_the_camera(prepare_scene):
    """testing if calling the slice() method will set the renderPanZoom
    attribute of the camera
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    rs.slice(10, 20)
    assert camera.renderPanZoom.get()


def test_slice_will_set_the_horizontal_pan_attribute_of_the_camera_properly(
    prepare_scene, create_pymel
):
    """testing if calling the slice() method will set the horizontalPan
    attribute of the camera properly
    """
    pm = create_pymel
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    rs.slice(2, 3)
    expected_values = [-0.35433, 0.35433, -0.35433, 0.35433, -0.35433, 0.35433]
    for i in range(6):
        pm.currentTime(i)
        assert camera.horizontalPan.get() == pytest.approx(expected_values[i], abs=1e-3)


def test_slice_will_set_the_vertical_pan_attribute_of_the_camera_properly(
    prepare_scene, create_pymel
):
    """testing if calling the slice() method will set the verticalPan
    attribute of the camera properly
    """
    camera = prepare_scene
    pm = create_pymel
    rs = RenderSlicer(camera=camera)
    rs.slice(2, 3)
    expected_values = [-0.2657475, -0.2657475, 0, 0, 0.2657475, 0.2657475]
    for i in range(6):
        pm.currentTime(i)
        assert camera.verticalPan.get() == pytest.approx(expected_values[i], abs=1e-3)


def test_slice_will_set_the_zoom_attribute_of_the_camera_properly(prepare_scene):
    """testing if calling the slice() method will set the zoom attribute
    of the camera properly
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    rs.slice(2, 3)
    assert camera.zoom.get() == pytest.approx(0.5, abs=1e-3)


def test_slice_will_set_the_vertical_film_aperture_of_the_camera_properly(
    prepare_scene,
):
    """testing if calling the slice() method will set the
    verticalFilmAperture attribute of the camera properly
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    rs.slice(2, 3)
    assert camera.verticalFilmAperture.get() == pytest.approx(0.7972425, abs=1e-3)


def test_slice_will_un_slice_the_same_camera(prepare_scene, create_pymel):
    """testing if calling the slice() method will un-slice the camera if
    it is already sliced
    """
    camera = prepare_scene
    pm = create_pymel
    # check the scene render resolution first
    dres = pm.PyNode("defaultResolution")
    dres.width.set(960)
    dres.height.set(540)

    rs = RenderSlicer(camera=camera)
    rs.slice(10, 10)

    # check the render resolution
    assert dres.width.get() == 96
    assert dres.height.get() == 54

    # create a new camera and slice again
    rs2 = RenderSlicer(camera=camera)
    rs2.slice(5, 5)

    # check the resolution
    assert dres.width.get() == 192
    assert dres.height.get() == 108


def test_slice_will_un_slice_if_the_scene_has_a_silced_camera(
    prepare_scene, create_pymel
):
    """testing if calling the slice() method will un-slice the scene if
    there is a previously sliced camera
    """
    camera = prepare_scene
    pm = create_pymel
    # check the scene render resolution first
    dres = pm.PyNode("defaultResolution")
    dres.width.set(960)
    dres.height.set(540)

    rs = RenderSlicer(camera=camera)
    rs.slice(10, 10)

    # check the render resolution
    assert dres.width.get() == 96
    assert dres.height.get() == 54

    # create a new camera and slice again
    cam = pm.nt.Camera()
    rs2 = RenderSlicer(camera=cam)
    rs2.slice(5, 5)

    # check the resolution
    assert dres.width.get() == 192
    assert dres.height.get() == 108


def test_slice_will_set_the_pixel_aspect_to_1(prepare_scene, create_pymel):
    """testing if the slice() method will set the render pixel aspect to 1"""
    camera = prepare_scene
    pm = create_pymel
    dres = pm.PyNode("defaultResolution")
    dres.width.set(1920)
    dres.height.set(1080)
    dres.pixelAspect.set(2.5)

    rs = RenderSlicer(camera)
    rs.slice(10, 10)

    assert dres.pixelAspect.get() == 1
    assert dres.width.get() == 192
    assert dres.height.get() == 108


def test_unslice_will_set_the_pixel_aspect_to_1(prepare_scene, create_pymel):
    """testing if the unslice() method will set the pixel aspect to 1"""
    camera = prepare_scene
    pm = create_pymel
    dres = pm.PyNode("defaultResolution")
    dres.width.set(1920)
    dres.height.set(1080)
    dres.pixelAspect.set(2.5)

    rs = RenderSlicer(camera)
    rs.slice(10, 10)
    rs.unslice()

    assert dres.pixelAspect.get() == 1
    assert dres.width.get() == 1920
    assert dres.height.get() == 1080


def test_unslice_scene_will_set_the_pixel_aspect_to_1(prepare_scene, create_pymel):
    """testing if the unslice_scene() method will set the pixel aspect to 1"""
    camera = prepare_scene
    pm = create_pymel
    dres = pm.PyNode("defaultResolution")
    dres.width.set(1920)
    dres.height.set(1080)
    dres.pixelAspect.set(1.0)

    rs = RenderSlicer(camera)
    rs.slice(10, 10)
    rs.unslice_scene()

    assert dres.pixelAspect.get() == 1
    assert dres.width.get() == 1920
    assert dres.height.get() == 1080


def test_unslice_will_restore_original_render_resolution(prepare_scene, create_pymel):
    """unslice will restore the original render resolution"""
    camera = prepare_scene
    pm = create_pymel
    dres = pm.PyNode("defaultResolution")
    dres.width.set(960)
    dres.height.set(540)

    rs = RenderSlicer(camera=camera)
    rs.slice(10, 10)

    assert dres.width.get() == 96
    assert dres.height.get() == 54

    rs.unslice()
    assert dres.width.get() == 960
    assert dres.height.get() == 540


def test_unslice_will_set_the_is_sliced_attribute_of_the_camera_correctly(
    prepare_scene,
):
    """testing if unslice() method will set the isSliced attribute of the
    camera correctly
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    rs.slice(10, 10)

    assert camera.isSliced.get()

    rs.unslice()
    assert not camera.isSliced.get()


def test_unslice_will_set_the_is_sliced_attribute_correctly(prepare_scene):
    """testing if unslice() method will set the is_sliced attribute\
    correctly
    """
    camera = prepare_scene
    rs = RenderSlicer(camera=camera)
    rs.slice(10, 10)

    assert rs.is_sliced

    rs.unslice()
    assert not rs.is_sliced


def test_init_with_a_sliced_camera(prepare_scene, create_pymel):
    """testing if initializing with a pre-sliced camera will work properly"""
    camera = prepare_scene
    pm = create_pymel
    dres = pm.PyNode("defaultResolution")
    dres.width.set(1000)
    dres.height.set(1000)

    rs = RenderSlicer(camera=camera)
    rs.slice(10, 10)

    rs2 = RenderSlicer(camera=camera)
    assert rs2.is_sliced
    assert rs2.slices_in_x == 10
    assert rs2.slices_in_y == 10
    # assert rs2.original_resolution == 1000
