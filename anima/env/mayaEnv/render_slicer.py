# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pymel.core as pm


class RenderSlicer(object):
    """A tool to help slice single frame renders in to many little parts which
    will help it to be rendered in small parts in a render farm.
    """

    def __init__(self, camera=None, slices_in_x=5, slices_in_y=5):
        self._camera = None
        self._slices_in_x = None
        self._slices_in_y = None
        self._is_sliced = False
        self._original_resolution = [None, None]

        # call the properties to initialize values
        self.camera = camera
        self.slices_in_x = slices_in_x
        self.slices_in_y = slices_in_y
        self.is_sliced = False
        self.original_resolution = [None, None]

    @property
    def slices_in_x(self):
        """getter for _slices_in_x attribute
        """
        return self._slices_in_x

    @slices_in_x.setter
    def slices_in_x(self, slices_in_x):
        """setter for _slices_in_x attribute
        """
        self._slices_in_x = self._validate_slices_in_x(slices_in_x)

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
        return self._slices_in_y

    @slices_in_y.setter
    def slices_in_y(self, slices_in_y):
        """setter for _slices_in_y attribute
        """
        self._slices_in_y = self._validate_slices_in_y(slices_in_y)

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
        self._camera = self._validate_camera(camera)

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

    def _create_data_attributes(self):
        """creates slicer data attributes inside the camera
        """
        # store the original resolution
        # slices in x
        # slices in y

        # is_sliced
        # non_sliced_resolution_x
        # non_sliced_resolution_y
        # slices_in_x
        # slices_in_y

        if not self.camera.hasAttr('isSliced'):
            self.camera.addAttr('isSliced', at='bool')

        if not self.camera.hasAttr('nonSlicedResolutionX'):
            self.camera.addAttr('nonSlicedResolutionX', at='short')

        if not self.camera.hasAttr('nonSlicedResolutionY'):
            self.camera.addAttr('nonSlicedResolutionY', at='short')

        if not self.camera.hasAttr('slicesInX'):
            self.camera.addAttr('slicesInX', at='short')

        if not self.camera.hasAttr('slicesInY'):
            self.camera.addAttr('slicesInY', at='short')

    def _store_data(self):
        """stores slicer data inside the camera
        """
        self._create_data_attributes()
        self.camera.isSliced.set(self.is_sliced)

        # get the current render resolution
        dres = pm.PyNode("defaultResolution")
        width = dres.width.get()
        height = dres.height.get()

        self.camera.nonSlicedResolutionX.set(width)
        self.camera.nonSlicedResolutionY.set(height)
        self.camera.slicesInX.set(self.slices_in_x)
        self.camera.slicesInY.set(self.slices_in_y)

    def _unslice(self):
        """resets the camera to original non-sliced state
        """
        raise NotImplementedError()

    def do_slice(self):
        """slices all renderable cameras
        """
        if self.camera.hasAttr('isSliced'):
            if self.camera.isSliced.get():
                # un-slice the camera first
                self._unslice()

        self.is_sliced = True

        self._store_data()

        sx = self.slices_in_x
        sy = self.slices_in_y

        # set render resolution
        d_res = pm.PyNode("defaultResolution")
        h_res = d_res.width.get()
        v_res = d_res.height.get()
        self.original_resolution = [h_res, v_res]

        d_res.width.set(h_res / float(sx))
        d_res.height.set(v_res / float(sy))

        # use h_aperture to calculate v_aperture
        h_aperture = self.camera.getAttr('horizontalFilmAperture')

        # recalculate the other aperture
        self.camera.setAttr('verticalFilmAperture', h_aperture * v_res / h_res)

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

    def ui(self):
        """The UI for the slicer
        """
        pass
