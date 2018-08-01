# -*- coding: utf-8 -*-
# Copyright (c) 2017-2018, Erkan Ozgur Yilmaz
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import MaxPlus
from anima.env.base import EnvironmentBase


def get_max_version():
    """Encapsulates the very cumbersome 3ds Max version string retrieval
    process and returns a simple string that contains the current MAX
    version.

    :return:
    """
    versions_LUT = {
        17000: '2015',
        18000: '2016',
        19000: '2017'
    }

    c = MaxPlus.Core.EvalMAXScript('maxVersion()')
    l = c.GetIntList()
    return versions_LUT[l.GetItem(0)]


class Max(EnvironmentBase):
    """The 3dsmax environment class
    """

    name = "3dsMax%s" % get_max_version()
    extensions = ['.max']

    def get_current_version(self):
        """Returns the current Stalker version from the open scene

        :return:
        """
        version = None

        # pm.env.sceneName() always uses "/"
        full_path = MaxPlus.FileManager.GetFileNameAndPath()
        # try to get it from the current open scene
        if full_path != '':
            version = self.get_version_from_full_path(full_path)

        return version

    def open(self, version, force=False, representation=None,
             reference_depth=0, skip_update_check=False):
        """Opens the given version file

        :param version: The Stalker version instance
        :param force: force open, so don't care if there are any unsaved
          changes in the current scene.
        :param representation: The desired representation for the XRef files
          (Not Implemented)
        :param reference_depth: (Not Implemented)
        :param skip_update_check: (Not Implemented)
        :return: Returns a reference resolution that shows what to update.
        """
        # before open: set the system units and gamma settings to their
        # defaults
        self.set_system_units()
        self.set_gamma_settings()

        # set the project dir
        self.set_project(version)

        # then open the file
        MaxPlus.FileManager.Open(version.absolute_full_path, True)

        if not skip_update_check:
            # check the referenced versions for any possible updates
            return self.check_referenced_versions()
        else:
            from anima.env import empty_reference_resolution
            return empty_reference_resolution()

    def save_as(self, version, run_pre_publishers=True):
        """Saves the current scene under the given version.

        :param version: The Stalker.Version instance
        :param run_pre_publishers: A bool flag that allows skipping the pre
          publishers.
        :return:
        """
        # get the current version, and store it as the parent of the new
        # version
        current_version = self.get_current_version()

        version.update_paths()
        version.extension = self.extensions[0]

        # define that this version is created with Max
        version.created_with = self.name

        project = version.task.project

        # set the project dir
        self.set_project(version)

        # check if this is a shot related task
        is_shot_related_task = False
        shot = None
        from stalker import Shot
        for task in version.task.parents:
            if isinstance(task, Shot):
                is_shot_related_task = True
                shot = task
                break

        # set scene fps
        # even if this is not the first version set the fps
        #
        # or better try to get the parent versions and see if we can reach to
        # a v001 which will guarantee that this version is coming from a file
        # that has its fps set before.
        #
        # If we can't get a v001 file, than it means that the user created a
        # new scene and saved it as a new version for series of already
        # existing versions, (ex. save as v002 for the first time)
        #
        # Let's hope that it will not break animators scenes, where we have
        # 12 FPS set for the shot and the intended fps is 25 which we will
        # newer know.
        if is_shot_related_task:
            self.set_fps(shot.fps)

            # set render resolution
            self.set_resolution(shot.image_format.width,
                                shot.image_format.height,
                                shot.image_format.pixel_aspect)
            # set the render range if it is the first version
            if version.version_number == 1:
                self.set_frame_range(shot.cut_in, shot.cut_out)
        else:
            # set render resolution
            if version.version_number == 1:
                self.set_resolution(project.image_format.width,
                                    project.image_format.height,
                                    project.image_format.pixel_aspect)
            self.set_fps(project.fps)

        # set the render file name and version
        self.set_render_filename(version)

        # create the folders beforehand
        try:
            import os
            os.makedirs(version.absolute_path)
        except OSError:
            pass

        MaxPlus.FileManager.Save(version.absolute_full_path)

        # update the parent info
        if version != current_version:  # prevent CircularDependencyError
            version.parent = current_version

        from stalker.db.session import DBSession
        DBSession.add(version)

        # append it to the recent file list
        self.append_to_recent_files(
            version.absolute_full_path
        )

        DBSession.commit()

        self.create_local_copy(version)

        return True

    def export_as(self, version):
        """the export action for max environment
        """
        import MaxPlus
        # check if there is something selected
        if MaxPlus.SelectionManager.GetCount() < 1:
            raise RuntimeError("There is nothing selected to export")

        # check if this is the first version
        if version.is_published and not self.allow_publish_on_export:
            # it is not allowed to publish the first version (desdur)
            raise RuntimeError(
                'It is not allowed to Publish while export!!!'
                '<br><br>'
                'Export it normally. Then open the file and publish it.'
            )

        # do not save if there are local files
        # self.check_external_files(version)

        # set the extension to max by default
        version.update_paths()
        version.extension = self.extensions[0]

        # define that this version is created with Max
        version.created_with = self.name

        # create the folder if it doesn't exists
        import os
        try:
            os.makedirs(version.absolute_path)
        except OSError:
            # already exists
            pass

        # workspace_path = os.path.dirname(version.absolute_path)
        workspace_path = version.absolute_path

        # self.create_workspace_file(workspace_path)
        # self.create_workspace_folders(workspace_path)

        # export the file
        MaxPlus.FileManager.SaveSelected(version.absolute_full_path)

        # save the version to database
        from stalker.db.session import DBSession
        DBSession.add(version)
        DBSession.commit()

        # create a local copy
        self.create_local_copy(version)

        return True

    def import_(self, version, use_namespace=True):
        """Imports the content of the given Version instance to the current
        scene.

        :param version: The desired
          :class:`~stalker.models.version.Version` to be imported
        :param bool use_namespace: use namespace or not.
        """
        from pymxs import runtime as rt
        rt.mergeMAXFile(version.absolute_full_path)
        return True

    def reference(self, version, use_namespace=True):
        """Creates an XRef for the given version in the current scene.

        :param version: The Stalker Verison instance.
        :param bool use_namespace: Use a namespace or not.
        :return:
        """
        import os
        from anima.representation import Representation
        import pymxs
        rt = pymxs.runtime

        file_full_path = version.absolute_full_path
        namespace = os.path.basename(version.nice_name)

        namespace = namespace.split(Representation.repr_separator)[0]

        xref_objects = rt.getMAXFileObjectNames(file_full_path)
        xref = rt.xrefs.addNewXRefObject(
            file_full_path,
            xref_objects,
            # dupMtlNameAction='#autoRename'
        )

        # append the referenced version to the current versions references
        # attribute
        current_version = self.get_current_version()
        if current_version:
            current_version.inputs.append(version)
            from stalker.db.session import DBSession
            DBSession.commit()

        # append it to reference path
        self.append_to_recent_files(file_full_path)

        return xref

    def deep_version_inputs_update(self):
        """updates the inputs of the references of the current scene
        """
        # first update with data from first level references
        self.update_version_inputs()

    def get_referenced_versions(self, parent_ref=None):
        """Returns a list of Version instances that are referenced to the
        current scene.

        :return:
        """
        from pymxs import runtime as rt
        xref_file_names = []
        versions = []

        record_count = rt.objXRefMgr.recordCount
        references = []

        if not parent_ref:
            for i in range(record_count):
                record = rt.objXRefMgr.GetRecord(i + 1)
                if not record.nested:
                    file_name = record.srcFileName
                    if file_name not in xref_file_names:
                        xref_file_names.append(file_name)
        else:
            for record in parent_ref.GetChildRecords():
                file_name = record.srcFileName
                if file_name not in xref_file_names:
                    xref_file_names.append(file_name)

        for path in xref_file_names:
            version = self.get_version_from_full_path(path)
            if version and version not in versions:
                versions.append(version)

        return versions

    def update_versions(self, reference_resolution):
        """Updates XRef versions with the given reference_resolution.

        The reference_resolution should be a dictionary in the following
        format::

          reference_resolution = {
              'root": [versionLM, versionUM, versionCM, ..., VersionXM],
              'leave': [versionL1, versionL2, ..., versionLN],
              'update': [versionU1, versionU2, ..., versionUN],
              'create': [versionC1, versionC2, ..., versionCN],
          }

        All the references in the 'create' key need to be opened and then the
        all references need to be updated to the latest version and then a new
        :class:`~stalker.models.version.Version` instance will be created for
        each of them, and the newly created versions will be returned.

        The Version instances in 'leave' list will not be touched.

        The Version instances in 'update' list are there because the Version
        instances in 'create' list needs them to be updated. So practically
        these are Versions with already new versions so they will also not be
        touched.

        :param reference_resolution: A dictionary with keys 'leave', 'update'
          or 'create' and values of list of
          :class:`~stalker.models.version.Version` instances.
        :return list: A list of :class:`~stalker.models.version.Version`
          instances if created any.
        """
        # # list only first level references
        # from pymxs import runtime as rt
        # references = sorted([
        #     xref
        #     for xref in rt.objXRefs.getAllXRefObjects()
        #     if not xref.nested
        # ], key=lambda x: x.fileName)
        #
        # # optimize it:
        # #   do only one search for each references to the same version
        # previous_ref_path = None
        # previous_full_path = None
        #
        # for reference in references:
        #     path = reference.fileName
        #     if path == previous_ref_path:
        #         full_path = previous_full_path
        #     else:
        #         version = self.get_version_from_full_path(path)
        #         if version in reference_resolution['update']:
        #             latest_published_version = version.latest_published_version
        #             full_path = latest_published_version.absolute_full_path
        #         else:
        #             full_path = None
        #
        #     if full_path:
        #         reference.srcFileName = full_path
        #
        # self.remove_empty_records()
        #
        # return []  # no new version will be created with the current version

        # list only first level references
        from pymxs import runtime as rt
        record_count = rt.objXRefMgr.recordCount
        references = []
        for i in range(record_count):
            record = rt.objXRefMgr.GetRecord(i + 1)
            if not record.nested:
                references.append(record)

        # optimize it:
        #   do only one search for each references to the same version
        previous_ref_path = None
        previous_full_path = None

        for reference in references:
            path = reference.srcFileName
            if path == previous_ref_path:
                full_path = previous_full_path
            else:
                version = self.get_version_from_full_path(path)
                if version in reference_resolution['update']:
                    latest_published_version = version.latest_published_version
                    full_path = latest_published_version.absolute_full_path
                else:
                    full_path = None

            if full_path:
                reference.srcFileName = full_path

        return []  # no new version will be created with the current version

    @classmethod
    def remove_empty_records(cls):
        """After updating XRef paths, Max will still keep the old XRef as an
        empty record.
        This removes any empty records
        """
        from pymxs import runtime as rt
        record_count = rt.objXRefMgr.recordCount
        print ('record count: %s' % record_count)
        records = []
        for i in range(record_count):
            records.append(rt.objXRefMgr.GetRecord(i + 1))
        for record in records:
            if record.empty:
                rt.objXRefMgr.RemoveRecordFromScene(record)

    @classmethod
    def set_resolution(cls, width, height, pixel_aspect=1.0):
        """Sets the render resolution of this scene

        :param int width: Width of the render in pixels.
        :param int height: Height of the render in pixels.
        :param float pixel_aspect: The pixel aspect ratio. Default is 1.0.
        :return:
        """
        rs = MaxPlus.RenderSettings
        rs.SetWidth(width)
        rs.SetHeight(height)
        rs.SetPixelAspectRatio(pixel_aspect)
        rs.UpdateDialogParameters()

    def set_render_filename(self, version):
        """sets the render file name
        """
        import os
        render_output_folder = os.path.join(
            version.absolute_path,
            'Outputs',
            'renders'
        ).replace("\\", "/")
        version_sig_name = self.get_significant_name(version)

        render_file_full_path = \
            '%(render_output_folder)s/masterLayer/' \
            '%(version_sig_name)s.0000.exr' % \
            {
                'render_output_folder': render_output_folder,
                'version_sig_name': version_sig_name
            }

        rs = MaxPlus.RenderSettings
        # rs.SetTimeType(1)  # Active Time Segment
        rs.SetTimeType(2)  # Range

        # rs.SetUseImageSequence(True)
        rs.SetSaveFile(True)
        rs.SetOutputFile(render_file_full_path)

        # also set any RenderElement to the same path so a MultiPart OpenEXR
        # file is written (saving to a different file is not working for now)
        from pymxs import runtime as rt
        rem = rt.maxOps.GetCurRenderElementMgr()
        if rem:
            num_res = rem.NumRenderElements()
            for i in range(num_res):
                rem.SetRenderElementFilename(i, render_file_full_path)

        rs.UpdateDialogParameters()

        # create the output folder
        import os
        try:
            os.makedirs(
                os.path.dirname(render_file_full_path)
            )
        except OSError:
            # folder already exists
            pass

    def set_frame_range(self, start_frame=0, end_frame=100,
                        adjust_frame_range=False):
        """sets the start and end frame range
        """
        # set the playback range
        anim = MaxPlus.Animation
        ticks_per_frame = anim.GetTicksPerFrame()
        anim.SetStartTime(start_frame * ticks_per_frame)
        anim.SetEndTime(end_frame * ticks_per_frame)

        # and set the render range
        rs = MaxPlus.RenderSettings
        rs.SetTimeType(2)  # Range
        rs.SetStart(start_frame)
        rs.SetEnd(end_frame)

    def get_fps(self):
        """returns the fps of this environment
        """
        anim = MaxPlus.Animation
        return anim.GetFrameRate()

    @classmethod
    def set_fps(cls, fps=25.0):
        """sets the fps of the environment
        """
        anim = MaxPlus.Animation
        anim.SetFrameRate(int(fps))

    def set_project(self, version):
        """Sets the project to the given Versions project.

        :param version: A :class:`~stalker.models.version.Version`.
        """
        project_dir = version.absolute_path
        pm = MaxPlus.PathManager
        pm.SetProjectFolderDir(project_dir)

        # Set all the auxiliary paths
        project_structure = {
            'Animation': 'Outputs/sceneassets/animations',
            'Archives': 'Outputs/archives',
            'Autoback': 'Outputs/autoback',
            'CFD': 'Outputs/sceneassets/CFD',
            'Download': 'Outputs/downloads',
            'Export': 'Outputs/export',
            'Expression': 'Outputs/express',
            'Image': 'Outputs/sceneassets/images',
            'Import': 'Outputs/import',
            'Matlib': 'Outputs/materiallibraries',
            'Photometric': 'Outputs/sceneassets/photometric',
            'Preview': 'Outputs/previews',
            'ProjectFolder': '',
            'Proxies': 'Outputs/proxies',
            'RenderAssets': 'Outputs/sceneassets/renderassets',
            'RenderOutput': 'Outputs/renderoutput',
            'RenderPresets': 'Outputs/renderpresets',
            'Scene': '',
            'Sound': 'Outputs/sceneassets/sounds',
            'UserStartupTemplates': 'Outputs/startuptemplates',
            'Vpost': 'Outputs/vpost',
        }

    def set_system_units(self):
        """Sets the system units to studio defaults. Which is centimeters for
        distance and degree for angular units.

        :return:
        """
        import pymxs
        rt = pymxs.runtime
        metric = rt.name('metric')
        rt.units.SystemType = metric
        rt.units.DisplayType = metric
        rt.units.MetricType = rt.name('centimeters')

    def set_gamma_settings(self, in_=2.2, out=1.0):
        """Sets the system gamma settings

        :param in_: The Bitmap In Gamma. Defaults to 2.2.
        :param out: The Bitmap Out Gamma. Defaults to 1.0.
        :return:
        """
        gamma_mgr = MaxPlus.GammaMgr
        gamma_mgr.SetFileInGamma(in_)
        gamma_mgr.SetFileOutGamma(out)
        gamma_mgr.SetDisplayGamma(2.2)
        gamma_mgr.Enable(True)
