# -*- coding: utf-8 -*-

from anima.utils import do_db_setup
from pymel import core as pm
from anima.utils.progress import ProgressManager


class Reference(object):
    """supplies reference related tools"""

    @classmethod
    def select_reference_in_reference_editor(cls):
        """selects the reference node in the reference editor related to the
        scene selection
        """
        selection = pm.selected()
        if not selection:
            return

        node = selection[0]
        ref_file = node.referenceFile()

        if ref_file is None:
            return

        ref_node = ref_file.refNode

        # gather reference editor data
        ref_editor_panel = pm.mel.globals["gReferenceEditorPanel"]
        ref_editor_data = {}

        i = 0  # be safe
        while True and i < 1000:
            try:
                pm.sceneEditor(ref_editor_panel, e=1, selectItem=i)
            except RuntimeError:
                break

            sel_ref_node_name = pm.sceneEditor(
                ref_editor_panel, q=1, selectReference=1
            )[0]

            ref_editor_data[i] = pm.PyNode(sel_ref_node_name)
            i += 1

        for i, ref_editor_ref_node in ref_editor_data.items():
            if ref_editor_ref_node == ref_node:
                pm.sceneEditor(ref_editor_panel, e=1, selectItem=i)

    @classmethod
    def get_no_parent_transform(cls, ref):
        """returns the top most parent node in the given subReferences

        :param ref: pm.nt.FileReference instance
        """
        all_referenced_nodes = ref.nodes()
        for node in all_referenced_nodes:
            if isinstance(node, pm.nt.Transform):
                # print('%s has parent' % node.name())
                parent_node = node.getParent()
                if parent_node not in all_referenced_nodes:
                    return node

        # check sub references
        sub_refs = pm.listReferences(ref)
        for sub_ref in sub_refs:
            no_parent_transform = cls.get_no_parent_transform(sub_ref)
            if no_parent_transform:
                return no_parent_transform

    @classmethod
    def duplicate_selected_reference(cls):
        """duplicates the selected referenced object as reference"""
        all_selected_refs = []
        for sel_node in pm.ls(sl=1):
            ref = sel_node.referenceFile()
            if ref not in all_selected_refs:
                all_selected_refs.append(ref)

        select_list = []
        for ref in all_selected_refs:
            # get the highest parent ref
            if ref.parent():
                while ref.parent():
                    ref = ref.parent()

            namespace = ref.namespace
            dup_ref = pm.createReference(
                ref.path, gl=True, namespace=namespace, options="v=0"
            )

            top_parent = cls.get_no_parent_transform(ref)
            if top_parent:
                node = top_parent
                tra = pm.xform(node, q=1, ws=1, t=1)
                rot = pm.xform(node, q=1, ws=1, ro=1)
                sca = pm.xform(node, q=1, ws=1, s=1)

                new_top_parent_node = cls.get_no_parent_transform(dup_ref)
                pm.xform(new_top_parent_node, ws=1, t=tra)
                pm.xform(new_top_parent_node, ws=1, ro=rot)
                pm.xform(new_top_parent_node, ws=1, s=sca)

                # parent to the same group
                group = node.getParent()
                if group:
                    pm.parent(new_top_parent_node, group)

                # select the top node
                select_list.append(new_top_parent_node)
        pm.select(select_list)
        return select_list

    # @classmethod
    # def duplicate_rs_proxy(cls):
    #     """duplicates the given rs proxy object
    #     """
    #     for node in pm.selected(type='transform'):
    #         shape = node.getShape()
    #         if not shape:
    #             continue
    #         # get the rs proxy node
    #         shape_inputs = shape.inMesh.inputs()
    #         proxy_node = None
    #         for n in shape_inputs:
    #             if isinstance(n, pm.nt.RedshiftProxyMesh):
    #                 proxy_node = n
    #                 break
    #         # now duplicate the hierarchy
    #         dup = pm.duplicate(node)
    #         # this will create the shape but will not create the proxy
    #         new_proxy_node = pm.nt.RedshiftProxyMesh()
    #         new_proxy_node.

    @classmethod
    def publish_model_as_look_dev(cls):
        """Publishes Model versions as LookDev versions of the same task.

        Also handles references etc.
        """
        #
        # Create LookDev for Current Model Task
        #

        from stalker import Task, Version, Type, LocalSession
        from stalker.db.session import DBSession
        from anima import defaults
        from anima.dcc import mayaEnv

        do_db_setup()
        m = mayaEnv.Maya()

        local_session = LocalSession()
        logged_in_user = local_session.logged_in_user
        if not logged_in_user:
            raise RuntimeError("Please login to Stalker")

        model_type = Type.query.filter(Type.name == "Model").first()
        look_dev_type = Type.query.filter(Type.name == "Look Development").first()

        current_version = m.get_current_version()
        model_task = current_version.task

        if model_task.type != model_type:
            raise RuntimeError("This is not a Model version")

        if not current_version.is_published:
            raise RuntimeError("Please Publish this maya scene")

        if current_version.take_name != "Main":
            raise RuntimeError("This is not the Main take")

        # find lookDev
        look_dev = (
            Task.query.filter(Task.parent == model_task.parent)
            .filter(Task.type == look_dev_type)
            .first()
        )

        if not look_dev:
            raise RuntimeError(
                "There is no LookDev task, please inform your Stalker admin"
            )

        previous_look_dev_version = (
            Version.query.filter(Version.task == look_dev)
            .filter(Version.take_name == "Main")
            .first()
        )

        description = "Auto Created By %s " % logged_in_user.name
        take_name = defaults.version_take_name
        if not previous_look_dev_version:
            # do the trick
            pm.newFile(f=1)

            # create a new version
            new_version = Version(
                task=look_dev,
                description=description,
                take_name=take_name,
                created_by=logged_in_user,
            )
            new_version.is_published = True

            m.save_as(new_version)

            # reference the model version
            pm.createReference(
                current_version.absolute_full_path,
                gl=True,
                namespace=current_version.nice_name,
                options="v=0",
            )

            pm.saveFile()
            DBSession.add(new_version)

        else:
            latest_look_dev_version = previous_look_dev_version.latest_version
            reference_resolution = m.open(
                latest_look_dev_version, force=True, skip_update_check=True
            )
            m.update_versions(reference_resolution)

            if reference_resolution["update"] or reference_resolution["create"]:
                # create a new version
                new_version = Version(
                    task=look_dev,
                    description=description,
                    take_name=take_name,
                    created_by=logged_in_user,
                    parent=latest_look_dev_version,
                )
                new_version.is_published = True

                m.save_as(new_version)

        # reopen model scene
        m.open(current_version, force=True, skip_update_check=True)

    @classmethod
    def get_selected_reference_path(cls):
        """prints the path of the selected reference path"""
        selection = pm.ls(sl=1)
        if len(selection):
            node = selection[0]
            ref = node.referenceFile()
            if ref:
                print(ref.path)
                parent_ref = ref.parent()
                while parent_ref is not None:
                    print(parent_ref.path)
                    parent_ref = parent_ref.parent()

    @classmethod
    def open_reference_in_new_maya(cls):
        """opens the selected references in new maya session"""
        import subprocess

        selection = pm.ls(sl=1)
        if len(selection):
            node = selection[0]
            ref = node.referenceFile()
            if ref:
                process = subprocess.Popen(["maya", ref.path], stderr=subprocess.PIPE)

    @classmethod
    def fix_reference_namespace(cls):
        """fixes reference namespace"""
        ref_count = len(pm.listReferences(recursive=True))

        if ref_count > 25:
            result = pm.windows.confirmBox(
                "Fix Reference Namespace",
                "You have %s references in your scene,\n"
                "this will take too much time\n\nIs that Ok?" % ref_count,
            )
            if not result:
                return

        from stalker import LocalSession
        from anima.dcc import mayaEnv

        m = mayaEnv.Maya()

        local_session = LocalSession()
        logged_in_user = local_session.logged_in_user

        if not logged_in_user:
            raise RuntimeError("Please login before running the script")

        versions = m.fix_reference_namespaces()
        for version in versions:
            version.created_by = logged_in_user

        from stalker.db.session import DBSession

        DBSession.commit()

    @classmethod
    def fix_reference_paths(cls):
        """Fixes reference paths that are not using environment vars"""
        # list current scene references
        from anima.dcc import mayaEnv

        m_env = mayaEnv.Maya()
        current_version = m_env.get_current_version()

        all_refs = pm.listReferences(recursive=True)
        refs_with_wrong_prefix = []

        for ref in all_refs:
            if "$REPO" not in ref.unresolvedPath():
                parent = ref.parent()
                if parent:
                    refs_with_wrong_prefix.append(parent)

        ref_paths = [ref.path for ref in refs_with_wrong_prefix]
        for ref_path in ref_paths:
            version = m_env.get_version_from_full_path(ref_path)
            if version:
                m_env.open(version, force=True, skip_update_check=True)
                pm.saveFile()

        if pm.env.sceneName() != current_version.absolute_full_path:
            m_env.open(current_version, force=True, skip_update_check=True)

    @classmethod
    def fix_student_license_on_references(cls):
        """fixes the student license error on referenced files"""
        for ref in pm.listReferences():
            result = cls.fix_student_license(ref.path)
            if result:
                ref.unload()
                ref.load()

    @classmethod
    def fix_student_license_on_selected_file(cls):
        """fixes the student license error on selected file"""
        texture_path = file_path = pm.fileDialog2(
            cap="Choose Maya Scene", okc="Choose", fm=1
        )[0]
        result = cls.fix_student_license(file_path)
        if result:
            pm.informBox("Done!", "Fixed:\n\n%s" % file_path)
        else:
            pm.informBox("Fail!", "No Student License Found on\n\n%s" % file_path)

    @classmethod
    def fix_student_license(cls, path):
        """fixes the student license error"""
        import shutil

        with open(path, "r") as f:
            data = f.readlines()

        for i in range(200):
            if "student" in data[i].lower():
                # backup the file
                shutil.copy(path, "%s.orig" % path)
                data.pop(i)
                print("Fixed: %s" % path)
                with open(path, "w") as f:
                    f.writelines(data)
                return True

        return False

    @classmethod
    def archive_current_scene(cls):
        """archives the current scene"""
        from anima.dcc.mayaEnv import Maya
        from anima.dcc.mayaEnv.archive import Archiver
        from anima.utils.archive import archive_current_scene

        m_env = Maya()
        version = m_env.get_current_version()
        archiver = Archiver()
        archive_current_scene(version, archiver)

    @classmethod
    def bind_to_original(cls):
        """binds the current scene references to original references from the
        repository
        """
        # get all reference paths
        import os
        from anima.dcc import mayaEnv
        from stalker import Repository, Task, Project, Version

        m = mayaEnv.Maya()
        current_version = m.get_current_version()

        # get the current project
        project = None
        if current_version:
            project = current_version.task.project
        else:
            raise RuntimeError(
                "The current scene is unknown to Stalker!!! "
                "Please, save this scene first."
            )

        # no project then do nothing
        if project:
            for ref in pm.listReferences():
                unresolved_path = ref.unresolvedPath()
                filename = os.path.basename(unresolved_path)
                # find the corresponding version
                v = (
                    Version.query.join(Version.task, Task.versions)
                    .filter(Task.project == project)
                    .filter(Version.full_path.endswith(filename))
                    .first()
                )
                if not v:
                    # try to look in to all projects, order by
                    v = (
                        Version.query.join(Version.task, Task.versions)
                        .join(Project, Task.project)
                        .filter(Version.full_path.endswith(filename))
                        .order_by(Project.date_created)
                        .first()
                    )

                if v:
                    ref.replaceWith(
                        Repository.to_os_independent_path(v.absolute_full_path)
                    )

    @classmethod
    def unload_selected_references(cls):
        """unloads the highest parent references that is related to the selected objects"""
        refs_to_unload = []

        # store selected references
        for node in pm.ls(sl=1):
            ref = node.referenceFile()

            if not ref:
                # not a reference, skip
                continue

            # get the highest parent ref
            parent_ref = ref.parent()

            i = 0
            while parent_ref and i < 100:
                ref = parent_ref
                parent_ref = ref.parent()
                i += 1

            if ref not in refs_to_unload:
                refs_to_unload.append(ref)

        for ref in refs_to_unload:
            ref.unload()

    @classmethod
    def remove_selected_references(cls):
        """removes the highest parent references that is related to the selected objects"""
        refs_to_remove = []

        # store selected references
        for node in pm.ls(sl=1):
            ref = node.referenceFile()

            if not ref:
                # not a reference, skip
                continue

            # get the highest parent ref
            parent_ref = ref.parent()

            i = 0
            while parent_ref and i < 100:
                ref = parent_ref
                parent_ref = ref.parent()
                i += 1

            if ref not in refs_to_remove:
                refs_to_remove.append(ref)

        response = pm.confirmDialog(
            title="Remove Selected References?",
            message="Remove selected references\n\n%s"
            % "\n".join(map(lambda x: str(x), refs_to_remove)),
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No",
        )

        if response == "No":
            return

        for ref in refs_to_remove:
            ref.remove()

    @classmethod
    def unload_unselected_references(cls):
        """unloads the references that is not related to the selected objects"""
        import copy

        selected_references = []

        # store selected references
        for node in pm.ls(sl=1):
            ref = node.referenceFile()
            if ref is not None and ref not in selected_references:
                selected_references.append(ref)

        temp_selected_references = copy.copy(selected_references)

        # store parent references
        for ref in temp_selected_references:
            parent_ref = ref.parent()
            if parent_ref is not None and parent_ref not in selected_references:
                while parent_ref is not None:
                    if parent_ref not in selected_references:
                        selected_references.append(parent_ref)
                    parent_ref = parent_ref.parent()

        # now unload all the other references
        for ref in reversed(pm.listReferences(recursive=1)):
            if ref not in selected_references:
                ref.unload()

    @classmethod
    def to_base(cls, apply_to=0):
        """Replace the related references with Base representation.

        :param int apply_to: 0: All 1: Selected
        """
        cls.to_repr("Base", apply_to=apply_to)

    @classmethod
    def to_gpu(cls, apply_to=0):
        """Replace the related references with GPU representation.

        :param int apply_to: 0: All 1: Selected
        """
        cls.to_repr("GPU", apply_to=apply_to)

    @classmethod
    def to_ass(cls, apply_to=0):
        """Replace the related references with the ASS representation.

        :param int apply_to: 0: All 1: Selected
        """
        cls.to_repr("ASS", apply_to=apply_to)

    @classmethod
    def to_rs(cls, apply_to=0):
        """Replace the related references with the RS representation.

        :param int apply_to: 0: All 1: Selected
        """
        cls.to_repr("RS", apply_to=apply_to)

    @classmethod
    def to_repr(cls, repr_name, apply_to=0):
        """replaces the related references with the given representation

        :param str repr_name: Desired representation name
        :param int apply_to: 0: All 1: Selected
        """
        if apply_to == 1:
            # work on every selected object
            selection = pm.ls(sl=1)

            # collect reference files first
            references = []
            for node in selection:
                ref = node.referenceFile()
                # get the topmost parent
                ref = ref.topmost_parent

                if ref is not None and ref not in references:
                    references.append(ref)

            from anima.dcc.mayaEnv.repr_tools import RepresentationGenerator

            # now go over each reference
            for ref in references:
                if not ref.is_repr(repr_name):
                    parent_ref = ref
                    while parent_ref is not None:
                        # check if it is a look dev node
                        v = parent_ref.version
                        if v:
                            task = v.task
                            if RepresentationGenerator.is_look_dev_task(
                                task
                            ) or RepresentationGenerator.is_vegetation_task(task):
                                # convert it to repr
                                parent_ref.to_repr(repr_name)
                                break
                            else:
                                # go to parent ref
                                parent_ref = parent_ref.parent()
                        else:
                            parent_ref = parent_ref.parent()
        elif apply_to == 2:
            # apply to all references
            for ref in pm.listReferences():
                ref.to_repr(repr_name)

    @classmethod
    def generate_repr_of_scene_caller(cls):
        """helper method to call Reference.generate_repr_of_scene() with data
        coming from UI
        """
        generate_gpu = (
            1 if pm.checkBoxGrp("generate_repr_types_checkbox_grp", q=1, v1=1) else 0
        )
        generate_ass = (
            1 if pm.checkBoxGrp("generate_repr_types_checkbox_grp", q=1, v2=1) else 0
        )
        generate_rs = (
            1 if pm.checkBoxGrp("generate_repr_types_checkbox_grp", q=1, v3=1) else 0
        )

        skip_existing = pm.checkBox("generate_repr_skip_existing_checkBox", q=1, v=1)

        cls.generate_repr_of_scene(
            generate_gpu, generate_ass, generate_rs, skip_existing
        )

    @classmethod
    def generate_repr_of_scene(
        cls, generate_gpu=True, generate_ass=True, generate_rs=True, skip_existing=False
    ):
        """generates desired representations of this scene"""
        from anima.dcc.mayaEnv import Maya, repr_tools

        response = pm.confirmDialog(
            title="Do Create Representations?",
            message="Create all Repr. for this scene?",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No",
        )
        if response == "No":
            return

        # register a new caller
        pdm = ProgressManager()

        m_env = Maya()
        source_version = m_env.get_current_version()
        gen = repr_tools.RepresentationGenerator()

        # open each version
        from stalker import Version

        if skip_existing:
            # check if there is a GPU or ASS repr
            # generated from this version
            child_versions = Version.query.filter(
                Version.parent == source_version
            ).all()
            for cv in child_versions:
                if generate_gpu is True and "@GPU" in cv.take_name:
                    generate_gpu = False

                if generate_ass is True and "@ASS" in cv.take_name:
                    generate_ass = False

                if generate_rs is True and "@RS" in cv.take_name:
                    generate_rs = False

        total_number_of_reprs = generate_gpu + generate_ass + generate_rs
        caller = pdm.register(total_number_of_reprs, title="Generate Reprs")

        gen.version = source_version
        # generate representations
        if generate_gpu:
            gen.generate_gpu()
            caller.step()

        if generate_ass:
            gen.generate_ass()
            caller.step()

        if generate_rs:
            gen.generate_rs()
            caller.step()

        # now open the source version again
        m_env.open(source_version, force=True, skip_update_check=True)

    @classmethod
    def generate_repr_of_all_references_caller(cls):
        """a helper method that calls
        References.generate_repr_of_all_references() with paremeters from the
        UI
        """
        generate_gpu = pm.checkBoxGrp("generate_repr_types_checkbox_grp", q=1, v1=1)
        generate_ass = pm.checkBoxGrp("generate_repr_types_checkbox_grp", q=1, v2=1)
        generate_rs = pm.checkBoxGrp("generate_repr_types_checkbox_grp", q=1, v3=1)

        skip_existing = pm.checkBox("generate_repr_skip_existing_checkBox", q=1, v=1)

        cls.generate_repr_of_all_references(
            generate_gpu, generate_ass, generate_rs, skip_existing
        )

    @classmethod
    def generate_repr_of_all_references(
        cls, generate_gpu=True, generate_ass=True, generate_rs=True, skip_existing=False
    ):
        """generates all representations of all references of this scene"""
        from anima.dcc.mayaEnv import Maya, repr_tools

        paths_visited = []
        versions_to_visit = []
        versions_cannot_be_published = []

        # generate a sorted version list
        # and visit each reference only once
        pdm = ProgressManager()

        all_refs = pm.listReferences(recursive=True)
        caller = pdm.register(len(all_refs), "List References")

        for ref in reversed(all_refs):
            ref_path = str(ref.path)
            caller.step(message=ref_path)
            if ref_path not in paths_visited:
                v = ref.version
                if v is not None:
                    paths_visited.append(ref_path)
                    versions_to_visit.append(v)

        response = pm.confirmDialog(
            title="Do Create Representations?",
            message="Create all Repr. for all %s FileReferences?"
            % len(versions_to_visit),
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No",
        )
        if response == "No":
            return

        # register a new caller
        caller = pdm.register(
            max_iteration=len(versions_to_visit), title="Generate Reprs"
        )

        m_env = Maya()
        source_version = m_env.get_current_version()
        gen = repr_tools.RepresentationGenerator()

        # open each version
        from stalker import Version

        for v in versions_to_visit:
            local_generate_gpu = generate_gpu
            local_generate_ass = generate_ass
            local_generate_rs = generate_rs

            # check if this is a repr
            if "@" in v.take_name:
                # use the parent
                v = v.parent
                if not v:
                    continue

            if skip_existing:
                # check if there is a GPU or ASS repr
                # generated from this version
                child_versions = Version.query.filter(Version.parent == v).all()
                for cv in child_versions:
                    if local_generate_gpu is True and "@GPU" in cv.take_name:
                        local_generate_gpu = False

                    if local_generate_ass is True and "@ASS" in cv.take_name:
                        local_generate_ass = False

                    if local_generate_rs is True and "@RS" in cv.take_name:
                        local_generate_rs = False

            gen.version = v
            # generate representations
            if local_generate_gpu:
                try:
                    gen.generate_gpu()
                except RuntimeError:
                    if v not in versions_cannot_be_published:
                        versions_cannot_be_published.append(v)

            if local_generate_ass:
                try:
                    gen.generate_ass()
                except RuntimeError:
                    if v not in versions_cannot_be_published:
                        versions_cannot_be_published.append(v)

            if local_generate_rs:
                try:
                    gen.generate_rs()
                except RuntimeError:
                    if v not in versions_cannot_be_published:
                        versions_cannot_be_published.append(v)

            caller.step()

        # now open the source version again
        m_env.open(source_version, force=True, skip_update_check=True)

        # and generate representation for the source
        gen.version = source_version

        # generate representations
        if not versions_cannot_be_published:
            if generate_gpu:
                gen.generate_gpu()
            if generate_ass:
                gen.generate_ass()
            if generate_rs:
                gen.generate_rs()
        else:
            pm.confirmDialog(
                title="Error",
                message="The following versions can not be published "
                "(check script editor):\n\n%s"
                % ("\n".join(map(lambda x: x.nice_name, versions_cannot_be_published))),
                button=["OK"],
                defaultButton="OK",
                cancelButton="OK",
                dismissString="OK",
            )

            pm.error(
                "\n".join(
                    map(lambda x: x.absolute_full_path, versions_cannot_be_published)
                )
            )
