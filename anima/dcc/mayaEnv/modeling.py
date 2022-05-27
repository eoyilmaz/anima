# -*- coding: utf-8 -*-

from anima.dcc.mayaEnv import auxiliary
from pymel import core as pm


class Modeling(object):
    """Modeling tools"""

    @classmethod
    def smooth_edges(cls, iteration=1):
        """Smooths the selected edge loops"""
        orig_selection = pm.selected()

        vtxs = pm.ls(pm.polyListComponentConversion(toVertex=1), fl=1)
        ordered_vtxs = []
        bucket = []

        # find a start vertex that have only one neighbour in the vtxs list
        shape = vtxs[0].node()

        for vtx in vtxs:
            in_list = 0
            indeces = vtx.connectedVertices().indices()
            for cvtx_index in indeces:
                cvtx = pm.PyNode("%s.vtx[%s]" % (shape.name(), cvtx_index))
                if cvtx in vtxs:
                    in_list += 1
            if in_list == 1:
                ordered_vtxs.append(vtx)
                bucket.append(vtx)
                vtxs.remove(vtx)
                break

        # iterate over the bucket
        i = 0
        while bucket and i < 100:
            current_vtx = bucket.pop()

            cvtx_indeces = current_vtx.connectedVertices().indices()
            for cvtx_index in cvtx_indeces:
                cvtx = pm.PyNode("%s.vtx[%s]" % (shape.name(), cvtx_index))
                if cvtx in vtxs:
                    vtxs.remove(cvtx)
                    bucket.append(cvtx)
                    ordered_vtxs.append(cvtx)
                    break
            i += 1

        # get the vertex positions
        ordered_vtx_positions = [
            pm.dt.Vector(pm.xform(vtx, q=1, ws=1, t=1)) for vtx in ordered_vtxs
        ]

        # smooth the positions
        from anima import utils

        ordered_vtx_positions = utils.smooth_array(ordered_vtx_positions, iteration)

        # set it back
        map(lambda x, y: pm.xform(y, ws=1, t=x), ordered_vtx_positions, ordered_vtxs)

        # reselect original selection
        pm.select(orig_selection)

    @classmethod
    def transfer_uvs(cls, sample_space=4):
        """transfer uvs between selected objects. It can search for
        hierarchies both in source and target sides.

        :parm sample_space: The sampling space:

          0: World
          1: Local
          2: UV
          3: Component
          4: Topology
        """
        selection = pm.ls(sl=1)
        pm.select(None)
        source = selection[0]
        target = selection[1]
        # auxiliary.transfer_shaders(source, target)
        # pm.select(selection)

        lut = auxiliary.match_hierarchy(source, target)

        for source, target in lut["match"]:
            pm.transferAttributes(
                source,
                target,
                transferPositions=0,
                transferNormals=0,
                transferUVs=2,
                transferColors=2,
                sampleSpace=sample_space,
                sourceUvSpace="map1",
                targetUvSpace="map1",
                searchMethod=0,
                flipUVs=0,
                colorBorders=1,
            )
        # restore selection
        pm.select(selection)

    @classmethod
    def create_auto_uvmap(cls):
        """creates automatic uv maps for the selected objects and layouts the
        uvs. Fixes model problems along the way.
        """
        selection_list = pm.selected()
        for node in selection_list:
            pm.polyAutoProjection(
                node, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0
            )

            pm.select(node)
            f = Modeling.select_zero_uv_area_faces()

            if f:
                print("DELETED Faces!")
                pm.delete(f)

            pm.select(node)
            try:
                pm.u3dLayout(
                    node, res=256, scl=3, spc=0.0078125, mar=0.0078125, box=(0, 1, 0, 1)
                )
            except RuntimeError as e:
                if "non-manifold UVs" in str(
                    e
                ) or "Mesh has unconnected vertices" in str(e):
                    pm.mel.eval('Unfold3DFixNonManifold({"nonManifoldUV"})')
                pm.u3dLayout(
                    node, res=256, scl=3, spc=0.0078125, mar=0.0078125, box=(0, 1, 0, 1)
                )

            pm.select(node)
            pm.mel.eval("DeleteHistory;")

        pm.select(selection_list)

    @classmethod
    def fix_uvsets(cls):
        """Fixes uvSets (DiffuseUV -> map1)"""
        for node in pm.selected():
            shape = node.getShape()

            # get current uvset
            uvset_names = pm.polyUVSet(shape, query=True, allUVSets=True)

            if "DiffuseUV" in uvset_names:
                if len(uvset_names) == 1:
                    # Copy values of uvset "DiffuseUV" to "map1"
                    pm.polyUVSet(shape, copy=True, nuv="map1", uvSet="DiffuseUV")

                    # set current uvset to map1
                    pm.polyUVSet(shape, currentUVSet=True, uvSet="map1")

                    # delete uv set
                    # pm.polyUVSet( shape, delete=True, uvSet='DiffuseUV')
                else:
                    if "map1" in uvset_names:
                        # set current uvset to map1
                        uvs = shape.getUVs(uvSet="map1")

                        if len(uvs[0]) == 0:
                            # Copy values of uvset "DiffuseUV" to "map1"
                            pm.polyUVSet(
                                shape, copy=True, nuv="map1", uvSet="DiffuseUV"
                            )

    @classmethod
    def reverse_normals(cls):
        selection = pm.ls(sl=1)
        for item in selection:
            pm.polyNormal(item, normalMode=0, userNormalMode=0, ch=1)
        pm.delete(ch=1)
        pm.select(selection)

    @classmethod
    def fix_normals(cls):
        selection = pm.ls(sl=1)
        pm.polySetToFaceNormal()
        for item in selection:
            pm.polyNormal(item, normalMode=2, userNormalMode=0, ch=1)
            pm.polySoftEdge(item, a=30, ch=1)
        pm.delete(ch=1)
        pm.select(selection)

    @classmethod
    def polySmoothFace(cls, method):
        selection = pm.ls(sl=1)
        for item in selection:
            pm.polySmooth(
                item,
                mth=method,
                dv=1,
                c=1,
                kb=0,
                ksb=0,
                khe=0,
                kt=1,
                kmb=0,
                suv=1,
                peh=0,
                sl=1,
                dpe=1,
                ps=0.1,
                ro=1,
                ch=1,
            )
        pm.select(selection)

    @classmethod
    def activate_deActivate_smooth(cls, nodeState):
        selection = pm.ls(type="polySmoothFace")
        for item in selection:
            item.nodeState.set(nodeState)

    @classmethod
    def delete_smooth(cls):
        Modeling.activate_deActivate_smooth(0)
        selection = pm.ls(type="polySmoothFace")
        if len(selection) > 0:
            pm.delete(selection)

    @classmethod
    def delete_smooth_on_selected(cls):
        selection = pm.ls(sl=1)
        deleteList = []
        for item in selection:
            hist = pm.listHistory(item)
            for i in range(0, len(hist)):
                if hist[i].type() == "polySmoothFace":
                    deleteList.append(hist[i])
        pm.delete(deleteList)

    @classmethod
    def hierarchy_instancer(cls):
        from anima.dcc.mayaEnv import hierarchy_instancer

        new_nodes = []

        instancer = hierarchy_instancer.HierarchyInstancer()
        for node in pm.ls(sl=1):
            new_nodes.append(instancer.instance(node))

        pm.select(new_nodes)

    @classmethod
    def relax_vertices(cls):
        from anima.dcc.mayaEnv import relax_vertices

        relax_vertices.relax()

    @classmethod
    def create_curve_from_mesh_edges(cls):
        """creates 3rd degree curves from the selected mesh edges"""

        def order_edges(edge_list):
            """orders the given edge list according to their connectivity"""
            edge_list = pm.ls(edge_list, fl=1)

            # find a starting edge
            starting_edge = None
            for e in edge_list:
                connected_edges = pm.ls(e.connectedEdges(), fl=1)
                number_of_connected_edges_in_selection = 0
                for e2 in connected_edges:
                    if e2 in edge_list:
                        number_of_connected_edges_in_selection += 1

                if number_of_connected_edges_in_selection == 1:
                    starting_edge = e
                    break

            if starting_edge is None:
                starting_edge = edge_list[0]

            current_edge = starting_edge
            ordered_edges = [current_edge]
            edge_list.remove(current_edge)

            i = 0
            while current_edge and len(edge_list) and i < 1000:
                i += 1
                # go over neighbours that are in the selection list
                next_edge = None
                connected_edges = pm.ls(current_edge.connectedEdges(), fl=1)
                for e in connected_edges:
                    if e in edge_list:
                        next_edge = e
                        break

                if next_edge:
                    edge_list.remove(next_edge)
                    current_edge = next_edge
                    ordered_edges.append(current_edge)

            return ordered_edges

        def order_vertices(ordered_edges):
            """orders the vertices of the given ordered edge list"""
            # now get an ordered list of vertices
            ordered_vertices = []

            for i, e in enumerate(ordered_edges[0:-1]):
                v0, v1 = pm.ls(e.connectedVertices(), fl=1)

                # get the connected edges of v0
                if ordered_edges[i + 1] not in pm.ls(v0.connectedEdges(), fl=1):
                    # v0 is the first vertex
                    ordered_vertices.append(v0)
                else:
                    # v0 is the second vertex
                    ordered_vertices.append(v1)

            # append the vertex of the last edge which is not in the list
            v0, v1 = pm.ls(ordered_edges[-1].connectedVertices(), fl=1)
            # get the connected edges of v0
            if ordered_edges[-2] not in pm.ls(v0.connectedEdges(), fl=1):
                # v0 is the last vertex
                ordered_vertices.append(v1)
                ordered_vertices.append(v0)
            else:
                # v1 is the last vertex
                ordered_vertices.append(v0)
                ordered_vertices.append(v1)

            return ordered_vertices

        selection = pm.ls(sl=1)
        ordered_edges = order_edges(selection)
        ordered_vertices = order_vertices(ordered_edges)

        # now create a curve from the given vertices
        pm.curve(
            p=list(map(lambda x: x.getPosition(space="world"), ordered_vertices)), d=3
        )

    @classmethod
    def vertex_aligned_locator(cls):
        """creates vertex aligned locator, select 3 vertices"""
        selection = pm.ls(os=1, fl=1)

        # get the axises
        p0 = selection[0].getPosition(space="world")
        p1 = selection[1].getPosition(space="world")
        p2 = selection[2].getPosition(space="world")

        v1 = p0 - p1
        v2 = p2 - p1
        # v3 = p0 - p2

        v1.normalize()
        v2.normalize()

        dcm = pm.createNode("decomposeMatrix")

        x = v1
        z = v2
        y = z ^ x
        y.normalize()

        dcm.inputMatrix.set(
            [x[0], x[1], x[2], 0, y[0], y[1], y[2], 0, z[0], z[1], z[2], 0, 0, 0, 0, 1],
            type="matrix",
        )

        loc = pm.spaceLocator()

        loc.t.set(p1)
        loc.r.set(dcm.outputRotate.get())

        pm.delete(dcm)

    @classmethod
    def select_zero_uv_area_faces(cls):
        """selects faces with zero UV area"""

        def area(p):
            return 0.5 * abs(
                sum(x0 * y1 - x1 * y0 for ((x0, y0), (x1, y1)) in segments(p))
            )

        def segments(p):
            return zip(p, p[1:] + [p[0]])

        all_meshes = pm.ls([node.getShape() for node in pm.ls(sl=1)], type="mesh")

        mesh_count = len(all_meshes)

        from anima.utils.progress import ProgressManager

        pdm = ProgressManager()

        if pm.general.about(batch=1) or not mesh_count:
            from anima.utils.progress import ProgressDialogBase
            pdm.dialog_class = ProgressDialogBase
            pdm.create_dialog()

        caller = pdm.register(mesh_count, "check_uvs()")

        faces_with_zero_uv_area = []
        for node in all_meshes:
            all_uvs = node.getUVs()
            for i in range(node.numFaces()):
                uvs = []
                try:
                    for j in range(node.numPolygonVertices(i)):
                        # uvs.append(node.getPolygonUV(i, j))
                        uv_id = node.getPolygonUVid(i, j)
                        uvs.append((all_uvs[0][uv_id], all_uvs[1][uv_id]))
                    if area(uvs) == 0.0:
                        # meshes_with_zero_uv_area.append(node)
                        # break
                        faces_with_zero_uv_area.append(
                            "%s.f[%s]" % (node.fullPath(), i)
                        )
                except RuntimeError:
                    faces_with_zero_uv_area.append("%s.f[%s]" % (node.fullPath(), i))

            caller.step()

        if len(faces_with_zero_uv_area) == 0:
            pm.warning("No Zero UV area polys found!!!")
            return []
        else:
            pm.select(faces_with_zero_uv_area)
            return faces_with_zero_uv_area

    @classmethod
    def set_pivot(cls, axis=0):
        """moves the object pivot to desired axis

        There are 7 options to move the pivot point to:
            c, -x, +x, -y, +y, -z, +z
            0,  1,  2,  3,  4,  5,  6

        :param int axis: One of [0-6] showing the desired axis to get the
          pivot point to
        """
        from maya.OpenMaya import MBoundingBox, MPoint

        if not 0 <= axis <= 6:
            return

        for node in pm.ls(sl=1):
            # check if the node has children
            children = pm.ls(sl=1)[0].getChildren(ad=1, type="transform")
            # get the bounding box points
            # bbox = node.boundingBox()
            bbox = pm.xform(node, q=1, ws=1, boundingBox=1)
            bbox = MBoundingBox(
                MPoint(bbox[0], bbox[1], bbox[2]), MPoint(bbox[3], bbox[4], bbox[5])
            )

            if len(children):
                # get all the bounding boxes
                for child in children:
                    if child.getShape() is not None:
                        # child_bbox = child.boundingBox()
                        child_bbox = pm.xform(child, q=1, ws=1, boundingBox=1)
                        child_bbox = MBoundingBox(
                            MPoint(child_bbox[0], child_bbox[1], child_bbox[2]),
                            MPoint(child_bbox[3], child_bbox[4], child_bbox[5]),
                        )
                        bbox.expand(child_bbox.min())
                        bbox.expand(child_bbox.max())

            piv = bbox.center()
            if axis == 1:
                # -x
                piv.x = bbox.min().x
            elif axis == 2:
                # +x
                piv.x = bbox.max().x
            elif axis == 3:
                # -y
                piv.y = bbox.min().y
            elif axis == 4:
                # +y
                piv.y = bbox.max().y
            elif axis == 5:
                # -z
                piv.z = bbox.min().z
            elif axis == 6:
                # +z
                piv.z = bbox.max().z

            pm.xform(node, ws=1, rp=piv)
            pm.xform(node, ws=1, sp=piv)

    @classmethod
    def set_texture_res(cls, res):
        """sets the texture resolution
        :param res:
        :return:
        """
        selection_list = pm.ls(sl=1)

        if not len(selection_list):
            return

        node = selection_list[0]

        # if the selection is a material
        try:
            node.resolution.set(res)
        except AttributeError:
            # not a material
            # try it as a DAG object
            try:
                shape = node.getShape()
            except RuntimeError:
                # not a DAG object with shape
                return

            shading_engines = shape.outputs(type="shadingEngine")
            if not len(shading_engines):
                # not an object either
                # so what the fuck are you amk
                return

            # consider the first material
            conn = shading_engines[0].surfaceShader.listConnections()

            if len(conn):
                material = conn[0]
                # now we can set the resolution
                material.resolution.set(res)

    @classmethod
    def bbox_from_selection(cls):
        """creates the bbox of the selected objects as a real polyCube"""
        bbox = pm.dt.BoundingBox()
        for node in pm.selected():
            bbox2 = node.boundingBox()
            bbox.expand(bbox2.min())
            bbox.expand(bbox2.max())
        cube_transform, cube_shape = pm.polyCube(
            width=bbox.width(),
            height=bbox.height(),
            depth=bbox.depth(),
        )
        cube_transform.t.set(bbox.center())
