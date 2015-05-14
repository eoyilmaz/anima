# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from pymel.core.nodetypes import RenderLayer


class aiRenderLayer(RenderLayer):
    """Overridden RenderLayer class, helps managing Arnold attributes
    """

    __layer_types__ = ['Diffuse', 'Glossy']


class RenderLayerManager(object):
    """Manages render layers
    """

    def split_current_layer(self, layer_types=[]):
        """Splits the current layer in to types of layers specified with
        layer_types argument.

        :param list layer_types: list of strings specifying the resultant layer
          types

        :return:
        """

    def from_selected(self, layer_type='Diffuse'):
        """Creates render layers from selected objects.

        :param layer_type: 
        :return:
        """


