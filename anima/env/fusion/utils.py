# -*- coding: utf-8 -*-


class NodeUtils(object):
    """Node related utils for Fusion
    """

    @classmethod
    def list_input_ids(cls, node):
        """List input ids of the given node
        :param node:
        :return:
        """
        node_input_list = node.GetInputList()
        for input_entry_key in node_input_list.keys():
            input_entry = node_input_list[input_entry_key]
            input_id = input_entry.GetAttrs()['INPS_ID']
            print("%s: %s" % (input_entry_key, input_id))

    @classmethod
    def set_node_attr(cls, node, attr, value):
        """sets node attr, sadly we need that

        :param node:
        :param attr:
        :param value:
        :return:
        """
        node_input_list = node.GetInputList()
        for input_entry_key in node_input_list.keys():
            input_entry = node_input_list[input_entry_key]
            input_id = input_entry.GetAttrs()['INPS_ID']
            if input_id == attr:
                input_entry[0] = value
                break
