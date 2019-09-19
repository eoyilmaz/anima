from anima.env.mayaEnv.camera_tools import cam_to_chan
from pymel import core as pm


class Animation(object):
    """animation tools
    """

    @classmethod
    def equalize_node_speed(cls):
        """Equalizes the node animation to keep the speed constant
        """
        #
        # This only works for position
        #
        # To make it also work with Rotation you need to do some nasty stuff,
        # like creating the camera transformation frame with two locators, one
        # showing the up or the local y-axis and other showing the z-axis of
        # the camera, trace them with a curve, smooth them as you did with the
        # position, then read them back create local y and z axis and set the
        # euler rotations.
        #
        # For now I don't need it. So I'll code it later on.
        #
        start_frame = int(pm.playbackOptions(q=1, min=1))
        end_frame = int(pm.playbackOptions(q=1, max=1))

        selected_node = pm.selected()[0]

        # duplicate the input graph
        node = pm.duplicate(selected_node, un=1, rr=1)[0]
        node.rename("%s_Equalized#" % selected_node.name())

        # create speed attribute
        if not node.hasAttr("speed"):
            node.addAttr("speed", at="double")
        pm.currentTime(start_frame)
        pm.setKeyframe(node.speed)

        prev_pos = node.t.get()

        pos_data = []
        rot_data = []

        for i in range(start_frame, end_frame + 1):
            pm.currentTime(i)
            current_pos = node.t.get()
            pos_data.append(current_pos)
            rot_data.append(node.r.get())
            speed = (current_pos - prev_pos).length()
            prev_pos = current_pos
            node.speed.set(speed)
            pm.setKeyframe(node.speed)

        camera_path = pm.curve(d=3, p=pos_data)
        camera_path_curve = camera_path.getShape()

        pm.rebuildCurve(
            camera_path_curve,
            ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0,
            s=end_frame - start_frame + 1, d=3, tol=0.01
        )

        curve_cv_positions = camera_path_curve.getCVs()

        # pop the unnecessary CVs
        curve_cv_positions.pop(1)
        curve_cv_positions.pop(-2)

        prev_pos = curve_cv_positions[0]
        for i, j in enumerate(range(start_frame, end_frame)):
            pm.currentTime(j)
            current_pos = curve_cv_positions[i]
            node.t.set(curve_cv_positions[i])
            node.speed.set((current_pos - prev_pos).length())
            pm.setKeyframe(node.speed)
            prev_pos = current_pos

    @classmethod
    def bake_all_constraints(cls):
        """Bakes all constraints in the current scene
        """
        # TODO: Bake selectively
        command  = 'bakeResults -simulation true -t "{start}:{end}" ' \
                   '-sampleBy 1 -oversamplingRate 1 ' \
                   '-disableImplicitControl true -preserveOutsideKeys true ' \
                   '-sparseAnimCurveBake false ' \
                   '-removeBakedAttributeFromLayer false ' \
                   '-removeBakedAnimFromLayer false ' \
                   '-bakeOnOverrideLayer false -minimizeRotation true ' \
                   '-at "tx" -at "ty" -at "tz" -at "rx" -at "ry" -at "rz" ' \
                   '{objects};'

        start_frame = int(pm.playbackOptions(q=1, min=1))
        end_frame = int(pm.playbackOptions(q=1, max=1))

        all_transforms = []
        for node in pm.ls(type="constraint"):
            all_transforms += node.outputs(type='transform')

        object_names = ' '.join([node.longName() for node in all_transforms])
        bake_command = command.format(
            start=start_frame,
            end=end_frame,
            objects=object_names
        )
        pm.mel.eval(bake_command)

    @classmethod
    def bake_alembic_animations(cls):
        """bakes all animations of transform nodes connected to an alembic node
        """
        command  = 'bakeResults -simulation true -t "{start}:{end}" ' \
           '-sampleBy 1 -oversamplingRate 1 ' \
           '-disableImplicitControl true -preserveOutsideKeys true ' \
           '-sparseAnimCurveBake false ' \
           '-removeBakedAttributeFromLayer false ' \
           '-removeBakedAnimFromLayer false ' \
           '-bakeOnOverrideLayer false -minimizeRotation true ' \
           '-at "tx" -at "ty" -at "tz" -at "rx" -at "ry" -at "rz" ' \
           '{objects};'

        start_frame = int(pm.playbackOptions(q=1, min=1))
        end_frame = int(pm.playbackOptions(q=1, max=1))

        all_transforms = []
        for node in pm.ls(type="AlembicNode"):
            all_transforms += node.outputs(type='transform')

        object_names = ' '.join([node.longName() for node in all_transforms])
        bake_command = command.format(
            start=start_frame,
            end=end_frame,
            objects=object_names
        )
        pm.mel.eval(bake_command)

    @classmethod
    def delete_base_anim_layer(cls):
        """deletes the base anim layer
        """
        base_layer = pm.PyNode('BaseAnimation')
        base_layer.unlock()
        pm.delete(base_layer)

    @classmethod
    def oySmoothComponentAnimation(cls, ui_item):
        """calls the mel script oySmoothComponentAnimation
        """
        # get the frame range
        frame_range = pm.textFieldButtonGrp(
            ui_item, q=1, tx=1
        )
        pm.mel.eval('oySmoothComponentAnimation(%s)' % frame_range)

    @classmethod
    def cam_2_chan(cls, startButton, endButton):
        start = int(pm.textField(startButton, q=True, tx=True))
        end = int(pm.textField(endButton, q=True, tx=True))
        cam_to_chan(start, end)

    @classmethod
    def create_alembic_command(cls):
        """for ui
        """
        from_top_node = pm.checkBox('from_top_node_checkBox', q=1, v=1)
        cls.create_alembic(from_top_node)

    @classmethod
    def create_alembic(cls, from_top_node=1):
        """creates alembic cache from selected nodes
        """
        import os
        root_flag = '-root %(node)s'
        mel_command = 'AbcExport -j "-frameRange %(start)s %(end)s -ro ' \
                      '-stripNamespaces -uvWrite -wholeFrameGeo -worldSpace ' \
                      '%(roots)s ' \
                      '-file %(path)s";'

        current_path = pm.workspace.path
        abc_path = os.path.join(current_path, 'cache', 'alembic')
        try:
            os.makedirs(abc_path)
        except OSError:
            pass

        abc_full_path = pm.fileDialog2(startingDirectory=abc_path)

        def find_top_parent(node):
            parents = node.listRelatives(p=1)
            parent = None
            while parents:
                parent = parents[0]
                parents = parent.listRelatives(p=1)
                if parents:
                    parent = parents[0]
                else:
                    return parent
            if not parent:
                return node
            else:
                return parent

        if abc_full_path:
            abc_full_path = abc_full_path[0]  # this is dirty
            abc_full_path = os.path.splitext(abc_full_path)[0] + '.abc'

            # get nodes
            selection = pm.ls(sl=1)
            nodes = []
            for node in selection:
                if from_top_node:
                    node = find_top_parent(node)
                if node not in nodes:
                    nodes.append(node)

            # generate root flags
            roots = []
            for node in nodes:
                roots.append(
                    root_flag % {
                        'node': node.fullPath()
                    }
                )

            roots_as_string = ' '.join(roots)

            start = int(pm.playbackOptions(q=1, minTime=1))
            end = int(pm.playbackOptions(q=1, maxTime=1))
            rendered_mel_command = mel_command % {
                'start': start,
                'end': end,
                'roots': roots_as_string,
                'path': abc_full_path
            }
            pm.mel.eval(rendered_mel_command)

    @classmethod
    def copy_alembic_data(cls, source=None, target=None):
        """Copies alembic data from source to target hierarchy
        """
        selection = pm.ls(sl=1)
        if not source or not target:
            source = selection[0]
            target = selection[1]

        #
        # Move Alembic Data From Source To Target
        #
        #selection = pm.ls(sl=1)
        #
        #source = selection[0]
        #target = selection[1]

        source_nodes = source.listRelatives(
            ad=1,
            type=(pm.nt.Mesh, pm.nt.NurbsSurface)
        )
        target_nodes = target.listRelatives(
            ad=1,
            type=(pm.nt.Mesh, pm.nt.NurbsSurface)
        )

        source_node_names = []
        target_node_names = []

        for node in source_nodes:
            name = node.name().split(':')[-1].split('|')[-1]
            source_node_names.append(name)

        for node in target_nodes:
            name = node.name().split(':')[-1].split('|')[-1]
            target_node_names.append(name)

        lut = []

        for i, target_node in enumerate(target_nodes):
            target_node_name = target_node_names[i]
            try:
                index = source_node_names.index(target_node_name)
            except ValueError:
                pass
            else:
                lut.append((source_nodes[index], target_nodes[i]))

        for source_node, target_node in lut:
            if isinstance(source_node, pm.nt.Mesh):
                in_attr_name = 'inMesh'
                out_attr_name = 'outMesh'
            else:
                in_attr_name = 'create'
                out_attr_name = 'worldSpace'

            conns = source_node.attr(in_attr_name).inputs(p=1)
            if conns:
                for conn in conns:
                    if isinstance(conn.node(), pm.nt.AlembicNode):
                        conn >> target_node.attr(in_attr_name)
                        break
            else:
                # no connection
                # just connect the shape itself
                source_node.attr(out_attr_name) >> \
                    target_node.attr(in_attr_name)

    @classmethod
    def bake_component_animation(cls):
        """bakes the selected component animation to a space locator
        """
        start = int(pm.playbackOptions(q=1, minTime=1))
        end = int(pm.playbackOptions(q=1, maxTime=1))

        vertices = pm.ls(sl=1, fl=1)

        locator = pm.spaceLocator()

        for i in range(start, end+1):
            pm.currentTime(i)
            point_positions = pm.xform(vertices, q=1, ws=1, t=1)
            point_count = len(point_positions) / 3
            px = reduce(lambda x, y: x+y, point_positions[0::3]) / point_count
            py = reduce(lambda x, y: x+y, point_positions[1::3]) / point_count
            pz = reduce(lambda x, y: x+y, point_positions[2::3]) / point_count

            locator.t.set(px, py, pz)
            pm.setKeyframe(locator.tx)
            pm.setKeyframe(locator.ty)
            pm.setKeyframe(locator.tz)

    @classmethod
    def attach_follicle(cls):
        """attaches a follicle on selected mesh vertices
        """
        pnts = pm.ls(sl=1)

        for pnt in pnts:
            mesh = pnt.node()
            follicle = pm.createNode('follicle')
            mesh.worldMesh[0] >> follicle.inputMesh
            uv = pnts[0].getUV()
            follicle.parameterU.set(uv[0])
            follicle.parameterV.set(uv[1])
            follicle_t = follicle.getParent()
            follicle.outTranslate >> follicle_t.t
            follicle.outRotate >> follicle_t.r

    @classmethod
    def set_range_from_shot(cls):
        """sets the playback range from a shot node in the scene
        """
        shots = pm.ls(type='shot')
        min_frame = None
        max_frame = None
        if shots:
            # use the available shot node
            shot = shots[0]
            min_frame = shot.getAttr('startFrame')
            max_frame = shot.getAttr('endFrame')
        else:
            # check if this is a shot related scene
            from anima.env import mayaEnv
            m = mayaEnv.Maya()
            v = m.get_current_version()
            if v:
                t = v.task
                from stalker import Shot
                parents = t.parents
                parents.reverse()
                for p in parents:
                    if isinstance(p, Shot):
                        pm.warning(
                            'No shot node in the scene, '
                            'using the Shot task!!!'
                        )
                        min_frame = p.cut_in
                        max_frame = p.cut_out
                        break

        if min_frame is not None and max_frame is not None:
            pm.playbackOptions(
                ast=min_frame,
                aet=max_frame,
                min=min_frame,
                max=max_frame
            )
        else:
            pm.error(
                'No shot node in the scene, nor the task is related to a Shot!'
            )