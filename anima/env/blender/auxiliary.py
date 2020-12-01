# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

import bpy


class Render:
    """utils for shading and render context
    """

    @classmethod
    def get_selected_shading_nodes(cls):
        """returns the selected shading nodes in the shading node tree
        """
        selected_nodes = []
        for mat in bpy.data.materials:
            if mat.node_tree:
                for node in mat.node_tree.nodes:
                    if node.select:
                        selected_nodes.append(node)

        return selected_nodes

    @classmethod
    def set_selected_image_texture_nodes_color_space(cls, space):
        """sets the selected image texture node to color space

        :param str space: A valid Color space name
        :return:
        """
        nodes = cls.get_selected_shading_nodes()
        for node in nodes:
            cls.set_image_texture_node_color_space(node, space)

    @classmethod
    def set_selected_image_texture_nodes_to_srgb(cls):
        """sets the selected image texture node to sRGB
        """
        nodes = cls.get_selected_shading_nodes()
        for node in nodes:
            cls.set_to_srgb(node)

    @classmethod
    def set_selected_image_texture_nodes_to_raw(cls):
        """sets the selected image texture node to RAW
        """
        nodes = cls.get_selected_shading_nodes()
        for node in nodes:
            cls.set_to_raw(node)

    @classmethod
    def set_to_srgb(cls, node):
        """sets the given image texture node to sRGB
        """
        cls.set_image_texture_node_color_space(node, 'Utility - sRGB - Texture')

    @classmethod
    def set_to_raw(cls, node):
        """sets the given image texture node to sRGB
        """
        cls.set_image_texture_node_color_space(node, 'raw')

    @classmethod
    def set_image_texture_node_color_space(cls, node, space):
        """sets the given image texture node to the given node

        :param node:
        :param str space: A valid Color space name
        :return:
        """
        try:
            node.image.colorspace_settings.name = space
        except AttributeError:
            # this is not a Image Texture node
            pass
