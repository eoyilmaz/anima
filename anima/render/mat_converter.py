# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Contains the base classes for material conversion for different environments
"""


class NodeCreatorBase(object):
    """Creates nodes according to the given specs
    """

    def __init__(self, specs=None):
        self.specs = specs

    def create(self):
        """override this method
        """
        raise NotImplementedError()


class ConversionManagerBase(object):
    """The base class for material conversion managers for different
    environments
    """

    def __init__(self):
        self.conversion_spec_sheet = None
        self.node_creator_factory = None

    def get_node_type(self, node):
        """Returns the node type for this environment

        :param node: A node familiar to the host environment
        :return:
        """
        raise NotImplementedError()

    def list_nodes(self, type_):
        """lists the node of given type

        :param type_: A type object or string that the environment need
        :return:
        """
        raise NotImplementedError()

    def rename_node(self, node, new_name):
        """Renames the node

        :param node:
        :param new_name:
        :return:
        """
        raise NotImplementedError()

    def get_node_name(self, node):
        """Returns the node name

        :param node:
        :return:
        """
        raise NotImplementedError()

    def get_node_inputs(self, node, attr=None):
        """returns the node inputs

        :param node:
        :param attr:
        :return:
        """
        raise NotImplementedError()

    def connect_attr(self, source_attr, target_node, target_attr):
        """creates a connection from source_attr to target_attr target_node

        :param source_attr:
        :param target_node:
        :param target_attr:
        :return:
        """
        raise NotImplementedError()

    def get_attr(self, node, attr):
        """gets node.attr

        :param node:
        :param attr:
        :return:
        """
        raise NotImplementedError()

    def set_attr(self, node, attr, value):
        """sets attr value

        :param node:
        :param attr:
        :param value:
        :return:
        """
        raise NotImplementedError()

    def auto_convert(self):
        """finds and converts all the nodes in the current scene
        """
        nodes_converted = []
        for node_type in self.conversion_spec_sheet:
            print('searching for: %s' % node_type)
            found_nodes = self.list_nodes(node_type)
            print('found: %s nodes' % len(found_nodes))
            for node in found_nodes:
                new_node = self.convert(node)
                nodes_converted.append([node, new_node])

        return nodes_converted

    def convert(self, node):
        """converts the given node to the other counterpart by looking at the
        self.conversion_spec_sheet.

        The conversion_spec_sheet is a dictionary in the following format:

        {
            "{SourceTypeName}": {
                "node_type": "{TargetTypeName}",
                "secondary_type": "shader",  # This is for Maya

                "call_after": None,
                    # a callable that accepts one or two arguments
                    # where the first argument holds the source node
                    # and the second holds the newly created target node

                "attributes": {
                    # this is a dictionary holding the attributes list

                    "source_attr1": "target_attr1"
                        # This directly sets the source value in the target
                        # node

                    "source_attr2": [
                        "target_attr2a",
                        "target_attr2b",
                    ],
                        # set multiple attributes at one in the target node

                    "source_attr3": {
                        "target_attr3": lambda x: x * 2,
                            # this uses a lambda function to calculate the
                            # target node attribute value
                    },

                    "source_attr4": {
                        "target_attr4a": lambda x, y: x and y
                            # you can use lambda function with two arguments
                            # the first one is the
                    },

                    "source_attr5": {
                        "target_attr6a": lambda x: x if x > 0 else 1 - x,
                        "target_attr6b": lambda x: x,
                            # it is possible to use more than one target
                            # attribute
                    },

                    "source_attr7": {
                        "target_attr_7": lambda x, y: x + y.getAttr("target_attr_8"),
                            # it is possible to use two source attribute
                            # to generate one target attribute value
                    },

                    "source_attr8": {
                        "target_attr_8": lambda x, y, z: x
                            # with three arguments
                            # x: source attribute value
                            # y: source_node
                            # z: target_node
                    }

                }
            }
        }

        """
        # get the conversion lut
        node_type = self.get_node_type(node)
        conversion_specs = self.conversion_spec_sheet.get(node_type)
        if not conversion_specs:
            print('No conversion_specs for: %s' % node_type)
            return

        # call any call_before
        call_before = conversion_specs.get('call_before')
        if call_before and callable(call_before):
            call_before(node)

        # some conversion specs doesn't require a new node to be created
        # so return early if this is the case
        if 'node_type' not in conversion_specs:
            return node

        node_creator = self.node_creator_factory(conversion_specs)
        rs_node = node_creator.create()

        # rename the material to have a similar name with the original
        if rs_node is not None:
            node_type_name = conversion_specs['node_type'] \
                if isinstance(conversion_specs['node_type'], str) else \
                conversion_specs['secondary_type'].replace(' ', '_')

            self.rename_node(
                rs_node,
                self.get_node_name(node).replace(
                    node_type, node_type_name
                )
            )
        else:
            rs_node = node

        # set attributes
        attributes = conversion_specs.get('attributes')
        if attributes:
            for source_attr, target_attr in attributes.items():
                # value can be a string
                if isinstance(target_attr, basestring):
                    # check incoming connections
                    incoming_connections = \
                        self.get_node_inputs(node, source_attr)
                    if incoming_connections:
                        # connect any textures to the target node
                        for input_ in incoming_connections:
                            # input_ >> rs_node.attr(target_attr)
                            self.connect_attr(
                                input_,
                                rs_node,
                                target_attr
                            )
                    else:
                        # just read and set the value directly
                        self.set_attr(
                            rs_node,
                            target_attr,
                            self.get_attr(node, source_attr)
                        )

                elif isinstance(target_attr, list):
                    # or a list
                    # where we set multiple attributes in the rs_node to the
                    # same value
                    # source_attr_value = node.getAttr(source_attr)
                    source_attr_value = self.get_attr(node, source_attr)
                    for attr in target_attr:
                        self.set_attr(rs_node, attr, source_attr_value)
                        # for input_ in node.attr(source_attr).inputs(p=1):
                        for input_ in self.get_node_inputs(node, source_attr):
                            self.connect_attr(input_, rs_node, attr)
                elif isinstance(target_attr, dict):
                    # or another dictionary
                    # where we have a converter
                    source_attr_value = self.get_attr(node, source_attr)
                    for attr, converter in target_attr.items():
                        if callable(converter):
                            try:
                                attr_value = converter(source_attr_value)
                            except TypeError:
                                # it should use two parameters, also include
                                # the node itself
                                try:
                                    attr_value = converter(
                                        source_attr_value,
                                        node
                                    )
                                except TypeError:
                                    # so this is the third form that also
                                    # includes the rs node
                                    attr_value = converter(
                                        source_attr_value,
                                        node,
                                        rs_node
                                    )
                        else:
                            attr_value = converter
                        self.set_attr(rs_node, attr, attr_value)

        # call any call_after
        call_after = conversion_specs.get('call_after')
        if call_after and callable(call_after):
            call_after(node, rs_node)

        return rs_node
