# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

import os
import tempfile

from pymel import core as pm


class General(object):
    """General tools
    """

    transform_info_temp_file_path = os.path.join(
        tempfile.gettempdir(),
        'transform_info'
    )

    @classmethod
    def unshape_parent_nodes(cls):
        """Moves the shape node of a mesh to another transform node as a
        children if the mesh node has other meshes under it. Essentially
        cleaning the scene.
        """
        mesh_nodes_with_transform_children = []
        all_meshes = pm.ls(dag=1, type='mesh')

        for node in all_meshes:
            parent = node.getParent()
            tra_under_shape = pm.ls(
                parent.listRelatives(),
                type='transform'
            )
            if len(tra_under_shape):
                mesh_nodes_with_transform_children.append(parent)

        for node in mesh_nodes_with_transform_children:
            # duplicate the node
            dup = pm.duplicate(node)[0]

            # remove all descendents
            all_descendents = dup.listRelatives(ad=1)
            # remove the shape from the list
            all_descendents.remove(dup.getShape())

            pm.delete(all_descendents)

            # parent under the original node
            pm.parent(dup, node)

            # remove the shape of the original node
            pm.delete(node.getShape())

    @classmethod
    def namespace_deleter(cls):
        """the legendary namespace deleter from Mehmet Erer

        finds and deletes unused namespaces
        """
        all_namespaces = pm.listNamespaces()
        ref_namespaces = [ref.namespace for ref in pm.listReferences()]
        missing_namespaces = []

        from anima.ui.progress_dialog import ProgressDialogManager
        if len(all_namespaces) > 0:
            pdm = ProgressDialogManager()
            pdm.close()

            caller = pdm.register(len(all_namespaces),
                                  'Locating Unused Namespaces...')
            for nsa in all_namespaces:
                i = 0
                for nsr in ref_namespaces:
                    i += 1
                    if nsr == nsa:
                        break
                    if i == len(ref_namespaces):
                        missing_namespaces.append(nsa)
                caller.step()

        if len(missing_namespaces) > 0:
            caller = pdm.register(len(missing_namespaces),
                                  'Deleting Unused Namespaces...')
            for ns in missing_namespaces:
                ns_info = pm.namespaceInfo(ns, lon=1, fn=1, r=1)
                if len(ns_info) > 0:
                    nsc = ns_info[len(ns_info) - 1]
                    nsc_array = nsc.split(':')
                    if len(nsc_array) > 0:
                        for del_nsc in nsc_array:
                            pm.namespace(rm=del_nsc, mnr=1)
                else:
                    pm.namespace(rm=ns, mnr=1)
                print ('Deleted -> :' + ns)
                caller.step()
        else:
            pm.warning(
                'There are no first-level unused namespaces in this scene.'
            )

        if len(ref_namespaces) == 0 and len(all_namespaces) > 0:
            for ns in all_namespaces:
                pm.namespace(rm=ns, mnr=1)
                print ('Deleted -> : %s' % ns)
            pm.warning(
                'There are no references in this scene. All empty namespaces '
                'are deleted.'
            )

    @classmethod
    def version_creator(cls):
        """version creator
        """
        from anima.ui.scripts import maya
        maya.version_creator()

    @classmethod
    def export_transform_info(cls, use_global_pos=False):
        """exports the transformation data in to a temp file
        """
        data = []
        for node in pm.ls(sl=1, type='transform'):

            if use_global_pos:
                # print('using global position')
                tra = pm.xform(node, q=1, ws=1, t=1)  # node.t.get()
                rot = pm.xform(node, q=1, ws=1, ro=1)  # node.r.get()
                sca = pm.xform(node, q=1, ws=1, s=1)  # node.s.get()
                pivr = pm.xform(node, q=1, ws=1, rp=1)
                pivs = pm.xform(node, q=1, ws=1, sp=1)

            else:
                # print('using local position')
                tra = node.t.get()
                rot = node.r.get()
                sca = node.s.get()
                pivr = node.rotatePivot.get()
                pivs = node.scalePivot.get()

            # print('tra: %0.3f %0.3f %0.3f' % (tra[0], tra[1], tra[2]))
            # print('rot: %0.3f %0.3f %0.3f' % (rot[0], rot[1], rot[2]))
            # print('sca: %0.3f %0.3f %0.3f' % (sca[0], sca[1], sca[2]))
            #
            # print('rotpiv: %0.3f %0.3f %0.3f' % (pivr[0], pivr[1], pivr[2]))
            # print('scapiv: %0.3f %0.3f %0.3f' % (pivs[0], pivs[1], pivs[2]))

            data.append('%s' % tra[0])
            data.append('%s' % tra[1])
            data.append('%s' % tra[2])

            data.append('%s' % rot[0])
            data.append('%s' % rot[1])
            data.append('%s' % rot[2])

            data.append('%s' % sca[0])
            data.append('%s' % sca[1])
            data.append('%s' % sca[2])

            data.append('%s' % pivr[0])
            data.append('%s' % pivr[1])
            data.append('%s' % pivr[2])

            data.append('%s' % pivs[0])
            data.append('%s' % pivs[1])
            data.append('%s' % pivs[2])

        with open(cls.transform_info_temp_file_path, 'w') as f:
            f.write('\n'.join(data))

    @classmethod
    def import_transform_info(cls, use_global_pos=False):
        """imports the transform info from the temp file
        """

        with open(cls.transform_info_temp_file_path) as f:
            data = f.readlines()

        for i, node in enumerate(pm.ls(sl=1, type='transform')):
            j = i * 15
            if use_global_pos:
                # print('using global position')

                # import pivots first
                # rotatePivot
                pm.xform(
                    node, ws=1,
                    rp=(float(data[j + 9]),
                       float(data[j + 10]),
                       float(data[j + 11]))
                )

                # scalePivot
                pm.xform(
                    node, ws=1,
                    sp=(float(data[j + 12]),
                       float(data[j + 13]),
                       float(data[j + 14]))
                )

                pm.xform(
                    node, ws=1,
                    t=(float(data[j]),
                       float(data[j + 1]),
                       float(data[j + 2]))
                )
                pm.xform(
                    node, ws=1,
                    ro=(float(data[j + 3]),
                        float(data[j + 4]),
                        float(data[j + 5]))
                )
                pm.xform(
                    node, ws=1,
                    s=(float(data[j + 6]),
                       float(data[j + 7]),
                       float(data[j + 8]))
                )

            else:
                print('using local position')

                # set pivots first
                # rotatePivot
                node.rotatePivot.set(
                    float(data[j + 9]), float(data[j + 10]), float(data[j + 11])
                )

                # scalePivot
                node.scalePivot.set(
                    float(data[j + 12]), float(data[j + 13]), float(data[j + 14])
                )

                try:
                    node.t.set(
                        float(data[j]), float(data[j + 1]), float(data[j + 2])
                    )
                except RuntimeError:
                    pass

                try:
                    node.r.set(
                        float(data[j + 3]), float(data[j + 4]), float(data[j + 5])
                    )
                except RuntimeError:
                    pass

                try:
                    node.s.set(
                        float(data[j + 6]), float(data[j + 7]), float(data[j + 8])
                    )
                except RuntimeError:
                    pass

            # print('tra: %0.3f %0.3f %0.3f' %
            #       (float(data[j]), float(data[j + 1]), float(data[j + 2])))
            # print('rot: %0.3f %0.3f %0.3f' %
            #       (float(data[j + 3]), float(data[j + 4]), float(data[j + 5])))
            # print('sca: %0.3f %0.3f %0.3f' %
            #       (float(data[j + 6]), float(data[j + 7]), float(data[j + 8])))
            # print('pivr: %0.3f %0.3f %0.3f' %
            #       (float(data[j + 9]), float(data[j + 10]), float(data[j + 11])))
            # print('pivs: %0.3f %0.3f %0.3f' %
            #       (float(data[j + 12]), float(data[j + 13]), float(data[j + 14])))

    @classmethod
    def export_component_transform_info(cls):
        """exports the transformation data in to a temp file
        """
        data = []
        for node in pm.ls(sl=1, fl=1):
            tra = pm.xform(node, q=1, ws=1, t=1)  # node.t.get()

            data.append('%s' % tra[0])
            data.append('%s' % tra[1])
            data.append('%s' % tra[2])

        with open(cls.transform_info_temp_file_path, 'w') as f:
            f.write('\n'.join(data))

    @classmethod
    def import_component_transform_info(cls):
        """imports the transform info from the temp file
        """
        with open(cls.transform_info_temp_file_path) as f:
            data = f.readlines()

        for i, node in enumerate(pm.ls(sl=1, fl=1)):
            j = i * 3
            pm.xform(node, ws=1, t=(float(data[j]), float(data[j + 1]), float(data[j + 2])))

    @classmethod
    def toggle_attributes(cls, attribute_name):
        """toggles the given attribute for the given list of objects
        """
        objs = pm.ls(sl=1)
        new_list = []

        attribute_count = 0
        set_to_state = 1

        for obj in objs:
            if obj.hasAttr(attribute_name):
                if obj.getAttr(attribute_name):
                    attribute_count += 1
                new_list.append(obj)

        obj_count = len(new_list)

        if attribute_count == obj_count:
            set_to_state = 0

        for obj in new_list:
            obj.setAttr(attribute_name, set_to_state)

    @classmethod
    def dereferencer(cls):
        """calls dereferencer
        """
        selection = pm.ls()
        for item in selection:
            if pm.attributeQuery('overrideEnabled', node=item, exists=True):
                if not item.overrideEnabled.get(l=True):
                    connections = pm.listConnections(item, d=True)
                    in_layer = 0
                    for i in range(0, len(connections)):
                        if connections[i].type() == "displayLayer":
                            in_layer = 1
                            break
                    if not in_layer:
                        if not item.overrideDisplayType.get(l=True):
                            item.overrideDisplayType.set(0)

    @classmethod
    def selection_manager(cls):
        from anima.env.mayaEnv import selection_manager
        selection_manager.UI()

    @classmethod
    def reference_selected_objects(cls):
        selection = pm.ls(sl=True)
        for item in selection:
            if item.overrideEnabled.get(se=True):
                item.overrideEnabled.set(1)
            if item.overrideDisplayType.get(se=True):
                item.overrideDisplayType.set(2)

        pm.select(cl=True)

    @classmethod
    def dereference_selected_objects(cls):
        selection = pm.ls(sl=True)
        for item in selection:
            if item.overrideEnabled.get(se=True):
                item.overrideEnabled.set(0)
            if item.overrideDisplayType.get(se=True):
                item.overrideDisplayType.set(0)

        pm.select(cl=True)

    @classmethod
    def remove_colon_from_names(cls):
        selection = pm.ls(sl=1)
        for item in selection:
            temp = item.split(':')[-1]
            pm.rename(item, temp)
            pm.ls(sl=1)

    @classmethod
    def remove_pasted(cls):
        """removes the string 'pasted__' from selected object names
        """
        rmv_str = "pasted__"
        [
            obj.rename(obj.name().split('|')[-1].replace(rmv_str, ''))
            for obj in pm.ls(sl=1)
            if rmv_str in obj.name()
        ]

    @classmethod
    def toggle_poly_meshes(cls):
        """toggles mesh selection in the current panel
        """
        panel_in_focus = pm.getPanel(wf=True)
        panel_type = pm.getPanel(typeOf=panel_in_focus)
        if panel_type == "modelPanel":
            poly_vis_state = pm.modelEditor(
                panel_in_focus,
                q=True,
                polymeshes=True
            )
            pm.modelEditor(
                panel_in_focus,
                e=True,
                polymeshes=(not poly_vis_state)
            )

    @classmethod
    def select_set_members(cls):
        selection = pm.ls(sl=1)
        if not selection:
            pass
        else:
            pm.select(selection[0].inputs())

    @classmethod
    def delete_unused_intermediate_shapes(cls):
        """clears unused intermediate shape nodes
        """
        ignored_node_types = [
            'nodeGraphEditorInfo',
            'shadingEngine',
        ]

        def filter_funct(x):
            return x.type() not in ignored_node_types

        unused_nodes = []
        for node in pm.ls(type=pm.nt.Mesh):
            if len(filter(filter_funct, node.inputs())) == 0 and \
               len(filter(filter_funct, node.outputs())) == 0 \
               and node.attr('intermediateObject').get():
                unused_nodes.append(node)
        pm.delete(unused_nodes)

    @classmethod
    def delete_all_sound(cls):
        pm.delete(pm.ls(type="audio"))

    @classmethod
    def generate_thumbnail(cls):
        """generates thumbnail for current scene
        """
        from anima.env.mayaEnv import auxiliary
        reload(auxiliary)
        result = auxiliary.generate_thumbnail()
        if result:
            pm.informBox('Done!', 'Thumbnail generated successfully!')
        else:
            pm.informBox('Fail!', 'Thumbnail generation was unsuccessful!')

    @classmethod
    def cleanup_light_cameras(cls):
        """Deletes all the light cameras in the current scene
        """
        cameras_to_delete = []
        for node in pm.ls(type=['light', 'RedshiftPhysicalLight']):
            parent = node.getParent()
            cameras = parent.listRelatives(ad=1, type='camera')
            if cameras:
                cameras_to_delete.extend(cameras)

        pm.delete(cameras_to_delete)

    @classmethod
    def rename_unique(cls):
        """renames the selected nodes with unique names
        """
        import re
        [node.rename(re.sub('[\d]+', '#', node.name()))
         for node in pm.selected()]

    @classmethod
    def rsproxy_data_importer(cls, path=''):
        """Imports RsProxy data from Houdini

        Required point attributes
            pos
            rot
            sca
        """
        from anima.env.mayaEnv import redshift

        if path == '':
            import os
            import tempfile
            path = os.path.join(
                tempfile.gettempdir(),
                'rsproxy_info.json'
            )

        data_man = redshift.RSProxyDataManager()
        data_man.load(path)
        data_man.create()