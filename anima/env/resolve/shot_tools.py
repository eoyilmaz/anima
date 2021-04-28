# -*- coding: utf-8 -*-
"""Shot related tools
"""
from anima.ui.base import AnimaDialogBase
from anima.ui.lib import QtCore, QtWidgets


class InjectionManager(object):
    """manager for plate injection process

    Contains the general logic
    """

    def __init__(self, project, sequence):
        self.project = project
        self.sequence = sequence
        self.timeline = self.get_current_timeline()

    @classmethod
    def get_current_shot_code(cls):
        """returns the current shot code
        """
        timeline = cls.get_current_timeline()
        clip = cls.get_current_clip()

        plate_injector = PlateInjector()
        plate_injector.timeline = timeline
        plate_injector.clip = clip
        return plate_injector.shot_code

    @classmethod
    def get_current_clip(cls):
        timeline = cls.get_current_timeline()
        clip = timeline.GetCurrentVideoItem()
        return clip

    @classmethod
    def get_current_timeline(cls):
        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()
        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()
        return timeline

    @classmethod
    def set_current_shot_code(cls, shot_code):
        """sets the current shot code

        :param str shot_code: The desired shot code
        """
        timeline = cls.get_current_timeline()

        plate_injector = PlateInjector()
        plate_injector.clip = timeline.GetCurrentVideoItem()
        plate_injector.set_shot_code(shot_code)

    def get_clip_list(self):
        """returns the clips
        """
        timeline = self.get_current_timeline()
        clips = timeline.GetItemListInTrack('video', 1)
        return clips

    def get_shots(self):
        """returns the shots in the current video track
        """
        shots = []
        clips = self.get_clip_list()
        for clip in clips:
            pi = PlateInjector(project=self.project, sequence=self.sequence, clip=clip, timeline=self.timeline)
            if pi.is_shot():
                shots.append(pi)
        return shots

    def check_duplicate_shots(self):
        """checks for duplicate shots
        """
        shot_list = self.get_shots()
        shot_codes = []
        for shot in shot_list:
            shot_codes.append(shot.shot_code)
        shot_codes = sorted(shot_codes)
        unique_shot_codes = sorted(list(set(shot_codes)))
        duplicate_shot_codes = []
        if len(unique_shot_codes) != len(shot_codes):
            # find duplicate shot names
            prev_shot_code = ''
            for shot_code in shot_codes:
                current_shot_code = shot_code
                if current_shot_code == prev_shot_code:
                    duplicate_shot_codes.append(current_shot_code)
                prev_shot_code = current_shot_code

        return duplicate_shot_codes

    def validate_shot_codes(self):
        """validate shot codes
        """
        shots = self.get_shots()
        invalid_shots = []
        for shot in shots:
            try:
                shot.validate_shot_code()
            except ValueError:
                invalid_shots.append(shot)

        return invalid_shots

    def get_thumbnail(cls):
        """returns the current media thumbnail
        """
        timeline = cls.get_current_timeline()

        plate_injector = PlateInjector()
        plate_injector.timeline = timeline
        plate_injector.clip = timeline.GetCurrentVideoItem()
        thumbnail = plate_injector.update_shot_thumbnail()
        return thumbnail


class PlateInjector(object):
    """Renders plates for the given clip

    Generates render jobs that renders the VFX related clips in the current
    timeline to their respective shot folder.
    """

    def __init__(self, project=None, sequence=None, clip=None, timeline=None):
        self.project = project
        self.sequence = sequence
        self.timeline = timeline
        self.clip = clip
        self._shot_code = None

    def create_shot(self):
        """creates the related shot
        """
        from stalker import Shot, Task
        from stalker.db.session import DBSession
        shot = Shot.query.filter(Shot.project==self.project).filter(Shot.code==self.shot_code).first()
        if not shot:
            # create the shot

            logged_in_user = self.get_logged_in_user()

            # FP001_001_0010
            scene_code = self.shot_code.split("_")[1]
            scene_task = Task.query.filter(Task.parent==self.sequence).filter(Task.name.contains(scene_code)).first()

            if not scene_task:
                # create the scene task
                scene_task = Task(
                    project=self.project,
                    name='SCN%s' % scene_code,
                    parent=self.sequence,
                    description='Autocreated by PlateInjector',
                    created_by=logged_in_user,
                    updated_by=logged_in_user,
                )
                DBSession.add(scene_task)
                DBSession.commit()

            shots_task = Task.query.filter(Task.parent==scene_task).filter(Task.name=='Shots').first()
            if not shots_task:
                shots_task = Task(
                    project=self.project,
                    name='Shots',
                    parent=scene_task,
                    description='Autocreated by PlateInjector',
                    created_by=logged_in_user,
                    updated_by=logged_in_user,
                )
                DBSession.add(shots_task)
                DBSession.commit()

            shot = Shot(
                name=self.shot_code,
                code=self.shot_code,
                project=self.project,
                parent=shots_task,
                sequences=[self.sequence],
                cut_in=1001,
                cut_out=self.clip.GetEnd() - self.clip.GetStart() + 1000,
                description='Autocreated by PlateInjector',
                created_by=logged_in_user,
                updated_by=logged_in_user,
            )
            DBSession.add(shot)

            # creat shot tasks
            # Anim
            anim_task = Task(
                name='Anim',
                parent=shot,
                type=self.get_type('Animation'),
                bid_timing=10,
                bid_unit='min',
                created_by=logged_in_user,
                updated_by=logged_in_user,
            )
            DBSession.add(anim_task)

            # Camera
            camera_task = Task(
                name='Camera',
                parent=shot,
                type=self.get_type('Camera'),
                bid_timing=10,
                bid_unit='min',
                created_by=logged_in_user,
                updated_by=logged_in_user,
            )
            DBSession.add(camera_task)

            # Cleanup
            cleanup_task = Task(
                name='Cleanup',
                parent=shot,
                type=self.get_type('Comp'),
                bid_timing=10,
                bid_unit='min',
                created_by=logged_in_user,
                updated_by=logged_in_user,
            )
            DBSession.add(cleanup_task)

            # Comp
            comp_task = Task(
                name='Comp',
                parent=shot,
                type=self.get_type('Comp'),
                bid_timing=10,
                bid_unit='min',
                created_by=logged_in_user,
                updated_by=logged_in_user,
            )
            DBSession.add(comp_task)

            # Lighting
            lighting_task = Task(
                name='Lighting',
                parent=shot,
                type=self.get_type('Lighting'),
                bid_timing=10,
                bid_unit='min',
                created_by=logged_in_user,
                updated_by=logged_in_user,
            )
            DBSession.add(lighting_task)

            # Plate
            plate_task = Task(
                name='Plate',
                parent=shot,
                type=self.get_type('Plate'),
                bid_timing=10,
                bid_unit='min',
                created_by=logged_in_user,
                updated_by=logged_in_user,
            )
            DBSession.add(plate_task)

            # add dependency relation
            camera_task.depends = [plate_task]
            anim_task.depends = [camera_task]
            lighting_task.depends = [anim_task]
            cleanup_task.depends = [plate_task]
            comp_task.depends = [lighting_task, cleanup_task]

            DBSession.commit()

        return shot

    def update_shot_thumbnail(self):
        """updates the shot thumbnail from resolve
        """
        # go to the color page to retrieve the thumbnail
        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()
        resolve.OpenPage('color')
        current_media_thumbnail = self.timeline.GetCurrentClipThumbnailImage()
        resolve.OpenPage('edit')

        from PIL import Image
        from io import BytesIO
        import base64
        im = Image.open(BytesIO(base64.b64decode(current_media_thumbnail['data'])))

        with open('/home/eoyilmaz/resolve_raw_thumbnail_data', 'w+') as f:
            f.write(current_media_thumbnail['data'])

        import tempfile
        thumbnail_path = tempfile.mktemp(suffix='.jpg')
        print('thumbnail_path: %s' % thumbnail_path)
        im.save(thumbnail_path, quality=85)

        return current_media_thumbnail

    @classmethod
    def get_logged_in_user(cls):
        """returns the logged in user
        """
        # get logged in user
        from stalker import LocalSession
        from stalker.db.session import DBSession

        local_session = LocalSession()
        with DBSession.no_autoflush:
            logged_in_user = local_session.logged_in_user

        if not logged_in_user:
            raise RuntimeError("Please login first!")

        return logged_in_user

    def get_type(self, type_name):
        """returns the Stalker Type instance with the given name, if the type doesn't exist it will create it

        :param str type_name: Type queried type name

        :return:
        """
        from stalker import Type
        type_instance = Type.query.filter(Type.name==type_name).first()
        if not type_instance:
            logged_in_user = self.get_logged_in_user()
            type_instance = Type(
                entity_type='Task',
                name=type_name,
                created_by=logged_in_user,
                updated_by=logged_in_user
            )
            from stalker.db.session import DBSession
            DBSession.add(type_instance)
            DBSession.commit()
        return type_instance

    def create_render_job(self):
        """creates render job for the clip
        """
        # create a new render output for each clip
        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()

        template_name = "PlateInjector"
        result = proj.LoadRenderPreset(template_name)
        if not result:
            print("No template named: %s" % template_name)
        else:
            print("Template loaded successfully: %s" % template_name)

        # get the shot
        from stalker import Task, Shot, Type
        shot = Shot.query.filter(Shot.project==self.project).filter(Shot.code==self.shot_code).first()
        if not shot:
            # raise RuntimeError("No shot with code: %s" % self.shot_code)
            shot = self.create_shot()

        # get plate task
        plate_type = Type.query.filter(Type.name=='Plate').first()
        if not plate_type:
            raise RuntimeError("No plate type!!!")

        plate_task = Task.query.filter(Task.parent==shot).filter(Task.type==plate_type).first()
        if not plate_task:
            raise RuntimeError("No plate task in shot: %s" % self.shot_code)

        proj.SetCurrentRenderFormatAndCodec('exr', 'RGBHalfZIP')

        proj.SetRenderSettings({
            'MarkIn': self.clip.GetStart(),
            'MarkOut': self.clip.GetEnd() - 1,
            'CustomName': '%s_Main_v001.' % self.shot_code,
            'TargetDir': '%s/Outputs/Main/v001/exr' % plate_task.absolute_path
        })
        proj.SetCurrentRenderMode(1)
        proj.AddRenderJob()

    def get_shot_related_marker(self):
        """returns the shot related marker data
        """
        clip_start_frame = self.clip.GetStart()
        timeline_start_frame = self.timeline.GetStartFrame()
        markers = self.timeline.GetMarkers()
        if markers:
            keys = markers.keys()
            frame_id = clip_start_frame - timeline_start_frame
            try:
                marker = markers[frame_id]
            except KeyError:
                return None

            marker['frameId'] = frame_id
            return marker

    def is_shot(self):
        """returns True if this is a shot clip
        """
        if self.shot_code:
            return True
        else:
            return False

    @property
    def shot_code(self):
        """Returns the shot code of the given clip

        :return:
        """
        if not self._shot_code:
            marker = self.get_shot_related_marker()
            if marker:
                self._shot_code = marker['note']

        return self._shot_code

    @shot_code.setter
    def shot_code(self, shot_code):
        """Sets the shot code of the given clip

        :return:
        """
        self._shot_code = None
        marker = self.get_shot_related_marker()

        if marker:
            self.timeline.DeleteMarkerAtFrame(marker['frameId'])

        # create a new marker
        result = self.timeline.AddMarker(
            frameId=self.clip.GetStart() - self.timeline.GetStartFrame(),
            color='Blue',
            name='Marker 1',
            note=shot_code,
            duration=1,
        )

        print("result: %s" % result)

    def validate_shot_code(self):
        """validates the shot code
        """
        import re
        regex = re.compile(r"([\w]+)_(\d{3})_(\d{3}[A-Z]{0,1})_(\d{4})")

        shot_code = self.shot_code
        match = regex.match(shot_code)
        if not match:
            raise ValueError("Shot code format is not valid: %s" % shot_code)


class PlateInjectorUI(QtWidgets.QDialog, AnimaDialogBase):
    """The UI for the PlateInjector
    """

    def __init__(self, *args, **kwargs):
        super(PlateInjectorUI, self).__init__(*args, **kwargs)
        self.main_layout = None
        self.form_layout = None
        self.project_combo_box = None
        self.sequence_combo_box = None
        self.setup_ui()

    def setup_ui(self):
        """sets the ui up
        """
        from anima.utils import do_db_setup
        do_db_setup()

        # get logged in user
        self.get_logged_in_user()

        self.setWindowTitle("Plate Injector")

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.form_layout = QtWidgets.QFormLayout(self)
        self.main_layout.addLayout(self.form_layout)

        i = 0
        # Project
        label = QtWidgets.QLabel(self)
        label.setText("Project")
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            label
        )

        from anima.ui.widgets.project import ProjectComboBox
        self.project_combo_box = ProjectComboBox(self)
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.project_combo_box
        )

        # Sequence
        i += 1
        label = QtWidgets.QLabel(self)
        label.setText("Sequence")
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            label
        )

        from anima.ui.widgets.sequence import SequenceComboBox
        self.sequence_combo_box = SequenceComboBox(self)
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.sequence_combo_box
        )

        # Get Shot List button
        get_shot_list_push_button = QtWidgets.QPushButton(self)
        get_shot_list_push_button.setText("Get Shot List")
        self.main_layout.addWidget(get_shot_list_push_button)

        # Check Duplicate Shot Code
        validate_shots_push_button = QtWidgets.QPushButton(self)
        validate_shots_push_button.setText("Validate Shots")
        self.main_layout.addWidget(validate_shots_push_button)

        # Check Duplicate Shot Code
        check_duplicate_shot_code_push_button = QtWidgets.QPushButton(self)
        check_duplicate_shot_code_push_button.setText("Check Duplicate Shot Code")
        self.main_layout.addWidget(check_duplicate_shot_code_push_button)

        # Create Render Jobs button
        create_render_jobs_button = QtWidgets.QPushButton(self)
        create_render_jobs_button.setText("Create Render Jobs")
        self.main_layout.addWidget(create_render_jobs_button)

        # Ok button
        ok_button = QtWidgets.QPushButton(self)
        ok_button.setText("OK")
        self.main_layout.addWidget(ok_button)

        # Signals
        self.project_changed(None)

        QtCore.QObject.connect(
            self.project_combo_box,
            QtCore.SIGNAL("currentIndexChanged(QString)"),
            self.project_changed
        )

        QtCore.QObject.connect(
            ok_button,
            QtCore.SIGNAL("clicked()"),
            self.close
        )

        QtCore.QObject.connect(
            create_render_jobs_button,
            QtCore.SIGNAL("clicked()"),
            self.create_render_jobs
        )

        QtCore.QObject.connect(
            get_shot_list_push_button,
            QtCore.SIGNAL("clicked()"),
            self.get_shot_list
        )

        QtCore.QObject.connect(
            check_duplicate_shot_code_push_button,
            QtCore.SIGNAL("clicked()"),
            self.check_duplicate_shots
        )

        QtCore.QObject.connect(
            validate_shots_push_button,
            QtCore.SIGNAL("clicked()"),
            self.validate_shot_codes
        )

    def project_changed(self, index):
        """runs when the current selected project has been changed
        """
        self.sequence_combo_box.project = self.project_combo_box.get_current_project()

    def get_shot_list(self):
        """just prints the shot names
        """
        project = self.project_combo_box.get_current_project()
        sequence = self.sequence_combo_box.get_current_sequence()
        im = InjectionManager(project, sequence)
        for shot in im.get_shots():
            isinstance(shot, PlateInjector)
            print(shot.shot_code)

    def create_render_jobs(self):
        """creates render jobs
        """
        # first check duplicate shots
        if not self.check_duplicate_shots():
            return

        if not self.validate_shot_codes():
            return

        project = self.project_combo_box.get_current_project()
        sequence = self.sequence_combo_box.get_current_sequence()
        im = InjectionManager(project, sequence)

        try:
            for shot in im.get_shots():
                isinstance(shot, PlateInjector)
                shot.create_render_job()
        except BaseException as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                str(e)
            )
            raise e
        finally:
            QtWidgets.QMessageBox.information(
                self,
                "Created Shots and Render Jobs 👍",
                "Created Shots and Render Jobs 👍"
            )

    def validate_shot_codes(self):
        """validates the shot codes
        """
        project = self.project_combo_box.get_current_project()
        sequence = self.sequence_combo_box.get_current_sequence()
        im = InjectionManager(project, sequence)
        invalid_shots = im.validate_shot_codes()
        invalid_shot_codes = []
        for shot in invalid_shots:
            invalid_shot_codes.append(shot.shot_code)

        if invalid_shot_codes:
            QtWidgets.QMessageBox.critical(
                self,
                "Invalid shot names!!!",
                "There are invalid shot codes:<br>%s" % "<br>".join(invalid_shot_codes)
            )
            return False
        else:
            QtWidgets.QMessageBox.information(
                self,
                "All shots valid 👍",
                "All shots valid 👍"
            )
            return True

    def check_duplicate_shots(self):
        """checks for duplicate shot code
        """
        project = self.project_combo_box.get_current_project()
        sequence = self.sequence_combo_box.get_current_sequence()
        im = InjectionManager(project, sequence)
        duplicate_shot_codes = im.check_duplicate_shots()
        if duplicate_shot_codes:
            QtWidgets.QMessageBox.critical(
                self,
                "Duplicate Shot Codes!!!",
                "There are duplicate shot codes:<br>%s" % "<br>".join(duplicate_shot_codes)
            )
            return False
        else:
            QtWidgets.QMessageBox.information(
                self,
                "No Duplicate Shots 👍",
                "No duplicate shots 👍"
            )
            return True
