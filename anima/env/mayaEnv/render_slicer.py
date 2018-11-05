# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pymel.core as pm


class RenderSlicer(object):
    """A tool to help slice single frame renders in to many little parts which
    will help it to be rendered in small parts in a render farm.
    """

    def __init__(self, camera=None):
        self._camera = None
        self.camera = camera

    @property
    def slices_in_x(self):
        """getter for _slices_in_x attribute
        """
        return self.camera.slicesInX.get()

    @slices_in_x.setter
    def slices_in_x(self, slices_in_x):
        """setter for _slices_in_x attribute
        """
        self.camera.slicesInX.set(self._validate_slices_in_x(slices_in_x))

    @classmethod
    def _validate_slices_in_x(cls, slices_in_x):
        """validates the slices_in_x value
        """
        if not isinstance(slices_in_x, int):
            raise TypeError(
                "%s.slices_in_x should be a non-zero positive integer, not %s"
                % (cls.__name__, slices_in_x.__class__.__name__)
            )

        if slices_in_x <= 0:
            raise ValueError(
                "%s.slices_in_x should be a non-zero positive integer" %
                cls.__name__
            )

        return slices_in_x

    @property
    def slices_in_y(self):
        """getter for _slices_in_y attribute
        """
        return self.camera.slicesInY.get()

    @slices_in_y.setter
    def slices_in_y(self, slices_in_y):
        """setter for _slices_in_y attribute
        """
        self.camera.slicesInY.set(self._validate_slices_in_y(slices_in_y))

    @classmethod
    def _validate_slices_in_y(cls, slices_in_y):
        """validates the slices_in_y value
        """
        if not isinstance(slices_in_y, int):
            raise TypeError(
                "%s.slices_in_y should be a non-zero positive integer, not %s"
                % (cls.__name__, slices_in_y.__class__.__name__)
            )

        if slices_in_y <= 0:
            raise ValueError(
                "%s.slices_in_y should be a non-zero positive integer" %
                cls.__name__
            )

        return slices_in_y

    @property
    def camera(self):
        """getter for the _camera attribute
        """
        return self._camera

    @camera.setter
    def camera(self, camera):
        """setter for the _camera attribute

        :param camera: A Maya camera
        :return: None
        """
        camera = self._validate_camera(camera)
        self._create_data_attributes(camera)
        self._camera = camera

    @classmethod
    def _validate_camera(cls, camera):
        """validates the given camera
        """
        if camera is None:
            raise TypeError("Please supply a Maya camera")

        if not isinstance(camera, pm.nt.Camera):
            raise TypeError(
                "%s.camera should be a Maya camera, not %s" % (
                    cls.__name__,
                    camera.__class__.__name__
                )
            )

        return camera

    @classmethod
    def _create_data_attributes(cls, camera):
        """creates slicer data attributes inside the camera

        :param pm.nt.Camera camera: A maya camera
        """
        # store the original resolution
        # slices in x
        # slices in y

        # is_sliced
        # non_sliced_resolution_x
        # non_sliced_resolution_y
        # slices_in_x
        # slices_in_y

        if not camera.hasAttr('isSliced'):
            camera.addAttr('isSliced', at='bool')

        if not camera.hasAttr('nonSlicedResolutionX'):
            camera.addAttr('nonSlicedResolutionX', at='short')

        if not camera.hasAttr('nonSlicedResolutionY'):
            camera.addAttr('nonSlicedResolutionY', at='short')

        if not camera.hasAttr('slicesInX'):
            camera.addAttr('slicesInX', at='short')

        if not camera.hasAttr('slicesInY'):
            camera.addAttr('slicesInY', at='short')

    def _store_data(self):
        """stores slicer data inside the camera
        """
        self._create_data_attributes(self.camera)
        self.camera.isSliced.set(self.is_sliced)

        # get the current render resolution
        dres = pm.PyNode("defaultResolution")
        width = dres.width.get()
        height = dres.height.get()

        self.camera.nonSlicedResolutionX.set(width)
        self.camera.nonSlicedResolutionY.set(height)
        self.camera.slicesInX.set(self.slices_in_x)
        self.camera.slicesInY.set(self.slices_in_y)

    @property
    def is_sliced(self):
        """A shortcut for the camera.isSliced attribute
        """
        if self.camera.hasAttr('isSliced'):
            return self.camera.isSliced.get()
        return False

    @is_sliced.setter
    def is_sliced(self, is_sliced):
        """A shortcut for the camera.isSliced attribute
        """
        if not self.camera.hasAttr('isSliced'):
            self._create_data_attributes(self.camera)

        self.camera.isSliced.set(is_sliced)

    def unslice(self):
        """resets the camera to original non-sliced state
        """
        # unslice the camera
        dres = pm.PyNode('defaultResolution')

        # set the resolution to original
        dres.width.set(self.camera.getAttr('nonSlicedResolutionX'))
        dres.height.set(self.camera.getAttr('nonSlicedResolutionY'))
        dres.pixelAspect.set(1)

        self.camera.isSliced.set(False)

    def unslice_scene(self):
        """scans the scene cameras and unslice the scene
        """
        dres = pm.PyNode('defaultResolution')
        dres.aspectLock.set(0)

        # TODO: check multi sliced camera
        for cam in pm.ls(type=pm.nt.Camera):
            if cam.hasAttr('isSliced') and cam.isSliced.get():
                dres.width.set(cam.nonSlicedResolutionX.get())
                dres.height.set(cam.nonSlicedResolutionY.get())
                dres.pixelAspect.set(1)
                cam.isSliced.set(False)

    def slice(self, slices_in_x, slices_in_y):
        """slices all renderable cameras
        """
        # set render resolution
        self.unslice_scene()
        self.is_sliced = True
        self._store_data()

        sx = self.slices_in_x = slices_in_x
        sy = self.slices_in_y = slices_in_y

        # set render resolution
        d_res = pm.PyNode("defaultResolution")
        h_res = d_res.width.get()
        v_res = d_res.height.get()

        # this system only works when the
        d_res.aspectLock.set(0)
        d_res.pixelAspect.set(1)
        d_res.width.set(h_res / float(sx))
        d_res.pixelAspect.set(1)
        d_res.height.set(v_res / float(sy))
        d_res.pixelAspect.set(1)

        # use h_aperture to calculate v_aperture
        h_aperture = self.camera.getAttr('horizontalFilmAperture')

        # recalculate the other aperture
        v_aperture = h_aperture * v_res / h_res
        self.camera.setAttr('verticalFilmAperture', v_aperture)

        v_aperture = self.camera.getAttr('verticalFilmAperture')

        self.camera.setAttr('zoom', 1.0/float(sx))

        t = 0
        for i in range(sy):
            v_pan = v_aperture / (2.0 * sy) * (1 + 2 * i - sy)
            for j in range(sx):
                h_pan = h_aperture / (2.0 * sx) * (1 + 2 * j - sx)
                pm.currentTime(t)
                pm.setKeyframe(self.camera, at='horizontalPan', v=h_pan)
                pm.setKeyframe(self.camera, at='verticalPan', v=v_pan)
                t += 1

        self.camera.panZoomEnabled.set(1)
        self.camera.renderPanZoom.set(1)

        d_res.pixelAspect.set(1)

    def ui(self):
        """The UI for the slicer
        """
        pass
