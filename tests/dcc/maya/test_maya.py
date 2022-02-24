# -*- coding: utf-8 -*-

import logging

import os
import shutil
import tempfile

import unittest

# prepare for test
import anima.dcc.mayaEnv.reference

os.environ['ANIMA_TEST_SETUP'] = ""

import pymel.core as pm

from stalker import (db, Project, Repository, StatusList, Status, Asset, Shot,
                     Task, Sequence, Version, User, Type, Structure,
                     FilenameTemplate, ImageFormat)
from stalker.db.session import DBSession

from anima import utils
from anima import publish
from anima.dcc.mayaEnv import Maya
from anima.dcc.mayaEnv.archive import Archiver
from anima.dcc.mayaEnv.repr_tools import Representation, RepresentationGenerator


class MayaTestBase(unittest.TestCase):
    """The base class for Maya Tests
    """

    def create_version(self, task, take_name, parent=None):
        """A helper method for creating a new version

        :param task: the task
        :param take_name: the take_name name
        :return: the version
        """
        # just renew the scene
        pm.newFile(force=True)

        if parent:
            self.maya_env.open(parent, force=True)

        v = Version(task=task, take_name=take_name)

        DBSession.add(v)
        self.maya_env.save_as(v)

        return v

    @classmethod
    def setUpClass(cls):
        """setup in class level
        """
        import logging
        logger = logging.getLogger('anima.dcc.mayaEnv')
        logger.setLevel(logging.DEBUG)

        import anima
        anima.stalker_server_internal_address = 'internal'
        anima.stalker_server_external_address = 'external'

    def setUp(self):
        """setup the tests
        """
        import logging
        logger = logging.getLogger('anima.dcc.mayaEnv')
        logger.setLevel(logging.DEBUG)

        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        logger.debug("initializing db")
        database_url = "sqlite:///:memory:"
        db.setup({'sqlalchemy.url': database_url})
        db.init()
        logger.debug("initializing db complete")

        logger.debug("creating temp repository path")
        self.temp_repo_path = tempfile.mkdtemp()

        logger.debug("creating user1")
        self.user1 = User(
            name='User 1',
            login='user1',
            email='user1@users.com',
            password='12345'
        )

        logger.debug("creating repo1")
        self.repo1 = Repository(
            name='Test Project Repository',
            code='TPR',
            linux_path=self.temp_repo_path,
            windows_path=self.temp_repo_path,
            osx_path=self.temp_repo_path
        )
        logger.debug("commiting repo1")
        DBSession.add(self.repo1)
        DBSession.commit()
        logger.debug("commit repo1 done!")

        logger.debug("creating statuses")
        self.status_new = Status.query.filter_by(code='NEW').first()
        self.status_wip = Status.query.filter_by(code='WIP').first()
        self.status_comp = Status.query.filter_by(code='CMPL').first()
        logger.debug("creating statuses done")

        logger.debug("creating filename template")
        self.task_template = FilenameTemplate(
            name='Task Template',
            target_entity_type='Task',
            path='$REPO{{project.repository.code}}/{{project.code}}/'
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )
        logger.debug("creating filename template done")

        logger.debug("creating asset template")
        self.asset_template = FilenameTemplate(
            name='Asset Template',
            target_entity_type='Asset',
            path='$REPO{{project.repository.code}}/{{project.code}}/'
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )
        logger.debug("creating asset template done")

        logger.debug("creating shot template")
        self.shot_template = FilenameTemplate(
            name='Shot Template',
            target_entity_type='Shot',
            path='$REPO{{project.repository.code}}/{{project.code}}/'
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )
        logger.debug("creating shot template done")

        self.sequence_template = FilenameTemplate(
            name='Sequence Template',
            target_entity_type='Sequence',
            path='$REPO{{project.repository.code}}/{{project.code}}/'
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.structure = Structure(
            name='Project Struture',
            templates=[self.task_template, self.asset_template,
                       self.shot_template, self.sequence_template]
        )

        self.project_status_list = \
            StatusList.query.filter_by(target_entity_type='Project').first()

        self.image_format = ImageFormat(
            name='HD 1080',
            width=1920,
            height=1080,
            pixel_aspect=1.0
        )

        # create a test project
        self.project = Project(
            name='Test Project',
            code='TP',
            repositories=[self.repo1],
            status_list=self.project_status_list,
            structure=self.structure,
            image_format=self.image_format
        )
        DBSession.add(self.project)
        DBSession.commit()

        self.task_status_list =\
            StatusList.query.filter_by(target_entity_type='Task').first()
        self.asset_status_list =\
            StatusList.query.filter_by(target_entity_type='Asset').first()
        self.shot_status_list =\
            StatusList.query.filter_by(target_entity_type='Shot').first()
        self.sequence_status_list =\
            StatusList.query.filter_by(target_entity_type='Sequence').first()

        self.character_type = Type(
            name='Character',
            code='CHAR',
            target_entity_type='Asset'
        )

        # create a test series of root task
        self.task1 = Task(
            name='Test Task 1',
            project=self.project
        )
        self.task2 = Task(
            name='Test Task 2',
            project=self.project
        )
        self.task3 = Task(
            name='Test Task 3',
            project=self.project
        )

        # then a couple of child tasks
        self.task4 = Task(
            name='Test Task 4',
            parent=self.task1
        )
        self.task5 = Task(
            name='Test Task 5',
            parent=self.task1,
        )
        self.task6 = Task(
            name='Test Task 6',
            parent=self.task1,
        )

        # create a root asset
        self.asset1 = Asset(
            name='Asset 1',
            code='asset1',
            type=self.character_type,
            project=self.project
        )

        # create a child asset
        self.asset2 = Asset(
            name='Asset 2',
            code='asset2',
            type=self.character_type,
            parent=self.task4
        )

        # create a root Sequence
        self.sequence1 = Sequence(
            name='Sequence1',
            code='SEQ1',
            project=self.project
        )

        # create a child Sequence
        self.sequence2 = Sequence(
            name='Sequence2',
            code='SEQ2',
            parent=self.task2
        )

        # create a root Shot
        self.shot1 = Shot(
            code='SH001',
            project=self.project
        )

        # create a child Shot (child of a Sequence)
        self.shot2 = Shot(
            code='SH002',
            parent=self.sequence1
        )

        # create a child Shot (child of a child Sequence)
        self.shot3 = Shot(
            code='SH003',
            parent=self.sequence2
        )

        # ******************************************************************
        #
        # Lets create some real data
        #
        # ******************************************************************

        # Types
        self.character_design_type = Type(
            name='Character Design',
            code='chardesign',
            target_entity_type='Task'
        )

        self.model_type = Type(
            name='Model',
            code='model',
            target_entity_type='Task'
        )

        self.look_development_type = Type(
            name='Look Development',
            code='lookdev',
            target_entity_type='Task'
        )

        self.rig_type = Type(
            name='Rig',
            code='rig',
            target_entity_type='Task'
        )

        self.exterior_type = Type(
            name='Exterior',
            code='rig',
            target_entity_type='Asset'
        )

        self.building_type = Type(
            name='Building',
            code='building',
            target_entity_type='Asset'
        )

        self.layout_type = Type(
            name='Layout',
            code='layout',
            target_entity_type='Task'
        )

        self.prop_type = Type(
            name='Prop',
            code='prop',
            target_entity_type='Asset'
        )

        self.vegetation_type = Type(
            name='Vegetation',
            code='vegetation',
            target_entity_type='Task'
        )

        # Tasks
        self.assets = Task(
            name='Assets',
            project=self.project
        )

        self.characters = Task(
            name='Characters',
            parent=self.assets
        )

        self.char1 = Asset(
            name='Char1',
            code='Char1',
            type=self.character_type,
            parent=self.characters
        )

        self.character_design = Task(
            name='Character Design',
            type=self.character_design_type,
            parent=self.char1
        )

        self.char1_model = Task(
            name='Model',
            parent=self.char1,
            type=self.model_type,
            depends=[self.character_design]
        )

        self.char1_look_dev = Task(
            name='Look Dev',    # this is named Look Dev instead of LookDev on
            parent=self.char1,  # purpose
            type=self.look_development_type,
            depends=[self.char1_model]
        )

        self.char1_rig = Task(
            name='Rig',    # this is named Look Dev instead of LookDev on
            parent=self.char1,  # purpose
            type=self.rig_type,
            depends=[self.char1_model]
        )

        self.environments = Task(
            name='Environments',
            parent=self.assets
        )

        self.exteriors = Task(
            name='Exteriors',
            parent=self.environments
        )

        self.ext1 = Asset(
            name='Ext1',
            code='Ext1',
            type=self.exterior_type,
            parent=self.exteriors
        )

        # Building 1
        self.building1 = Asset(
            name='Building1',
            code='Building1',
            type=self.building_type,
            parent=self.ext1
        )

        self.building1_layout = Task(
            name='Layout',
            type=self.layout_type,
            parent=self.building1
        )

        self.building1_layout_proxy = Task(
            name='Proxy',
            type=self.layout_type,
            parent=self.building1_layout
        )

        self.building1_layout_hires = Task(
            name='Hires',
            type=self.layout_type,
            parent=self.building1_layout,
            depends=[self.building1_layout_proxy]
        )

        self.building1_look_dev = Task(
            name='LookDev',
            type=self.look_development_type,
            parent=self.building1
        )

        self.building1_props = Task(
            name='Props',
            parent=self.building1
        )

        self.building1_yapi = Task(
            name='YAPI',
            parent=self.building1_props
        )

        self.building1_yapi_model = Task(
            name='Model',
            type=self.model_type,
            parent=self.building1_yapi
        )

        self.building1_yapi_model_proxy = Task(
            name='Proxy',
            type=self.model_type,
            parent=self.building1_yapi_model
        )

        self.building1_yapi_model_hires = Task(
            name='Hires',
            type=self.model_type,
            parent=self.building1_yapi_model
        )

        self.building1_yapi_look_dev = Task(
            name='LookDev',
            type=self.look_development_type,
            parent=self.building1_yapi,
            depends=[self.building1_yapi_model_hires]
        )

        self.building1_layout_proxy.depends.append(
            self.building1_yapi_model_proxy
        )

        self.building1_layout_hires.depends.append(
            self.building1_yapi_model_hires
        )

        # Building 2
        self.building2 = Asset(
            name='Building2',
            code='Building2',
            type=self.building_type,
            parent=self.ext1
        )

        self.building2_layout = Task(
            name='Layout',
            type=self.layout_type,
            parent=self.building2
        )

        self.building2_layout_proxy = Task(
            name='Proxy',
            type=self.layout_type,
            parent=self.building2_layout
        )

        self.building2_layout_hires = Task(
            name='Hires',
            type=self.layout_type,
            parent=self.building2_layout,
            depends=[self.building2_layout_proxy]
        )

        self.building2_look_dev = Task(
            name='LookDev',
            type=self.look_development_type,
            parent=self.building2
        )

        self.building2_props = Task(
            name='Props',
            parent=self.building2
        )

        self.building2_yapi = Task(
            name='YAPI',
            parent=self.building2_props
        )

        self.building2_yapi_model = Task(
            name='Model',
            type=self.model_type,
            parent=self.building2_yapi
        )

        self.building2_yapi_model_proxy = Task(
            name='Proxy',
            type=self.model_type,
            parent=self.building2_yapi_model
        )

        self.building2_yapi_model_hires = Task(
            name='Hires',
            type=self.model_type,
            parent=self.building2_yapi_model
        )

        self.building2_yapi_look_dev = Task(
            name='LookDev',
            type=self.look_development_type,
            parent=self.building2_yapi,
            depends=[self.building2_yapi_model_hires]
        )

        self.building2_layout_proxy.depends.append(
            self.building2_yapi_model_proxy
        )

        self.building2_layout_hires.depends.append(
            self.building2_yapi_model_hires
        )

        # continue to ext1 layout
        self.ext1_layout = Task(
            name='Layout',
            type=self.layout_type,
            parent=self.ext1
        )

        self.ext1_layout_proxy = Task(
            name='Proxy',
            type=self.layout_type,
            parent=self.ext1_layout
        )

        self.ext1_layout_hires = Task(
            name='Hires',
            type=self.layout_type,
            parent=self.ext1_layout,
            depends=[self.ext1_layout_proxy]
        )

        self.ext1_look_dev = Task(
            name='LookDev',
            type=self.look_development_type,
            parent=self.ext1,
            depends=[self.ext1_layout]
        )

        self.ext1_props = Task(
            name='Props',
            parent=self.ext1
        )

        self.prop1 = Asset(
            name='Prop1',
            code='Prop1',
            type=self.prop_type,
            parent=self.ext1_props
        )

        self.prop1_model = Task(
            name='Model',
            type=self.model_type,
            parent=self.prop1
        )

        self.prop1_model_proxy = Task(
            name='Proxy',
            type=self.model_type,
            parent=self.prop1_model
        )

        self.prop1_model_hires = Task(
            name='Hires',
            type=self.model_type,
            parent=self.prop1_model,
            depends=[self.prop1_model_proxy]
        )

        self.prop1_look_dev = Task(
            name='LookDev',
            type=self.look_development_type,
            parent=self.prop1
        )

        # and finally vegetation
        self.ext1_vegetation = Task(
            name='Vegetation',
            parent=self.ext1,
            type=self.vegetation_type
        )

        # commit everything
        DBSession.add_all([
            self.repo1, self.status_new, self.status_wip, self.status_comp,
            self.project_status_list, self.project, self.task_status_list,
            self.asset_status_list, self.shot_status_list,
            self.sequence_status_list, self.task1, self.task2, self.task3,
            self.task4, self.task5, self.task6, self.asset1, self.asset2,
            self.shot1, self.shot2, self.shot3, self.sequence1, self.sequence2,
            self.task_template, self.asset_template, self.shot_template,
            self.sequence_template,

            self.character_design_type, self.model_type,
            self.look_development_type, self.rig_type, self.exterior_type,
            self.building_type, self.layout_type, self.prop_type,
            self.vegetation_type, self.assets, self.characters, self.char1,
            self.character_design, self.char1_model, self.char1_look_dev,
            self.char1_rig, self.environments, self.exteriors, self.ext1,

            self.building1, self.building1_layout, self.building1_layout_proxy,
            self.building1_layout_hires, self.building1_look_dev,
            self.building1_props, self.building1_yapi,
            self.building1_yapi_model, self.building1_yapi_model_proxy,
            self.building1_yapi_model_hires, self.building1_yapi_look_dev,

            self.building2, self.building2_layout, self.building2_layout_proxy,
            self.building2_layout_hires, self.building2_look_dev,
            self.building2_props, self.building2_yapi,
            self.building2_yapi_model, self.building2_yapi_model_proxy,
            self.building2_yapi_model_hires, self.building2_yapi_look_dev,

            self.ext1_layout, self.ext1_layout_proxy, self.ext1_layout_hires,
            self.ext1_look_dev, self.ext1_props, self.prop1, self.prop1_model,
            self.prop1_model_proxy, self.prop1_model_hires,
            self.prop1_look_dev, self.ext1_vegetation
        ])
        DBSession.commit()

        # create the environment instance
        self.maya_env = Maya()
        self.maya_env.use_progress_window = False

        # asset2
        self.version1 = self.create_version(self.asset2, 'Main')
        self.version2 = self.create_version(self.asset2, 'Main')
        self.version3 = self.create_version(self.asset2, 'Main')

        self.version4 = self.create_version(self.asset2, 'Take1')
        self.version5 = self.create_version(self.asset2, 'Take1')
        self.version6 = self.create_version(self.asset2, 'Take1')

        # task5
        self.version7 = self.create_version(self.task5, 'Main')
        self.version8 = self.create_version(self.task5, 'Main')
        self.version9 = self.create_version(self.task5, 'Main')

        self.version10 = self.create_version(self.task5, 'Take1')
        self.version11 = self.create_version(self.task5, 'Take1')
        self.version12 = self.create_version(self.task5, 'Take1')

        # task6
        self.version13 = self.create_version(self.task6, 'Main')
        self.version14 = self.create_version(self.task6, 'Main')
        self.version15 = self.create_version(self.task6, 'Main')

        self.version16 = self.create_version(self.task6, 'Take1')
        self.version17 = self.create_version(self.task6, 'Take1')
        self.version18 = self.create_version(self.task6, 'Take1')

        # shot3
        self.version19 = self.create_version(self.shot3, 'Main')
        self.version20 = self.create_version(self.shot3, 'Main')
        self.version21 = self.create_version(self.shot3, 'Main')

        self.version22 = self.create_version(self.shot3, 'Take1')
        self.version23 = self.create_version(self.shot3, 'Take1')
        self.version24 = self.create_version(self.shot3, 'Take1')

        # task3
        self.version25 = self.create_version(self.task3, 'Main')
        self.version26 = self.create_version(self.task3, 'Main')
        self.version27 = self.create_version(self.task3, 'Main')

        self.version28 = self.create_version(self.task3, 'Take1')
        self.version29 = self.create_version(self.task3, 'Take1')
        self.version30 = self.create_version(self.task3, 'Take1')

        # asset1
        self.version31 = self.create_version(self.asset1, 'Main')
        self.version32 = self.create_version(self.asset1, 'Main')
        self.version33 = self.create_version(self.asset1, 'Main')

        self.version34 = self.create_version(self.asset1, 'Take1')
        self.version35 = self.create_version(self.asset1, 'Take1')
        self.version36 = self.create_version(self.asset1, 'Take1')

        # shot2
        self.version37 = self.create_version(self.shot2, 'Main')
        self.version38 = self.create_version(self.shot2, 'Main')
        self.version39 = self.create_version(self.shot2, 'Main')

        self.version40 = self.create_version(self.shot2, 'Take1')
        self.version41 = self.create_version(self.shot2, 'Take1')
        self.version42 = self.create_version(self.shot2, 'Take1')

        # shot1
        self.version43 = self.create_version(self.shot1, 'Main')
        self.version44 = self.create_version(self.shot1, 'Main')
        self.version45 = self.create_version(self.shot1, 'Main')

        self.version46 = self.create_version(self.shot1, 'Take1')
        self.version47 = self.create_version(self.shot1, 'Take1')
        self.version48 = self.create_version(self.shot1, 'Take1')

        # Reflected Data
        # Char1 - Character Design
        self.version49 = self.create_version(self.character_design, 'Main')
        self.version50 = self.create_version(self.character_design, 'Main')
        self.version51 = self.create_version(self.character_design, 'Main')

        # Char1 - Model
        self.version52 = self.create_version(self.char1_model, 'Main')
        self.version53 = self.create_version(self.char1_model, 'Main')
        self.version54 = self.create_version(self.char1_model, 'Main')

        # Char1 - Look Dev
        self.version55 = self.create_version(self.char1_look_dev, 'Main')
        self.version56 = self.create_version(self.char1_look_dev, 'Main')
        self.version57 = self.create_version(self.char1_look_dev, 'Main')

        # Char1 - Rig
        self.version58 = self.create_version(self.char1_rig, 'Main')
        self.version59 = self.create_version(self.char1_rig, 'Main')
        self.version60 = self.create_version(self.char1_rig, 'Main')

        # Building1
        # Building1 - Layout - Proxy
        self.version61 = self.create_version(self.building1_layout_proxy, 'Main')
        self.version62 = self.create_version(self.building1_layout_proxy, 'Main')
        self.version63 = self.create_version(self.building1_layout_proxy, 'Main')

        # Building1 - Layout - Hires
        self.version64 = self.create_version(self.building1_layout_hires, 'Main')
        self.version65 = self.create_version(self.building1_layout_hires, 'Main')
        self.version66 = self.create_version(self.building1_layout_hires, 'Main')

        # Building1 - LookDev
        self.version67 = self.create_version(self.building1_look_dev, 'Main')
        self.version68 = self.create_version(self.building1_look_dev, 'Main')
        self.version69 = self.create_version(self.building1_look_dev, 'Main')

        # Building1 | Props | Yapi | Model | Proxy
        self.version70 = self.create_version(self.building1_yapi_model_proxy, 'Main')
        self.version71 = self.create_version(self.building1_yapi_model_proxy, 'Main')
        self.version72 = self.create_version(self.building1_yapi_model_proxy, 'Main')

        # Building1 | Props | Yapi | Model | Hires
        self.version73 = self.create_version(self.building1_yapi_model_hires, 'Main')
        self.version74 = self.create_version(self.building1_yapi_model_hires, 'Main')
        self.version75 = self.create_version(self.building1_yapi_model_hires, 'Main')

        # Building1 | Props | Yapi | LookDev
        self.version76 = self.create_version(self.building1_yapi_look_dev, 'Main')
        self.version77 = self.create_version(self.building1_yapi_look_dev, 'Main')
        self.version78 = self.create_version(self.building1_yapi_look_dev, 'Main')

        # Building2 | Layout | Proxy
        self.version79 = self.create_version(self.building2_layout_proxy, 'Main')
        self.version80 = self.create_version(self.building2_layout_proxy, 'Main')
        self.version81 = self.create_version(self.building2_layout_proxy, 'Main')

        # Building2 | Layout | Hires
        self.version82 = self.create_version(self.building2_layout_hires, 'Main')
        self.version83 = self.create_version(self.building2_layout_hires, 'Main')
        self.version84 = self.create_version(self.building2_layout_hires, 'Main')

        # Building2 | LookDev
        self.version85 = self.create_version(self.building2_look_dev, 'Main')
        self.version86 = self.create_version(self.building2_look_dev, 'Main')
        self.version87 = self.create_version(self.building2_look_dev, 'Main')

        # Building2 | Props | Yapi | Model | Proxy
        self.version88 = self.create_version(self.building2_yapi_model_proxy, 'Main')
        self.version89 = self.create_version(self.building2_yapi_model_proxy, 'Main')
        self.version90 = self.create_version(self.building2_yapi_model_proxy, 'Main')

        # Building2 | Props | Yapi | Model | Hires
        self.version91 = self.create_version(self.building2_yapi_model_hires, 'Main')
        self.version92 = self.create_version(self.building2_yapi_model_hires, 'Main')
        self.version93 = self.create_version(self.building2_yapi_model_hires, 'Main')

        # Building2 | Props | Yapi | LookDev
        self.version94 = self.create_version(self.building2_yapi_look_dev, 'Main')
        self.version95 = self.create_version(self.building2_yapi_look_dev, 'Main')
        self.version96 = self.create_version(self.building2_yapi_look_dev, 'Main')

        # Ext1 | Layout | Proxy
        self.version97 = self.create_version(self.ext1_layout_proxy, 'Main')
        self.version98 = self.create_version(self.ext1_layout_proxy, 'Main')
        self.version99 = self.create_version(self.ext1_layout_proxy, 'Main')

        # Ext1 | Layout | Hires
        self.version100 = self.create_version(self.ext1_layout_hires, 'Main')
        self.version101 = self.create_version(self.ext1_layout_hires, 'Main')
        self.version102 = self.create_version(self.ext1_layout_hires, 'Main')

        # Ext1 | LookDev
        self.version103 = self.create_version(self.ext1_look_dev, 'Main')
        self.version104 = self.create_version(self.ext1_look_dev, 'Main')
        self.version105 = self.create_version(self.ext1_look_dev, 'Main')

        # Ext1 | Props | Prop1 | Model | Proxy
        self.version106 = self.create_version(self.prop1_model_proxy, 'Main')
        self.version107 = self.create_version(self.prop1_model_proxy, 'Main')
        self.version108 = self.create_version(self.prop1_model_proxy, 'Main')

        # Ext1 | Props | Prop1 | Model | Hires
        self.version109 = self.create_version(self.prop1_model_hires, 'Main')
        self.version110 = self.create_version(self.prop1_model_hires, 'Main')
        self.version111 = self.create_version(self.prop1_model_hires, 'Main')

        # Ext1 | Props | Prop1 | LookDev
        self.version112 = self.create_version(self.prop1_look_dev, 'Main')
        self.version113 = self.create_version(self.prop1_look_dev, 'Main')
        self.version114 = self.create_version(self.prop1_look_dev, 'Main')

        # Ext1 | Vegetation
        self.version115 = self.create_version(self.ext1_vegetation, 'Main')
        self.version116 = self.create_version(self.ext1_vegetation, 'Main')
        self.version117 = self.create_version(self.ext1_vegetation, 'Main')

        # Ext1 | Prop | LookDev (Kisa)
        self.version118 = self.create_version(self.prop1_look_dev, 'Kisa')
        self.version119 = self.create_version(self.prop1_look_dev, 'Kisa')
        self.version120 = self.create_version(self.prop1_look_dev, 'Kisa')

        # Ext1 | Prop | Model (Kisa)
        self.version121 = self.create_version(self.prop1_model_hires, 'Kisa')
        self.version122 = self.create_version(self.prop1_model_hires, 'Kisa')
        self.version123 = self.create_version(self.prop1_model_hires, 'Kisa')

        # load mtoa plugin
        try:
            pm.loadPlugin("mtoa")
        except RuntimeError:
            # no mtoa plugin
            # pass the test
            pass

        # now fill some content
        # Vegetation
        pm.newFile(force=True)

        # add the nodes
        base_transform = pm.nt.Transform(name='kksEnv___vegetation_ALL')
        strokes = pm.nt.Transform(name='kks___vegetation_pfxStrokes')
        strokes.v.set(0)
        polygons = pm.nt.Transform(name='kks___vegetation_pfxPolygons')
        paintable_geos = pm.nt.Transform(name='kks___vegetation_paintableGeos')

        # hide paintable geos
        paintable_geos.setAttr('v', False)

        pm.parent(strokes, base_transform)
        pm.parent(polygons, base_transform)
        pm.parent(paintable_geos, base_transform)

        # create some flowers
        pm.parent(
            pm.nt.Transform(name='KksEnv_PFXbrush___acacia___strokes'),
            strokes
        )

        pm.parent(
            pm.nt.Transform(name='Kks_PFXbrush___clover___strokes'),
            strokes
        )

        # create some transform nodes
        acacia_polygons = \
            pm.nt.Transform(name='KksEnv_PFXbrush___acacia___polygons')
        pm.parent(
            acacia_polygons,
            polygons
        )

        # and polygons
        acacia_mesh_group = \
            pm.nt.Transform(name='kksEnv_PFXbrush___acacia1MeshGroup')
        acacia_main = pm.polyCube(name='kksEnv_PFXbrush___acacia1Main')[0]
        acacia_leaf = pm.polyCube(name='kksEnv_PFXbrush___acacia1Leaf')[0]

        pm.parent(acacia_mesh_group, acacia_polygons)
        pm.parent(acacia_main, acacia_mesh_group)
        pm.parent(acacia_leaf, acacia_mesh_group)

        clover_polygons = \
            pm.nt.Transform(name='KksEnv_PFXbrush___clover___polygons')
        pm.parent(
            clover_polygons,
            polygons
        )

        # and polygons
        clover_mesh_group = \
            pm.nt.Transform(name='kksEnv_PFXbrush___clover1MeshGroup')
        clover_main = pm.polyCube(name='kksEnv_PFXbrush___clover1Main')[0]
        clover_leaf = pm.polyCube(name='kksEnv_PFXbrush___clover1Leaf')[0]

        pm.parent(clover_mesh_group, clover_polygons)
        pm.parent(clover_main, clover_mesh_group)
        pm.parent(clover_leaf, clover_mesh_group)

        # save its
        self.maya_env.save_as(version=self.version115)
        self.maya_env.save_as(version=self.version116)
        self.maya_env.save_as(version=self.version117)

        #***************************************
        # Prop1
        #***************************************
        # Prop1 | Model | Hires | Main take
        pm.newFile(force=True)
        root_node = pm.nt.Transform(name='prop1')
        kulp = pm.polyCube(name='kulp')
        pm.parent(kulp[0], root_node)
        self.maya_env.save_as(self.version109)
        self.maya_env.save_as(self.version110)
        self.maya_env.save_as(self.version111)
        self.version111.is_published = True

        # save it also under "Kisa" take
        self.maya_env.save_as(self.version121)
        self.maya_env.save_as(self.version122)
        self.maya_env.save_as(self.version123)
        self.version123.is_published = True

        # Prop1 | Look Dev | Main
        pm.newFile(force=True)
        self.maya_env.save_as(self.version112)
        self.maya_env.reference(self.version111)
        # assign a material to the object
        mat = pm.createSurfaceShader('aiStandard', name='kulp_aiStandard')
        pm.sets(mat[1], fe=pm.ls(type='mesh'))

        # save it
        self.maya_env.save_as(self.version112)
        self.maya_env.save_as(self.version113)
        self.maya_env.save_as(self.version114)
        self.version114.is_published = True

        # create "Kisa" take
        # Prop1 | Look Dev | Kisa
        pm.newFile(force=True)
        self.maya_env.save_as(self.version118)
        self.maya_env.reference(self.version123)
        # assign a material to the object
        mat = pm.createSurfaceShader('aiStandard', name='kulp_aiStandard')
        pm.sets(mat[1], fe=pm.ls(type='mesh'))

        self.maya_env.save_as(self.version118)
        self.maya_env.save_as(self.version119)
        self.maya_env.save_as(self.version120)
        self.version120.is_published = True

        #****************************************
        # create Building1
        #****************************************
        # hires model
        pm.newFile(force=True)

        building1_yapi = pm.nt.Transform(name='building1_yapi')
        some_cube = pm.polyCube(name='duvarlar')
        pm.runtime.DeleteHistory(some_cube[1])
        pm.parent(some_cube[0], building1_yapi)

        # save it
        self.maya_env.save_as(self.version73)
        self.maya_env.save_as(self.version74)
        self.maya_env.save_as(self.version75)
        self.version75.is_published = True

        # save it also for Building2 | Props | Yapi | Model
        building1_yapi.rename('building2_yapi')
        self.maya_env.save_as(self.version91)
        self.maya_env.save_as(self.version92)
        self.maya_env.save_as(self.version93)
        self.version93.is_published = True

        # Building1 | Props | Yapi | Look Dev
        pm.newFile(force=True)
        self.maya_env.save_as(self.version76)
        self.maya_env.reference(self.version75)

        # create an arnold material
        mat = pm.createSurfaceShader('aiStandard', name='bina_aiStandard')
        pm.sets(mat[1], fe=pm.ls(type='mesh'))

        # save it
        self.maya_env.save_as(self.version76)
        self.maya_env.save_as(self.version77)
        self.maya_env.save_as(self.version78)
        self.version78.is_published = True

        # save it for Building2 | Props | Yapi | Look Dev
        pm.listReferences()[0].replaceWith(self.version93.absolute_full_path)
        self.maya_env.save_as(self.version94)
        self.maya_env.save_as(self.version95)
        self.maya_env.save_as(self.version96)
        self.version96.is_published = True

        # building1 layout
        pm.newFile(force=1)
        base_group = pm.nt.Transform(name='building1_layout')

        self.maya_env.save_as(self.version64)
        ref = self.maya_env.reference(self.version78)
        ref_root_node = pm.ls('*:*:*building1_yapi')[0]
        pm.parent(ref_root_node, base_group)

        self.maya_env.save_as(self.version64)
        self.maya_env.save_as(self.version65)
        self.maya_env.save_as(self.version66)
        self.version66.is_published = True

        # building2 layout
        pm.newFile(force=1)
        base_group = pm.nt.Transform(name='building2_layout')

        # reference building2 | yapi | look dev
        self.maya_env.save_as(self.version82)
        ref = self.maya_env.reference(self.version96)
        ref_root_node = pm.ls('*:*:*building2_yapi')[0]
        pm.parent(ref_root_node, base_group)

        self.maya_env.save_as(self.version82)
        self.maya_env.save_as(self.version83)
        self.maya_env.save_as(self.version84)
        self.version84.is_published = True

        # building1 | look dev
        pm.newFile(force=True)
        # reference building1 | Layout | Hires
        self.maya_env.save_as(self.version67)
        self.maya_env.reference(self.version66)
        # just save it
        self.maya_env.save_as(self.version67)
        self.maya_env.save_as(self.version68)
        self.maya_env.save_as(self.version69)
        self.version69.is_published = True

        # building2 | look dev
        pm.newFile(force=True)
        # reference building1 | Layout | Hires
        self.maya_env.save_as(self.version85)
        self.maya_env.reference(self.version84)
        # just save it
        self.maya_env.save_as(self.version85)
        self.maya_env.save_as(self.version86)
        self.maya_env.save_as(self.version87)
        self.version87.is_published = True

        # prepare the main layout of the exterior
        pm.newFile(force=True)
        self.maya_env.save_as(self.version100)
        # reference Building1 | Layout | Hires
        self.maya_env.reference(self.version66)
        # reference Building2 | Layout | Hires
        self.maya_env.reference(self.version84)

        # create the layout root node
        root_node = pm.nt.Transform(name='ext1_layout')
        # parent the other buildings under this node
        building1_layout = pm.ls('*:*building1_layout')[0]
        building2_layout = pm.ls('*:*building2_layout')[0]

        pm.parent(building1_layout, root_node)
        pm.parent(building2_layout, root_node)

        # move them around
        building1_layout.setAttr('t', (10, 0, 0))
        building2_layout.setAttr('t', (0, 0, 10))

        # reference the vegetation
        self.maya_env.reference(self.version117)

        # save it
        self.maya_env.save_as(self.version100)
        self.maya_env.save_as(self.version101)
        self.maya_env.save_as(self.version102)
        self.version102.is_published = True

        #*********************************
        # The Look Dev of the environment
        #*********************************
        pm.newFile(force=True)
        self.maya_env.save_as(self.version103)
        self.maya_env.reference(self.version102)
        self.maya_env.save_as(self.version103)
        self.maya_env.save_as(self.version104)
        self.maya_env.save_as(self.version105)
        self.version105.is_published = True
        pm.newFile(force=True)

        # +- task1
        # |  |
        # |  +- task4
        # |  |  |
        # |  |  +- asset2
        # |  |     +- Main
        # |  |     |  +- version1
        # |  |     |  +- version2 (P)
        # |  |     |  +- version3 (P)
        # |  |     +- Take1
        # |  |        +- version4 (P)
        # |  |        +- version5
        # |  |        +- version6 (P)
        # |  |
        # |  +- task5
        # |  |  +- Main
        # |  |  |  +- version7
        # |  |  |  +- version8
        # |  |  |  +- version9
        # |  |  +- Take1
        # |  |     +- version10
        # |  |     +- version11
        # |  |     +- version12 (P)
        # |  |
        # |  +- task6
        # |     +- Main
        # |     |  +- version13
        # |     |  +- version14
        # |     |  +- version15
        # |     +- Take1
        # |        +- version16 (P)
        # |        +- version17
        # |        +- version18 (P)
        # |
        # +- task2
        # |  |
        # |  +- sequence2
        # |     |
        # |     +- shot3
        # |        +- Main
        # |        |  +- version19
        # |        |  +- version20
        # |        |  +- version21
        # |        +- Take1
        # |           +- version22
        # |           +- version23
        # |           +- version24
        # |
        # +- task3
        # |  +- Main
        # |  |  +- version25
        # |  |  +- version26
        # |  |  +- version27
        # |  +- Take1
        # |     +- version28
        # |     +- version29
        # |     +- version30
        # |
        # +- asset1
        # |  +- Main
        # |  |  +- version31
        # |  |  +- version32
        # |  |  +- version33
        # |  +- Take1
        # |     +- version34
        # |     +- version35
        # |     +- version36
        # |
        # +- sequence1
        # |  |
        # |  +- shot2
        # |     +- Main
        # |     |  +- version37
        # |     |  +- version38
        # |     |  +- version39
        # |     +- Take1
        # |        +- version40
        # |        +- version41
        # |        +- version42
        # |
        # +- shot1
        # |  +- Main
        # |  |  +- version43
        # |  |  +- version44
        # |  |  +- version45
        # |  +- Take1
        # |     +- version46
        # |     +- version47
        # |     +- version48
        # |
        # +- Assets (Task)
        #    +- Characters (Task)
        #    |  +- Char1 (Asset - Character)
        #    |     +- Character Design (Task - Character Design)
        #    |     |  +- version49
        #    |     |  +- version50
        #    |     |  +- version51
        #    |     |
        #    |     +- Model (Task - Model)
        #    |     |  +- version52
        #    |     |  +- version53
        #    |     |  +- version54
        #    |     |
        #    |     +- Look Dev (Task - Look Development)
        #    |     |  +- version55
        #    |     |  +- version56
        #    |     |  +- version57
        #    |     |
        #    |     +- Rig (Task - Rig)
        #    |        +- version58
        #    |        +- version59
        #    |        +- version60
        #    |
        #    +- Environments (Task)
        #       +- Exteriors (Task)
        #          +- Ext1 (Asset - Exterior)
        #             +- Building1 (Asset - Building)
        #             |  +- Layout (Task - Layout)
        #             |  |  +- Proxy (Task - Layout)
        #             |  |  |  +- version61
        #             |  |  |  +- version62
        #             |  |  |  +- version63
        #             |  |  |
        #             |  |  +- Hires (Task - Layout)
        #             |  |     +- version64
        #             |  |     +- version65
        #             |  |     +- version66
        #             |  |
        #             |  +- LookDev (Task - Look Development)
        #             |  |  +- version67
        #             |  |  +- version68
        #             |  |  +- version69
        #             |  |
        #             |  +- Props (Task)
        #             |     +- YAPI (Task)
        #             |        +- Model (Task - Model)
        #             |        |  +- Proxy (Task - Model)
        #             |        |  |  +- version70
        #             |        |  |  +- version71
        #             |        |  |  +- version72
        #             |        |  |
        #             |        |  +- Hires (Task - Model)
        #             |        |     +- version73
        #             |        |     +- version74
        #             |        |     +- version75
        #             |        |
        #             |        +- LookDev (Task - Look Development)
        #             |           +- version76
        #             |           +- version77
        #             |           +- version78
        #             |
        #             +- Building2 (Asset - Building)
        #             |  +- Layout (Task - Layout)
        #             |  |  +- Proxy (Task - Layout)
        #             |  |  |  +- version79
        #             |  |  |  +- version80
        #             |  |  |  +- version81
        #             |  |  |
        #             |  |  +- Hires (Task - Layout)
        #             |  |     +- version82
        #             |  |     +- version83
        #             |  |     +- version84
        #             |  |
        #             |  +- LookDev (Task - Look Development)
        #             |  |  +- version85
        #             |  |  +- version86
        #             |  |  +- version87
        #             |  |
        #             |  +- Props (Task)
        #             |     +- YAPI (Task)
        #             |        +- Model (Task - Model)
        #             |        |  +- Proxy (Task - Model)
        #             |        |  |  +- version88
        #             |        |  |  +- version89
        #             |        |  |  +- version90
        #             |        |  |
        #             |        |  +- Hires (Task - Model)
        #             |        |     +- version91
        #             |        |     +- version92
        #             |        |     +- version93
        #             |        |
        #             |        +- LookDev (Task - Look Development)
        #             |           +- version94
        #             |           +- version95
        #             |           +- version96
        #             |
        #             +- Layout (Task - Layout)
        #             |  +- Proxy (Task - Layout)
        #             |  |  +- version97
        #             |  |  +- version98
        #             |  |  +- version99
        #             |  |
        #             |  +- Hires (Task - Layout)
        #             |     +- version100
        #             |     +- version101
        #             |     +- version102
        #             |
        #             +- LookDev (Task - Look Development)
        #             |  +- version103
        #             |  +- version104
        #             |  +- version105
        #             |
        #             +- Props (Task)
        #             |  +- Prop1 (Asset)
        #             |     +- Model (Task - Model)
        #             |     |  +- Proxy (Task - Model)
        #             |     |  |  +- version106
        #             |     |  |  +- version107
        #             |     |  |  +- version108
        #             |     |  |
        #             |     |  +- Hires (Task - Model)
        #             |     |     +- **Main** (Take)
        #             |     |     |  +- version109
        #             |     |     |  +- version110
        #             |     |     |  +- version111
        #             |     |     +- **Kisa** (Take)
        #             |     |        +- version121
        #             |     |        +- version122
        #             |     |        +- version123
        #             |     |
        #             |     +- LookDev (Task - Look Development)
        #             |        +- **Main** (Take)
        #             |        |  +- version112
        #             |        |  +- version113
        #             |        |  +- version114
        #             |        +- **Kisa** (Take)
        #             |           +- version118
        #             |           +- version119
        #             |           +- version120
        #             |
        #             +- Vegetation (Task - Vegetation)
        #                +- version115
        #                +- version116
        #                +- version117

        # just renew the scene
        pm.newFile(force=True)

        # create a buffer for extra created files, which are to be removed
        self.remove_these_files_buffer = []

    def tearDown(self):
        """cleanup the test
        """
        # set the db.session to None
        DBSession.remove()

        # delete the temp folder
        shutil.rmtree(self.temp_repo_path, ignore_errors=True)

        for f in self.remove_these_files_buffer:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f, True)

    @classmethod
    def tearDownClass(cls):
        # quit maya
        pm.runtime.Quit()


class MayaTestCase(MayaTestBase):
    """tests the maya.Maya
    """

    def test_save_as_creates_a_maya_file_at_version_absolute_full_path(self):
        """testing if the save_as creates a maya file at the Version.full_path
        """
        version1 = Version(task=self.task6)
        version1.extension = '.ma'
        version1.update_paths()

        # check the version file doesn't exists
        self.assertFalse(os.path.exists(version1.absolute_full_path))

        # save the version
        self.maya_env.save_as(version1)

        # check the file exists
        self.assertTrue(os.path.exists(version1.absolute_full_path))

    def test_save_as_sets_the_version_extension_to_ma(self):
        """testing if the save_as method sets the version extension to ma
        """
        version1 = Version(task=self.task6)
        version1.extension = '.ma'
        version1.update_paths()

        version1.extension = ""
        self.maya_env.save_as(version1)
        self.assertEqual(version1.extension, ".ma")

    def test_save_as_sets_the_render_version_string(self):
        """testing if the save_as method sets the version string in the render
        settings
        """
        version1 = Version(
            task=self.task1
        )
        version1.extension = '.ma'
        version1.update_paths()
        DBSession.add(version1)
        DBSession.commit()

        self.maya_env.save_as(version1)

        # now check if the render settings version is the same with the
        # version.version_number

        render_version =\
            pm.getAttr("defaultRenderGlobals.renderVersion")
        self.assertEqual(render_version,
                         "v%03d" % version1.version_number)

    def test_save_as_sets_the_render_format_to_exr_for_mentalray(self):
        """testing if the save_as method sets the render format to exr
        """
        # load mayatomr plugin
        try:
            pm.loadPlugin("Mayatomr")
        except RuntimeError:
            # no Mayatomr plugin
            # so pass the test
            return

        # set the current renderer to mentalray
        dRG = pm.PyNode("defaultRenderGlobals")

        dRG.setAttr('currentRenderer', 'mentalRay')

        # dirty little maya tricks
        pm.mel.miCreateDefaultNodes()

        mrG = pm.PyNode("mentalrayGlobals")

        version1 = Version(
            task=self.task1
        )
        version1.extension = '.ma'
        version1.update_paths()
        DBSession.add(version1)
        DBSession.commit()
        self.maya_env.save_as(version1)

        # now check if the render format is correctly set to exr with zip
        # compression
        self.assertEqual(dRG.getAttr("imageFormat"), 51)
        self.assertEqual(dRG.getAttr("imfkey"), "exr")
        self.assertEqual(mrG.getAttr("imageCompression"), 4)

    @unittest.skip('creates segmanteation fault')
    def test_save_as_sets_the_render_format_to_exr_for_arnold(self):
        """testing if the save_as method sets the render format to exr when the
        renderer is arnold
        """
        # load mtoa plugin
        try:
            pm.loadPlugin("mtoa")
        except RuntimeError:
            # no mtoa plugin
            # pass the test
            return

        # set the current renderer to arnold
        dRG = pm.PyNode("defaultRenderGlobals")
        dRG.setAttr('currentRenderer', 'arnold')

        # dirty little maya tricks: do a render to create arnold globals
        from mtoa.cmds.arnoldRender import arnoldRender
        arnoldRender(10, 10, False, False,
                     'perspShape', ' -layer defaultRenderLayer')

        dAD = pm.PyNode("defaultArnoldDriver")

        version1 = Version(
            task=self.task1
        )
        version1.extension = '.ma'
        version1.update_paths()
        DBSession.add(version1)
        DBSession.commit()
        self.maya_env.save_as(version1)

        # now check if the render format is correctly set to exr with zip
        # compression
        self.assertEqual(dRG.getAttr("imageFormat"), 51)
        self.assertEqual(dAD.exrCompression.get(), 2)  # zips
        self.assertEqual(dAD.halfPrecision.get(), 1)  # half
        self.assertEqual(dAD.tiled.get(), 0)  # not tiled
        self.assertEqual(dAD.autocrop.get(), 1)  # auto crop

    def test_save_as_sets_the_render_file_name_for_Assets(self):
        """testing if the save_as sets the render file name correctly
        """
        version1 = Version(task=self.task6)
        version1.extension = '.ma'
        version1.update_paths()

        self.maya_env.save_as(version1)

        # check if the path equals to
        expected_path = \
            '../../Outputs/<RenderLayer>/' \
            '%(project_code)s_%(version_nice_name)s_v%(version_number)s' \
            '_<RenderLayer>_<RenderPass>' % {
                'project_code': version1.task.project.code,
                'version_nice_name': version1.nice_name,
                'version_number': ('%s' % version1.version_number).zfill(3)
            }

        image_path = os.path.join(
            pm.workspace.path,
            pm.workspace.fileRules['image']
        ).replace("\\", "/")

        expected_path = utils.relpath(
            image_path,
            expected_path,
        )

        dRG = pm.PyNode("defaultRenderGlobals")

        self.assertEqual(
            expected_path,
            dRG.getAttr("imageFilePrefix")
        )

    def test_save_as_sets_the_render_file_name_for_Shots(self):
        """testing if the save_as sets the render file name correctly
        """
        version1 = Version(task=self.task6)
        version1.extension = '.ma'
        version1.update_paths()

        self.maya_env.save_as(version1)

        # check if the path equals to
        expected_path = \
            '../../Outputs/<RenderLayer>/' \
            '%(project_code)s_%(version_nice_name)s_v%(version_number)s' \
            '_<RenderLayer>_<RenderPass>' % {
                'project_code': version1.task.project.code,
                'version_nice_name': version1.nice_name,
                'version_number': ('%s' % version1.version_number).zfill(3)
            }

        image_path = os.path.join(
            pm.workspace.path,
            pm.workspace.fileRules['image']
        ).replace("\\", "/")

        expected_path = utils.relpath(
            image_path,
            expected_path,
        )

        dRG = pm.PyNode("defaultRenderGlobals")

        self.assertEqual(
            expected_path,
            dRG.getAttr("imageFilePrefix")
        )

    # def test_save_as_replaces_file_image_paths(self):
    #     """testing if save_as method replaces image paths with REPO relative
    #     path
    #     """
    #     self.maya_env.save_as(self.version1)
    # 
    #     # create file node
    #     file_node = pm.createNode("file")
    # 
    #     # set it to a path in the workspace
    #     texture_path = os.path.join(
    #         pm.workspace.path, ".maya_files/textures/test.jpg"
    #     )
    #     file_node.fileTextureName.set(texture_path)
    # 
    #     # save a newer version
    #     version2 = Version(**self.kwargs)
    #     version2.save()
    # 
    #     self.maya_env.save_as(version2)
    # 
    #     # now check if the file nodes fileTextureName is converted to a
    #     # relative path to the current workspace
    # 
    #     expected_path = texture_path.replace(os.environ["REPO"], "$REPO")
    # 
    #     self.assertEqual(
    #         file_node.getAttr("fileTextureName"),
    #         expected_path
    #     )

    def test_save_as_sets_the_resolution(self):
        """testing if save_as sets the render resolution for the current scene
        """
        version1 = Version(
            task=self.task1
        )
        version1.extension = '.ma'
        version1.update_paths()
        DBSession.add(version1)
        DBSession.commit()

        width = self.project.image_format.width
        height = self.project.image_format.height
        pixel_aspect = self.project.image_format.pixel_aspect

        # save the scene
        self.maya_env.save_as(version1)

        # check the resolutions
        dRes = pm.PyNode("defaultResolution")
        self.assertEqual(dRes.width.get(), width)
        self.assertEqual(dRes.height.get(), height)
        self.assertEqual(dRes.pixelAspect.get(), pixel_aspect)

    def test_save_as_sets_the_resolution_only_for_first_version(self):
        """testing if save_as sets the render resolution for the current scene
        but only for the first version of the asset
        """
        version1 = Version(
            task=self.task1
        )
        version1.extension = '.ma'
        version1.update_paths()
        DBSession.add(version1)
        DBSession.commit()

        width = self.project.image_format.width
        height = self.project.image_format.height
        pixel_aspect = self.project.image_format.pixel_aspect

        # save the scene
        self.maya_env.save_as(version1)

        # check the resolutions
        dRes = pm.PyNode("defaultResolution")
        self.assertEqual(dRes.width.get(), width)
        self.assertEqual(dRes.height.get(), height)
        self.assertEqual(dRes.pixelAspect.get(), pixel_aspect)

        new_width = 1280
        new_height = 720
        new_pixel_aspect = 1.0
        dRes.width.set(new_width)
        dRes.height.set(new_height)
        dRes.pixelAspect.set(new_pixel_aspect)

        # save the version again
        new_version = Version(
            task=self.task1
        )
        new_version.extension = '.ma'
        new_version.update_paths()
        DBSession.add(new_version)
        DBSession.commit()

        self.maya_env.save_as(new_version)

        # test if the resolution is not changed
        self.assertEqual(dRes.width.get(), new_width)
        self.assertEqual(dRes.height.get(), new_height)
        self.assertEqual(dRes.pixelAspect.get(), new_pixel_aspect)

    def test_save_as_fills_the_referenced_versions_list(self):
        """testing if the save_as method updates the Version.inputs list with
        the current references list from the Maya
        """
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        versionBase = Version(task=self.task6)
        DBSession.add(versionBase)
        DBSession.commit()

        # change the take name
        version1 = Version(
            task=self.task6,
            take_name="Take1"
        )
        DBSession.add(version1)
        DBSession.commit()

        version2 = Version(
            task=self.task6,
            take_name="Take2"
        )
        DBSession.add(version2)
        DBSession.commit()

        version3 = Version(
            task=self.task6,
            take_name="Take3"
        )
        DBSession.add(version3)
        DBSession.commit()

        # now create scenes with these files
        self.maya_env.save_as(version1)
        self.maya_env.save_as(version2)
        self.maya_env.save_as(version3)  # this is the dummy version

        # create a new scene
        pm.newFile(force=True)

        # check if the versionBase.inputs is an empty list
        self.assertTrue(versionBase.inputs == [])

        # reference the given versions
        self.maya_env.reference(version1)
        self.maya_env.reference(version2)

        # save it as versionBase
        self.maya_env.save_as(versionBase)

        # now check if versionBase.references is updated
        self.assertTrue(len(versionBase.inputs) == 2)

        self.assertEqual(
            sorted(versionBase.inputs, key=lambda x: x.name),
            sorted([version1, version2], key=lambda x: x.name)
        )

    def test_save_as_of_a_scene_with_two_references_to_the_same_version(self):
        """testing if the case where the current maya scene has two references
        to the same file is gracefully handled by assigning the version only
        once
        """
        # create a version for an asset
        vers1 = Version(task=self.asset1)

        # save it
        self.maya_env.save_as(vers1)

        # new scene
        pm.newFile(force=True)

        # create another version with different type
        vers2 = Version(task=self.asset1)

        # reference the other version twice
        self.maya_env.reference(vers1)
        self.maya_env.reference(vers1)

        # save it and expect no InvalidRequestError
        self.maya_env.save_as(vers2)

        # reference again
        self.maya_env.reference(vers1)

        # save as another version
        vers3 = Version(task=self.asset1)
        self.maya_env.save_as(vers3)

    def test_save_as_move_external_files_to_project_folder(self):
        """testing if save_as will move all the external files to project
        folder under the "external_files" folder
        """
        # create a texture file with local path
        new_texture_file = pm.nt.File()
        # generate a local path
        local_file_full_path = os.path.join(
            tempfile.gettempdir(),
            "temp.png"
        )
        # touch the file
        with open(local_file_full_path, 'w'):
            pass

        self.remove_these_files_buffer.append(local_file_full_path)
        new_texture_file.fileTextureName.set(local_file_full_path)

        # now save it as a new version
        version1 = Version(task=self.task1)
        DBSession.add(version1)
        DBSession.commit()

        self.maya_env.save_as(version1)

        # and expect the fileTexture has been moved to workspace/external_files
        # folder
        expected_path =\
            Repository.to_os_independent_path(
                os.path.join(
                    version1.absolute_path,
                    'external_files/Textures/temp.png'
                )
            )

        self.assertEqual(
            expected_path,
            new_texture_file.fileTextureName.get()
        )

    def test_open_updates_the_referenced_versions_list(self):
        """testing if the open method updates the Version.inputs list with the
        current references list from the Maya
        """
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        versionBase = Version(task=self.task1)
        DBSession.add(versionBase)
        DBSession.commit()

        # change the take name
        version1 = Version(task=self.task1, take_name="Take1")
        DBSession.add(version1)
        DBSession.commit()

        version2 = Version(task=self.task1, take_name="Take2")
        DBSession.add(version2)
        DBSession.commit()

        version3 = Version(task=self.task1, take_name="Take3")
        DBSession.add(version2)
        DBSession.commit()

        # now create scenes with these files
        self.maya_env.save_as(version1)
        self.maya_env.save_as(version2)
        self.maya_env.save_as(version3)  # this is the dummy version

        # create a new scene
        pm.newFile(force=True)

        # check if the versionBase.references is an empty list
        self.assertEqual([], versionBase.inputs)

        # reference the given versions
        self.maya_env.reference(version1)
        self.maya_env.reference(version2)

        # save it as versionBase
        self.maya_env.save_as(versionBase)

        # now check if versionBase.inputs is updated
        # this part is already tested in save_as
        self.assertEqual(2, len(versionBase.inputs))
        self.assertEqual(
            sorted(versionBase.inputs, key=lambda x: x.name),
            sorted([version1, version2], key=lambda x: x.name)
        )

        # now remove references
        for ref_node in pm.listReferences():
            ref_node.remove()

        # do a save (not save_as)
        pm.saveFile()

        # clean scene
        pm.newFile(force=True)

        # open the same version
        self.maya_env.open(versionBase, force=True)

        # and check the references is updated
        self.assertEqual(0, len(versionBase.inputs))
        self.assertEqual(versionBase.inputs, [])

    def test_open_does_not_load_unloaded_references(self):
        """testing if the open method doesn't load unloaded references
        """
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        version_base = Version(task=self.task1)
        DBSession.add(version_base)
        DBSession.commit()

        # change the take name
        version1 = Version(task=self.task1, take_name="Take1")
        DBSession.add(version1)
        DBSession.commit()

        version2 = Version(task=self.task1, take_name="Take2")
        DBSession.add(version2)
        DBSession.commit()

        version3 = Version(task=self.task1, take_name="Take3")
        DBSession.add(version3)
        DBSession.commit()

        # now create scenes with these files
        self.maya_env.save_as(version1)
        self.maya_env.save_as(version2)
        self.maya_env.save_as(version3)  # this is the dummy version

        # create a new scene
        pm.newFile(force=True)

        # reference the given versions
        self.maya_env.reference(version1)
        self.maya_env.reference(version2)

        # unload a couple of them
        refs = pm.listReferences()
        refs[0].unload()
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # save it as versionBase
        self.maya_env.save_as(version_base)
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # clean scene
        pm.newFile(force=True)

        # re-open the file
        self.maya_env.open(version_base, force=True)

        # check if the references are loaded
        refs = pm.listReferences()
        self.assertTrue(refs[1].isLoaded())
        self.assertFalse(refs[0].isLoaded())

    def test_open_with_reference_depth_parameter_is_skipped(self):
        """testing if the open method doesn't load unloaded references when
        the reference_depth parameter is skipped
        """
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        version_base = Version(task=self.task1)
        DBSession.add(version_base)
        DBSession.commit()

        # change the take name
        version1 = Version(task=self.task1, take_name="Take1")
        DBSession.add(version1)
        DBSession.commit()

        version2 = Version(task=self.task1, take_name="Take2")
        DBSession.add(version2)
        DBSession.commit()

        version3 = Version(task=self.task1, take_name="Take3")
        DBSession.add(version3)
        DBSession.commit()

        # now create scenes with these files
        self.maya_env.save_as(version1)
        self.maya_env.save_as(version2)
        self.maya_env.save_as(version3)  # this is the dummy version

        # create a new scene
        pm.newFile(force=True)

        # reference the given versions
        self.maya_env.reference(version1)
        self.maya_env.reference(version2)

        # unload a couple of them
        refs = pm.listReferences()
        refs[0].unload()
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # save it as versionBase
        self.maya_env.save_as(version_base)
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # clean scene
        pm.newFile(force=True)

        # re-open the file
        self.maya_env.open(version_base, force=True)

        # check if the references are loaded
        refs = pm.listReferences()
        self.assertTrue(refs[1].isLoaded())
        self.assertFalse(refs[0].isLoaded())

    def test_open_with_reference_depth_parameter_is_0(self):
        """testing if the open method doesn't load unloaded references when
        the reference_depth parameter is 0
        """
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        version_base = Version(task=self.task1)
        DBSession.add(version_base)
        DBSession.commit()

        # change the take name
        version1 = Version(task=self.task1, take_name="Take1")
        DBSession.add(version1)
        DBSession.commit()

        version2 = Version(task=self.task1, take_name="Take2")
        DBSession.add(version2)
        DBSession.commit()

        version3 = Version(task=self.task1, take_name="Take3")
        DBSession.add(version3)
        DBSession.commit()

        # now create scenes with these files
        self.maya_env.save_as(version1)
        self.maya_env.save_as(version2)
        self.maya_env.save_as(version3)  # this is the dummy version

        # create a new scene
        pm.newFile(force=True)

        # reference the given versions
        self.maya_env.reference(version1)
        self.maya_env.reference(version2)

        # unload a couple of them
        refs = pm.listReferences()
        refs[0].unload()
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # save it as versionBase
        self.maya_env.save_as(version_base)
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # clean scene
        pm.newFile(force=True)

        # re-open the file
        self.maya_env.open(version_base, force=True, reference_depth=0)

        # check if the references are loaded
        refs = pm.listReferences()
        self.assertTrue(refs[1].isLoaded())
        self.assertFalse(refs[0].isLoaded())

    def test_open_with_reference_depth_parameter_is_1(self):
        """testing if the open method will load all unloaded references when
        the reference_depth parameter is 1
        """
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        version_base = Version(task=self.task1)
        DBSession.add(version_base)
        DBSession.commit()

        # change the take name
        version1 = Version(task=self.task1, take_name="Take1")
        DBSession.add(version1)
        DBSession.commit()

        version2 = Version(task=self.task1, take_name="Take2")
        DBSession.add(version2)
        DBSession.commit()

        version3 = Version(task=self.task1, take_name="Take3")
        DBSession.add(version3)
        DBSession.commit()

        # now create scenes with these files
        self.maya_env.save_as(version1)
        self.maya_env.save_as(version2)
        self.maya_env.save_as(version3)  # this is the dummy version

        # create a new scene
        pm.newFile(force=True)

        # reference the given versions
        self.maya_env.reference(version1)
        self.maya_env.reference(version2)

        # unload a couple of them
        refs = pm.listReferences()
        refs[0].unload()
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # save it as versionBase
        self.maya_env.save_as(version_base)
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # clean scene
        pm.newFile(force=True)

        # re-open the file
        self.maya_env.open(version_base, force=True, reference_depth=1)

        # check if the references are loaded
        refs = pm.listReferences()
        self.assertTrue(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

    def test_open_with_reference_depth_parameter_is_2(self):
        """testing if the open method will load top only references when the
        reference_depth parameter is 2
        """
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        version_base = Version(task=self.task1)
        DBSession.add(version_base)
        DBSession.commit()

        # change the take name
        version1 = Version(task=self.task1, take_name="Take1")
        DBSession.add(version1)
        DBSession.commit()

        version2 = Version(task=self.task1, take_name="Take2")
        DBSession.add(version2)
        DBSession.commit()

        version3 = Version(task=self.task1, take_name="Take3")
        DBSession.add(version3)
        DBSession.commit()

        version4 = Version(task=self.task1, take_name="Take3")
        DBSession.add(version3)
        DBSession.commit()

        # now create scenes with these files
        self.maya_env.save_as(version1)
        self.maya_env.save_as(version2)
        self.maya_env.save_as(version3)  # this is the dummy version
        self.maya_env.save_as(version4)

        # reference version4 to version2
        self.maya_env.open(version2, force=True)
        self.maya_env.reference(version4)
        pm.saveFile()

        # create a new scene
        pm.newFile(force=True)

        # reference the given versions
        self.maya_env.reference(version1)
        self.maya_env.reference(version2)

        # unload a couple of them
        refs = pm.listReferences()
        refs[0].unload()
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # save it as versionBase
        self.maya_env.save_as(version_base)
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # clean scene
        pm.newFile(force=True)

        # re-open the file
        self.maya_env.open(version_base, force=True, reference_depth=2)

        # check if the references are loaded
        refs = pm.listReferences(recursive=True)
        self.assertTrue(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())
        self.assertFalse(refs[2].isLoaded())

    def test_open_with_reference_depth_parameter_is_3(self):
        """testing if the open method will load none of the references when the
        reference_depth parameter is 3
        """
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        version_base = Version(task=self.task1)
        DBSession.add(version_base)
        DBSession.commit()

        # change the take name
        version1 = Version(task=self.task1, take_name="Take1")
        DBSession.add(version1)
        DBSession.commit()

        version2 = Version(task=self.task1, take_name="Take2")
        DBSession.add(version2)
        DBSession.commit()

        version3 = Version(task=self.task1, take_name="Take3")
        DBSession.add(version3)
        DBSession.commit()

        version4 = Version(task=self.task1, take_name="Take3")
        DBSession.add(version3)
        DBSession.commit()

        # now create scenes with these files
        self.maya_env.save_as(version1)
        self.maya_env.save_as(version2)
        self.maya_env.save_as(version3)  # this is the dummy version
        self.maya_env.save_as(version4)

        # reference version4 to version2
        self.maya_env.open(version2, force=True)
        self.maya_env.reference(version4)
        pm.saveFile()

        # create a new scene
        pm.newFile(force=True)

        # reference the given versions
        self.maya_env.reference(version1)
        self.maya_env.reference(version2)

        # unload a couple of them
        refs = pm.listReferences()
        refs[0].unload()
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # save it as versionBase
        self.maya_env.save_as(version_base)
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # clean scene
        pm.newFile(force=True)

        # re-open the file
        self.maya_env.open(version_base, force=True, reference_depth=3)

        # check if the references are loaded
        refs = pm.listReferences(recursive=True)
        self.assertFalse(refs[0].isLoaded())
        self.assertFalse(refs[1].isLoaded())

    def test_open_replaces_first_level_reference_paths_with_os_independent_path(self):
        """testing if Maya.open() will replace first level reference paths with
        os independent path
        """
        # create a new reference
        version_base = Version(task=self.task1)
        DBSession.add(version_base)
        DBSession.commit()

        # change the take name
        version1 = Version(task=self.task1, take_name="Take1")
        DBSession.add(version1)
        DBSession.commit()

        version2 = Version(task=self.task1, take_name="Take2")
        DBSession.add(version2)
        DBSession.commit()

        version3 = Version(task=self.task1, take_name="Take3")
        DBSession.add(version3)
        DBSession.commit()

        # now create scenes with these files
        self.maya_env.save_as(version1)
        self.maya_env.save_as(version2)
        self.maya_env.save_as(version3)  # this is the dummy version

        # create a new scene
        pm.newFile(force=True)

        # save it as a new version
        self.maya_env.save_as(version_base)

        # reference the given versions
        ref1 = self.maya_env.reference(version1)
        ref2 = self.maya_env.reference(version2)

        # convert the path to abs on purpose
        ref1.replaceWith(ref1.path)
        ref2.replaceWith(ref2.path)

        self.assertFalse('$' in ref1.unresolvedPath())
        self.assertFalse('$' in ref2.unresolvedPath())
        self.assertEqual(ref1.path, ref1.unresolvedPath())
        self.assertEqual(ref2.path, ref2.unresolvedPath())

        # save the file
        pm.saveFile()

        # check if paths are still using absolute paths
        self.assertEqual(ref1.path, ref1.unresolvedPath())
        self.assertEqual(ref2.path, ref2.unresolvedPath())
        self.assertTrue(os.path.isabs(ref1.unresolvedPath()))
        self.assertTrue(os.path.isabs(ref2.unresolvedPath()))

        # open it with Maya
        pm.newFile(f=True)

        self.maya_env.open(version_base, force=True)
        references = pm.listReferences()
        ref1 = references[0]
        ref2 = references[1]

        # and expect the path to be os independent again
        self.assertNotEqual(ref1.path, ref1.unresolvedPath())
        self.assertNotEqual(ref2.path, ref2.unresolvedPath())
        self.assertFalse(os.path.isabs(ref1.unresolvedPath()))
        self.assertFalse(os.path.isabs(ref2.unresolvedPath()))
        self.assertTrue('$' in ref1.unresolvedPath())
        self.assertTrue('$' in ref2.unresolvedPath())

    def test_open_will_open_the_requested_representations_of_the_first_level_references(self):
        """testing if Maya.open() will open with the requested representations
        of the first level references
        """
        # create three different versions
        # create both a Base and a BBox representation for each of them

        # Base repr
        a_base_v1 = self.create_version(self.asset1, 'Main')

        a_base_v2 = self.create_version(self.asset1, 'Main')
        a_base_v2.is_published = True

        a_base_v3 = self.create_version(self.asset1, 'Main')
        a_base_v3.is_published = True

        # BBox repr
        a_bbox_v1 = self.create_version(self.asset1, 'Main@BBox', a_base_v3)

        a_bbox_v2 = self.create_version(self.asset1, 'Main@BBox', a_base_v3)
        a_bbox_v2.is_published = True

        a_bbox_v3 = self.create_version(self.asset1, 'Main@BBox', a_base_v3)
        a_bbox_v3.is_published = True

        # a new series of versions
        # Base repr
        b_base_v1 = self.create_version(self.asset1, 'Main')

        b_base_v2 = self.create_version(self.asset1, 'Main')
        b_base_v2.is_published = True

        b_base_v3 = self.create_version(self.asset1, 'Main')
        b_base_v3.is_published = True

        # BBox repr
        b_bbox_v1 = self.create_version(self.asset1, 'Main@BBox', b_base_v3)

        b_bbox_v2 = self.create_version(self.asset1, 'Main@BBox', b_base_v3)
        b_bbox_v2.is_published = True

        b_bbox_v3 = self.create_version(self.asset1, 'Main@BBox', b_base_v3)
        b_bbox_v3.is_published = True

        # and another one
        # a new series of versions
        # Base repr
        c_base_v1 = self.create_version(self.asset1, 'Main')

        c_base_v2 = self.create_version(self.asset1, 'Main')
        c_base_v2.is_published = True

        c_base_v3 = self.create_version(self.asset1, 'Main')
        c_base_v3.is_published = True

        # BBox repr
        c_bbox_v1 = self.create_version(self.asset1, 'Main@BBox', c_base_v3)

        c_bbox_v2 = self.create_version(self.asset1, 'Main@BBox', c_base_v3)
        c_bbox_v2.is_published = True

        c_bbox_v3 = self.create_version(self.asset1, 'Main@BBox', c_base_v3)
        c_bbox_v3.is_published = True

        # save it as a new version
        base_version = self.create_version(self.task1, 'Main')

        # reference the Base versions of each of them to this new scene
        self.maya_env.reference(a_base_v3)
        self.maya_env.reference(b_base_v3)
        self.maya_env.reference(c_base_v3)

        # expect all of the references to be Base representations
        all_refs = pm.listReferences()
        self.assertTrue(all_refs[0].is_repr('Base'))
        self.assertTrue(all_refs[1].is_repr('Base'))
        self.assertTrue(all_refs[2].is_repr('Base'))

        # save it again
        self.maya_env.save_as(base_version)

        # new scene
        pm.newFile(force=1)

        # open the same version with requesting the BBox representation
        self.maya_env.open(base_version, representation='BBox')

        # expect all of the references to be BBox representations
        all_refs = pm.listReferences()
        self.assertTrue(all_refs[0].is_repr('BBox'))
        self.assertTrue(all_refs[1].is_repr('BBox'))
        self.assertTrue(all_refs[2].is_repr('BBox'))

    def test_save_as_in_another_project_updates_paths_correctly(self):
        """testing if the external paths are updated correctly if the document
        is created in one maya project but it is saved under another one.
        """
        # create a new scene
        # save it under one Asset Version with name Asset1

        asset1 = Asset(
            name='Asset1',
            code='Ass1',
            type=self.character_type,
            project=self.project
        )
        DBSession.add(asset1)
        DBSession.commit()

        version1 = Version(task=asset1)
        DBSession.add(version1)
        DBSession.commit()

        version_ref1 = Version(
            task=asset1,
            take_name="References1"
        )
        DBSession.add(version_ref1)
        DBSession.commit()

        version_ref2 = Version(
            task=asset1,
            take_name="References2"
        )
        DBSession.add(version_ref2)
        DBSession.commit()

        # save a maya file with this references
        pm.newFile(f=True)
        self.maya_env.save_as(version_ref1)
        self.maya_env.save_as(version_ref2)

        # save the original version
        self.maya_env.save_as(version1)

        # create a couple of file textures
        file_texture1 = pm.createNode("file")
        file_texture2 = pm.createNode("file")

        path1 = Repository.to_os_independent_path(
            os.path.join(
                version1.absolute_path, ".maya_files/TEXTURES/a.jpg"
            )
        )
        path2 = Repository.to_os_independent_path(
            os.path.join(
                version1.absolute_path, ".maya_files/TEXTURES/b.jpg"
            )
        )

        # set them to some relative paths
        file_texture1.fileTextureName.set(path1)
        file_texture2.fileTextureName.set(path2)

        # create a couple of references in the same project
        self.maya_env.reference(version_ref1)
        self.maya_env.reference(version_ref2)

        # save again
        self.maya_env.save_as(version1)

        # then save it under another Asset with name Asset2
        # because with this new system all the Assets folders are a maya
        # project, the references should be updated correctly
        asset2 = Asset(
            name='Asset2',
            code='Ass2',
            type=self.character_type,
            project=self.project
        )
        DBSession.add(asset2)
        DBSession.commit()

        # create a new Version for Asset 2
        version2 = Version(task=asset2)

        # now save it under that asset
        self.maya_env.save_as(version2)

        # check the file paths they should stay intact
        # because they are already under the repository so no need to change
        # the path
        self.assertEqual(file_texture1.fileTextureName.get(), path1)
        self.assertEqual(file_texture2.fileTextureName.get(), path2)

    def test_save_as_sets_the_fps(self):
        """testing if the save_as method sets the fps value correctly
        """
        # create two projects with different fps values
        # first create a new scene and save it under the first project
        # and then save it under the other project
        # and check if the fps follows the project values

        project1 = Project(
            name="FPS Test Project 1",
            code='FTP1',
            status_list=self.project_status_list,
            structure=self.structure,
            repositories=[self.repo1],
            fps=24,
            image_format=self.image_format
        )
        DBSession.add(project1)

        project2 = Project(
            name="FPS Test Project 2",
            code='FTP2',
            status_list=self.project_status_list,
            structure=self.structure,
            repositories=[self.repo1],
            fps=30,
            image_format=self.image_format
        )
        DBSession.add(project2)

        # create assets
        asset1 = Asset(
            name="Test Asset 1",
            code='TA1',
            project=project1,
            type=self.character_type
        )
        DBSession.add(asset1)

        asset2 = Asset(
            name="Test Asset 2",
            code='TA2',
            project=project2,
            type=self.character_type
        )
        DBSession.add(asset2)
        DBSession.commit()

        # create versions
        version1 = Version(
            task=asset1,
            created_by=self.user1
        )
        DBSession.add(version1)
        DBSession.commit()

        version2 = Version(
            task=asset2,
            created_by=self.user1
        )
        DBSession.add(version2)
        DBSession.commit()

        # save the current scene for asset1
        self.maya_env.save_as(version1)

        # check the fps value
        self.assertEqual(
            self.maya_env.get_fps(),
            24
        )

        # now save it for asset2
        self.maya_env.save_as(version2)

        # check the fps value
        self.assertEqual(
            self.maya_env.get_fps(),
            30
        )

    def test_reference_creates_references_with_absolute_paths_containing_env_var(self):
        """testing if reference method creates references with unresolved paths
        are absolute paths containing repo env var
        """
        vers1 = Version(task=self.asset1, created_by=self.user1)
        DBSession.add(vers1)
        DBSession.commit()

        vers2 = Version(task=self.asset1, created_by=self.user1)
        DBSession.add(vers2)
        DBSession.commit()

        self.maya_env.save_as(vers1)

        pm.newFile(force=True)
        self.maya_env.save_as(vers2)

        # reference vers1 to vers2
        ref = self.maya_env.reference(vers1)

        # now check if the referenced files unresolved path is equal to
        # ver2.absolute_full_path
        refs = pm.listReferences()

        # there should be only one reference
        self.assertEqual(len(refs), 1)

        # the unresolved path should be an absolute path
        self.assertEqual(
            Repository.to_os_independent_path(vers1.absolute_full_path),
            ref.unresolvedPath()
        )

        self.assertTrue(ref.isLoaded())

    def test_reference_creates_references_of_representations_with_correct_namespace(self):
        """testing if references of representations will be referenced with
        correct namespace
        """
        pm.newFile(force=True)
        a_base_v3 = self.create_version(self.asset1, 'Main')
        a_bbox_v1 = self.create_version(self.asset1, 'Main@BBox', a_base_v3)
        pm.newFile(force=True)

        ref = self.maya_env.reference(a_bbox_v1)
        self.assertEqual(ref.namespace, os.path.basename(a_base_v3.nice_name))

    def test_save_as_replaces_image_plane_filename_with_env_variable(self):
        """testing if save_as replaces the imagePlane filename with repository
        environment variable
        """
        absolute_path = os.path.join(
            self.asset1.absolute_path,
            'Plate/plateA.1.jpg'
        )

        # create an image plane
        image_plane = pm.createNode('imagePlane')

        # and set the path to something absolute
        image_plane.setAttr('imageName', absolute_path)

        vers1 = Version(task=self.asset1, created_by=self.user1)
        DBSession.add(vers1)
        DBSession.commit()

        # save the scene
        self.maya_env.save_as(vers1)

        # check if the path is replaced with repository environment variable
        self.assertEqual(
            Repository.to_os_independent_path(absolute_path),
            image_plane.getAttr('imageName')
        )

    def test_save_as_will_even_replace_paths_if_they_are_referenced(self):
        """testing if save_as will even replace external paths of referenced
        nodes
        """
        absolute_path = os.path.normpath(
            os.path.join(
                self.asset1.absolute_path,
                'Plate/plateA.1.jpg'
            )
        )

        normal_path = os.path.normpath(
            os.path.join(
                self.asset1.path,
                'Plate/plateA.1.jpg'
            )
        )

        # create an image plane
        image_plane = pm.createNode('imagePlane')

        # and set the path to something absolute
        image_plane.setAttr('imageName', absolute_path)

        vers1 = Version(task=self.asset1, created_by=self.user1)
        DBSession.add(vers1)
        DBSession.commit()

        # save the scene
        self.maya_env.save_as(vers1)

        # re-set to absolute path
        image_plane.setAttr('imageName', absolute_path)

        # save again
        pm.saveFile()

        self.assertEqual(
            image_plane.getAttr('imageName'),
            absolute_path
        )

        vers2 = Version(task=self.asset1, created_by=self.user1)
        DBSession.add(vers2)
        DBSession.commit()

        # save the scene as a different version
        pm.newFile(f=1)
        self.maya_env.reference(vers1)
        self.maya_env.save_as(vers2)

        image_plane = pm.ls(type='imagePlane')[0]

        # check if the path is not replaced
        self.assertEqual(
            os.path.normpath(normal_path),
            os.path.normpath(image_plane.getAttr('imageName'))
        )

    def test_save_as_creates_the_workspace_mel_file_in_the_given_path(self):
        """testing if save_as creates the workspace.mel file in the Asset or
        Shot root
        """
        task6 = Task(
            name='Test Task 6 - New',
            parent=self.task1
        )
        DBSession.add(task6)
        DBSession.commit()

        version1 = Version(task=task6)
        version1.extension = '.ma'
        version1.update_paths()

        # check if the workspace.mel file does not exist yet
        workspace_mel_full_path = os.path.join(
            version1.absolute_path,
            'workspace.mel'
        )
        self.assertFalse(os.path.exists(workspace_mel_full_path))
        self.maya_env.save_as(version1)
        self.assertTrue(os.path.exists(workspace_mel_full_path))

    def test_save_as_creates_the_workspace_fileRule_folders(self):
        """testing if save_as creates the fileRule folders
        """
        task6 = Task(
            name='Test Task 6 - New',
            parent=self.task1
        )
        DBSession.add(task6)
        DBSession.commit()

        version1 = Version(task=task6)
        version1.extension = '.ma'
        version1.update_paths()

        # first prove that the folders doesn't exist
        for key in pm.workspace.fileRules.keys():
            file_rule_partial_path = pm.workspace.fileRules[key]
            file_rule_full_path = os.path.join(
                version1.absolute_path,
                file_rule_partial_path
            )
            self.assertFalse(os.path.exists(file_rule_full_path))

        self.maya_env.save_as(version1)

        # save_as and now expect the folders to be created
        for key in pm.workspace.fileRules.keys():
            file_rule_partial_path = pm.workspace.fileRules[key]
            file_rule_full_path = os.path.join(
                version1.absolute_path,
                file_rule_partial_path
            )
            self.assertTrue(os.path.exists(file_rule_full_path))

    def test_is_in_repo_working_properly(self):
        """testing if Maya.is_in_repo() is working properly
        """
        repo_path = self.repo1.path

        self.assertTrue(
            self.maya_env.is_in_repo(repo_path)
        )
        self.assertTrue(
            self.maya_env.is_in_repo(
                os.path.join(repo_path, 'a.txt')
            )
        )
        self.assertFalse(
            self.maya_env.is_in_repo(
                os.path.normpath(
                    os.path.join(repo_path, '../a.txt')
                )
            )
        )

    def test_move_to_local_is_working_properly(self):
        """testing if Maya.move_to_local is working properly
        """
        # create a couple of files in some other directories than repo
        another_tmp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(another_tmp_dir, 'test.png')

        with open(temp_file_path, 'w'):
            pass

        # add the file to be cleaned up list
        self.remove_these_files_buffer.append(temp_file_path)
        self.remove_these_files_buffer.append(another_tmp_dir)

        # now create a version and move the file to the local path of this
        # version
        version = Version(task=self.task1)
        version.extension = '.ma'
        version.update_paths()
        DBSession.add(version)
        DBSession.commit()

        new_path =\
            self.maya_env.move_to_local(version, temp_file_path, 'Textures')
        self.remove_these_files_buffer.append(new_path)

        # check if the file is there
        self.assertTrue(
            os.path.exists(new_path)
        )

    def test_update_first_level_versions_does_not_update_namespaces(self):
        """testing if update_first_level_versions method does not updates
        namespaces
        """
        vers1 = Version(task=self.asset1, created_by=self.user1)
        DBSession.add(vers1)
        DBSession.commit()

        vers2 = Version(task=self.asset1, created_by=self.user1, take_name='A')
        vers2.is_published = True
        DBSession.add(vers2)
        DBSession.commit()

        vers3 = Version(task=self.asset1, created_by=self.user1, take_name='A')
        vers3.is_published = True
        DBSession.add(vers3)
        DBSession.commit()

        pm.newFile(force=True)
        self.maya_env.save_as(vers2)

        pm.newFile(force=True)
        self.maya_env.save_as(vers3)

        self.maya_env.save_as(vers1)

        # reference vers2 to vers1
        self.maya_env.reference(vers2)

        # now check if the referenced files unresolved path is equal to
        # ver2.absolute_full_path
        refs = pm.listReferences()

        # there should be only one reference
        self.assertEqual(len(refs), 1)

        # the unresolved path should be an absolute path
        self.assertEqual(
            vers2.absolute_full_path,
            refs[0].path
        )

        self.assertTrue(refs[0].isLoaded())

        # update version to latest published version
        reference_resolution = {
            'root': [vers2],
            'create': [vers1],
            'update': [vers2],
            'leave': []
        }
        self.maya_env.update_first_level_versions(reference_resolution)

        # now check if the reference is updated and the namespace is set
        # correctly
        refs = pm.listReferences()
        self.assertEqual(
            vers3.absolute_full_path,
            refs[0].path
        )
        self.assertEqual(
            refs[0].namespace,
            vers2.nice_name
        )


class MayaReferenceUpdateTestCase(MayaTestBase):
    """tests the maya.Maya reference updates
    """

    def test_update_versions_is_working_properly_case_1(self):
        """testing if update_versions is working properly in following
        condition:

        Start Condition:

        version12
          version5
            version2 -> has new published version (version3)

        Expected Result:

        version12 (no new version based on version12)
          version5 (no new version based on version5)
            version2 (do not update version2)
        """
        # create a deep relation
        self.version2.is_published = True

        # new scene
        # version5 references version2
        self.maya_env.open(self.version5)
        self.maya_env.reference(self.version2)
        pm.saveFile()
        self.version5.is_published = True
        pm.newFile(force=True)

        # version12 references version5
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version5)
        pm.saveFile()
        self.version12.is_published = True
        pm.newFile(force=True)

        # version3 set published
        self.version3.is_published = True

        # check the setup
        visited_versions = []
        for v in self.version12.walk_inputs():
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version12, self.version5, self.version2]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        reference_resolution = self.maya_env.open(self.version12)
        updated_versions = \
            self.maya_env.update_versions(reference_resolution)

        # we should be still in version12 scene
        self.assertEqual(
            self.version12,
            self.maya_env.get_current_version()
        )

        # check references
        # we shouldn't have a new version5 referenced
        refs = pm.listReferences()
        self.assertEqual(
            self.version5,
            self.maya_env.get_version_from_full_path(refs[0].path)
        )

        # and it should still have referencing version2
        refs = pm.listReferences(refs[0])
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(refs[0].path)
        )

    def test_update_versions_is_working_properly_case_2(self):
        """testing if update_versions is working properly in following
        condition:

        Start Condition:

        version6 -> new version of version5 is already referencing version6
          version3 (so version6 is already using version3 and both are
                    published)

        version12
          version5 -> has new published version (version6)
            version2 -> has new published version (version3)

        Expected Final Result
        version12
          version6 -> 1st level reference is updated correctly
            version3
        """
        # create a deep relation
        self.version2.is_published = True

        # new scene
        # version5 references version2
        self.maya_env.open(self.version5)
        self.maya_env.reference(self.version2)
        pm.saveFile()
        self.version5.is_published = True
        pm.newFile(force=True)

        # version6 references version3
        self.maya_env.open(self.version6)
        self.maya_env.reference(self.version3)
        pm.saveFile()
        self.version6.is_published = True
        pm.newFile(force=True)

        # version12 references version5
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version5)
        pm.saveFile()
        self.version12.is_published = True
        pm.newFile(force=True)

        # version3 set published
        self.version3.is_published = True
        self.version6.is_published = True

        # check the setup
        visited_versions = []
        for v in self.version12.walk_inputs():
            visited_versions.append(v)

        expected_visited_versions = \
            [self.version12, self.version5, self.version2]

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        reference_resolution = self.maya_env.open(self.version12)
        created_versions = \
            self.maya_env.update_versions(reference_resolution)

        # no new versions should have been created
        self.assertEqual(0, len(created_versions))

        # check if we are still in version12 scene
        self.assertEqual(
            self.version12,
            self.maya_env.get_current_version()
        )

        # and expect maya have the updated references
        refs = pm.listReferences()
        self.assertEqual(
            self.version6,
            self.maya_env.get_version_from_full_path(refs[0].path)
        )

        # and it should have referenced version3
        refs = pm.listReferences(refs[0])
        self.assertEqual(
            self.version3,
            self.maya_env.get_version_from_full_path(refs[0].path)
        )

    def test_update_versions_is_working_properly_case_3(self):
        """testing if update_versions is working properly in following
        condition:

        Start Condition:

        version15
          version12
            version5
              version2 -> has new published version (version3)
          version12 -> referenced a second time
            version5
              version2 -> has new published version (version3)

        Expected Final Result
        version15
          version12
            version5
              version2 -> it is not a 1st level reference, nothing is updated
          version12
            version5
              version2 -> nothing is updated
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # new scene
        # version5 references version2
        self.maya_env.open(self.version5)
        self.maya_env.reference(self.version2)
        pm.saveFile()
        self.version5.is_published = True
        pm.newFile(force=True)

        # version12 references version5
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version5)
        pm.saveFile()
        self.version12.is_published = True
        pm.newFile(force=True)

        # version15 references version12 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version12)
        self.maya_env.reference(self.version12)
        pm.saveFile()
        pm.newFile(force=True)

        # check the setup
        visited_versions = []
        for v in self.version15.walk_inputs():
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version12, self.version5, self.version2]

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )
        reference_resolution = self.maya_env.open(self.version15)

        # check reference resolution
        self.assertEqual(
            sorted(reference_resolution['root'], key=lambda x: x.name),
            sorted([self.version12], key=lambda x: x.name)
        )
        self.assertEqual(
            sorted(reference_resolution['create'], key=lambda x: x.name),
            sorted([self.version5, self.version12], key=lambda x: x.name)
        )
        self.assertEqual(
            sorted(reference_resolution['update'], key=lambda x: x.name),
            sorted([self.version2], key=lambda x: x.name)
        )
        self.assertEqual(
            reference_resolution['leave'],
            []
        )

        updated_versions = \
            self.maya_env.update_versions(reference_resolution)

        self.assertEqual(0, len(updated_versions))

        # check if we are still in version15 scene
        self.assertEqual(
            self.version15,
            self.maya_env.get_current_version()
        )

        # and expect maya have the updated references
        refs_level1 = pm.listReferences()
        self.assertEqual(
            self.version12,
            self.maya_env.get_version_from_full_path(refs_level1[0].path)
        )
        self.assertEqual(
            self.version12,
            self.maya_env.get_version_from_full_path(refs_level1[1].path)
        )

        # and it should have referenced version5A
        refs_level2 = pm.listReferences(refs_level1[0])
        self.assertEqual(
            self.version5,
            self.maya_env.get_version_from_full_path(refs_level2[0].path)
        )

        # and it should have referenced version5A
        refs_level3 = pm.listReferences(refs_level2[0])
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(refs_level3[0].path)
        )

        # the other version5A
        refs_level2 = pm.listReferences(refs_level1[1])
        self.assertEqual(
            self.version5,
            self.maya_env.get_version_from_full_path(refs_level2[0].path)
        )

        # and it should have referenced version5A
        refs_level3 = pm.listReferences(refs_level2[0])
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(refs_level3[0].path)
        )

    def test_update_versions_is_working_properly_case_4(self):
        """testing if update_versions is working properly in following
        condition:

        Start Condition:

        version15
          version12
            version5
              version2 -> has new published version (version3)
            version5 -> Referenced a second time
              version2 -> has new published version (version3)
          version12 -> Referenced a second time
            version5
              version2 -> has new published version (version3)
            version5
              version2 -> has new published version (version3)

        Expected Final Result
        version15
          version12
            version5
              version2 -> nothing is updated
            version5
              version2 -> nothing is updated
          version12
            version5
              version2 -> nothing is updated
            version5
              version2 -> nothing is updated
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # new scene
        # version5 references version2
        self.maya_env.open(self.version5)
        self.maya_env.reference(self.version2)
        pm.saveFile()
        self.version5.is_published = True
        pm.newFile(force=True)

        # version12 references version5
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version5)
        self.maya_env.reference(self.version5)  # reference a second time
        pm.saveFile()
        self.version12.is_published = True
        pm.newFile(force=True)

        # version15 references version12 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version12)
        self.maya_env.reference(self.version12)
        pm.saveFile()
        pm.newFile(force=True)

        # check the setup
        visited_versions = []
        for v in self.version15.walk_inputs():
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version12, self.version5, self.version2]

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        reference_resolution = self.maya_env.open(self.version15)
        updated_versions = \
            self.maya_env.update_versions(reference_resolution)

        self.assertEqual(0, len(updated_versions))

        # check if we are still in version15 scene
        self.assertEqual(
            self.version15,
            self.maya_env.get_current_version()
        )

        # and expect maya have the updated references
        refs = pm.listReferences()
        version12_ref1 = refs[0]
        version12_ref2 = refs[1]

        refs = pm.listReferences(version12_ref1)
        version5_ref1 = refs[0]
        version5_ref2 = refs[1]

        refs = pm.listReferences(version12_ref2)
        version5_ref3 = refs[0]
        version5_ref4 = refs[1]

        version2_ref1 = pm.listReferences(version5_ref1)[0]
        version2_ref2 = pm.listReferences(version5_ref2)[0]
        version2_ref3 = pm.listReferences(version5_ref3)[0]
        version2_ref4 = pm.listReferences(version5_ref4)[0]

        # Version12
        published_version = self.version12
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version12_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version12_ref2.path)
        )

        # Version5
        published_version = self.version5
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version5_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version5_ref2.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version5_ref3.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version5_ref4.path)
        )

        # Version2
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(version2_ref1.path)
        )
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(version2_ref2.path)
        )
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(version2_ref3.path)
        )
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(version2_ref4.path)
        )

    def test_update_versions_is_working_properly_case_5(self):
        """testing if update_versions is working properly in following
        condition:

        Start Condition:

        version15
          version11 -> has a new version already using version6 (version12)
            version4 -> has a new published version (version6) using version3
              version2 -> has new published version (version3)
            version4 -> Referenced a second time
              version2 -> has new published version (version3)
          version11 -> Referenced a second time
            version4
              version2
            version4
              version2

        Expected Final Result (generates only one new version)
        version15 -> no new version based on version15
          version12
            version6
              version3
            version6
              version3
          version12
            version6
              version3
            version6
              version3
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # version4 references version2
        self.maya_env.open(self.version4)
        self.maya_env.reference(self.version2)
        pm.saveFile()
        self.version4.is_published = True
        pm.newFile(force=True)

        # version6 references version3
        self.maya_env.open(self.version6)
        self.maya_env.reference(self.version3)
        pm.saveFile()
        self.version6.is_published = True
        pm.newFile(force=True)

        # version11 references version5
        self.maya_env.open(self.version11)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)  # reference a second time
        pm.saveFile()
        self.version11.is_published = True
        pm.newFile(force=True)

        # version12 references version6
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version6)
        self.maya_env.reference(self.version6)  # reference a second time
        pm.saveFile()
        self.version12.is_published = True
        pm.newFile(force=True)

        # version15 references version11 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version11)
        self.maya_env.reference(self.version11)
        pm.saveFile()
        pm.newFile(force=True)

        # check the setup
        visited_versions = []
        for v in self.version15.walk_inputs():
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version11, self.version4, self.version2]

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        reference_resolution = self.maya_env.open(self.version15)
        updated_versions = \
            self.maya_env.update_versions(reference_resolution)

        self.assertEqual(0, len(updated_versions))

        # check if we are still in version15 scene
        self.assertEqual(
            self.version15,
            self.maya_env.get_current_version()
        )

        # and expect maya have the updated references
        refs = pm.listReferences()
        version12_ref1 = refs[0]
        version12_ref2 = refs[1]

        refs = pm.listReferences(version12_ref1)
        version6_ref1 = refs[0]
        version6_ref2 = refs[1]

        refs = pm.listReferences(version12_ref2)
        version6_ref3 = refs[0]
        version6_ref4 = refs[1]

        version3_ref1 = pm.listReferences(version6_ref1)[0]
        version3_ref2 = pm.listReferences(version6_ref2)[0]
        version3_ref3 = pm.listReferences(version6_ref3)[0]
        version3_ref4 = pm.listReferences(version6_ref4)[0]

        # Version12
        published_version = self.version12.latest_published_version
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version12_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version12_ref2.path)
        )

        # Version5
        published_version = self.version5.latest_published_version
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version6_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version6_ref2.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version6_ref3.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version6_ref4.path)
        )

        # Version2
        published_version = self.version2.latest_published_version
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version3_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version3_ref2.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version3_ref3.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version3_ref4.path)
        )

    def test_update_versions_is_working_properly_case_6(self):
        """testing if update_versions is working properly in following
        condition:

        Start Condition:

        version15
          version11 -> has a new version already using version6 (version12)
            version4 -> has a new published version (version6) using version3
              version2 -> has new published version (version3)
            version4 -> Referenced a second time
              version3 -> shallow updated before (let see what happens)

        Expected Final Result (generates only one new version)
        version15
          version12
            version6
              version3
            version6
              version3
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # version4 references version2
        self.maya_env.open(self.version4)
        self.maya_env.reference(self.version2)
        pm.saveFile()
        self.version4.is_published = True
        pm.newFile(force=True)

        # version6 references version3
        self.maya_env.open(self.version6)
        self.maya_env.reference(self.version3)
        pm.saveFile()
        self.version6.is_published = True
        pm.newFile(force=True)

        # version11 references version5
        self.maya_env.open(self.version11)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)  # reference a second time
        pm.saveFile()
        self.version11.is_published = True
        pm.newFile(force=True)

        # version12 references version6
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version6)
        self.maya_env.reference(self.version6)  # reference a second time
        pm.saveFile()
        self.version12.is_published = True
        pm.newFile(force=True)

        # version15 references version11 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version11)

        # now simulate a shallow update on version2 -> version3 while under
        # in version4
        refs = pm.listReferences(recursive=1)
        # we should have all the references
        self.assertEqual(self.version2.absolute_full_path, refs[-1].path)
        refs[-1].replaceWith(self.version3.absolute_full_path)

        pm.saveFile()
        pm.newFile(force=True)

        # check the setup
        visited_versions = []
        for v in self.version15.walk_inputs():
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version11, self.version4, self.version2]

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        reference_resolution = self.maya_env.open(self.version15)
        updated_versions = \
            self.maya_env.update_versions(reference_resolution)

        self.assertEqual(0, len(updated_versions))

        # check if we are still in version15 scene
        self.assertEqual(
            self.version15,
            self.maya_env.get_current_version()
        )

        # and expect maya have the updated references
        refs = pm.listReferences()
        version12_ref1 = refs[0]

        refs = pm.listReferences(version12_ref1)
        version6_ref1 = refs[0]
        version6_ref2 = refs[1]

        version3_ref1 = pm.listReferences(version6_ref1)[0]
        version3_ref2 = pm.listReferences(version6_ref2)[0]

        # Version12
        published_version = self.version12.latest_published_version
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version12_ref1.path)
        )

        # Version5
        published_version = self.version5.latest_published_version
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version6_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version6_ref2.path)
        )

        # Version2
        published_version = self.version2.latest_published_version
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version3_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version3_ref2.path)
        )

    def test_reference_updates_version_inputs_attribute(self):
        """testing if Maya.reference updates Version.inputs attribute
        """
        # create references to various versions
        self.maya_env.open(self.version6)

        self.maya_env.reference(self.version5)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version3)

        # at this point we should have self.version6.inputs filled correctly
        self.assertEqual(
            sorted([self.version5, self.version4, self.version3],
                   key=lambda x: x.name),
            sorted(self.version6.inputs, key=lambda x: x.name)
        )

    def test_get_referenced_versions_returns_a_list_of_Version_instances(self):
        """testing if Maya.get_referenced_versions returns a list of Versions
        instances referenced in the current scene
        """
        # create references to various versions
        self.maya_env.open(self.version6)

        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version5)
        self.maya_env.reference(self.version5)  # duplicate refs
        self.maya_env.reference(self.version4)  # duplicate refs
        self.maya_env.reference(self.version3)

        # now try to get the referenced versions
        referenced_versions = self.maya_env.get_referenced_versions()

        self.assertEqual(
            sorted(referenced_versions, key=lambda x: x.name),
            sorted([self.version3, self.version4, self.version5],
                   key=lambda x: x.name)
        )

    def test_get_referenced_versions_returns_a_list_of_Version_instances_even_with_representations(self):
        """testing if Maya.get_referenced_versions returns a list of Versions
        instances referenced in the current scene
        """
        from stalker import User, LocalSession
        u = User.query.first()
        l = LocalSession()
        l.store_user(u)
        l.save()

        gen = RepresentationGenerator()

        gen.version = self.version4
        gen.generate_all()

        gen.version = self.version5
        gen.generate_all()

        gen.version = self.version3
        gen.generate_all()

        # create references to various versions
        self.maya_env.open(self.version6)

        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version5)
        self.maya_env.reference(self.version5)  # duplicate refs
        self.maya_env.reference(self.version4)  # duplicate refs
        self.maya_env.reference(self.version3)

        # switch all references to bbox representation
        for ref in pm.listReferences():
            ref.to_repr('ASS')

        # now try to get the referenced versions
        referenced_versions = self.maya_env.get_referenced_versions()

        self.assertEqual(
            sorted(referenced_versions, key=lambda x: x.name),
            sorted([self.version3, self.version5],  # version4 will be skipped
                   key=lambda x: x.name)
        )

    def test_get_referenced_versions_returns_a_list_of_Version_instances_referenced_under_the_given_reference(self):
        """testing if Maya.get_referenced_versions returns a list of Versions
        referenced in the current scene under the given reference
        """
        # create references to various versions
        self.maya_env.open(self.version6)

        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version5)
        self.maya_env.reference(self.version5)  # duplicate refs
        self.maya_env.reference(self.version4)  # duplicate refs
        self.maya_env.reference(self.version3)

        # save the scene and start
        pm.saveFile()

        # open version7 and reference version6 to it
        self.maya_env.open(self.version7)
        self.maya_env.reference(self.version6)

        # now try to get the referenced versions
        versions = self.maya_env.get_referenced_versions()

        self.assertEqual(
            sorted(versions, key=lambda x: x.name),
            sorted([self.version6], key=lambda x: x.name)
        )

        # and get a deeper one
        versions = \
            self.maya_env.get_referenced_versions(
                pm.listReferences()[0]
            )

        self.assertEqual(
            sorted(versions, key=lambda x: x.name),
            sorted([self.version3, self.version4, self.version5],
                   key=lambda x: x.name)
        )

    def test_update_version_inputs_method_updates_the_inputs_of_the_open_version(self):
        """testing if Maya.update_version_inputs() returns updates the inputs
        attribute of the current open version by looking to the referenced
        versions
        """
        # do not use maya_env to open and reference files
        # create references to various versions
        def open_(version):
            new_workspace = version.absolute_path
            pm.workspace.open(new_workspace)
            pm.openFile(version.absolute_full_path, f=True,)

        # create references
        def reference(version):
            namespace = os.path.basename(version.filename)
            namespace = namespace.replace('.', '_')
            ref = pm.createReference(
                version.absolute_full_path,
                gl=True,
                namespace=namespace,
                options='v=0'
            )

        open_(self.version6)
        reference(self.version4)
        reference(self.version5)
        reference(self.version5)  # duplicate refs
        reference(self.version4)  # duplicate refs
        reference(self.version3)

        # save the scene and start
        pm.saveFile()

        # the version6.inputs should be an empty list
        self.assertEqual(self.version6.inputs, [])

        # open version7 and reference version6 to it
        open_(self.version7)
        reference(self.version6)

        # version7.inputs should be an empty list
        self.assertEqual(self.version7.inputs, [])

        # now try to update referenced versions
        self.maya_env.update_version_inputs()

        self.assertEqual(
            [self.version6],
            self.version7.inputs
        )

        # now get the version6.inputs right
        refs = pm.listReferences()
        self.maya_env.update_version_inputs(refs[0])

        self.assertEqual(
            sorted([self.version3, self.version4, self.version5],
                   key=lambda x: x.name),
            sorted(self.version6.inputs, key=lambda x: x.name)
        )

    def test_reference_method_updates_the_inputs_of_the_referenced_version(self):
        """testing if Maya.reference() method updates the Version.inputs of the
        referenced version
        """
        # create a new version
        self.maya_env.open(self.version6)

        # check prior to referencing
        self.assertTrue(self.version5 not in self.version6.inputs)

        # reference something and let Maya to update the inputs
        self.maya_env.reference(self.version5)

        # check if version5 is in version6.inputs
        self.assertTrue(self.version5 in self.version6.inputs)

        # remove the reference and save the file (do not saveAs)
        pm.listReferences()[0].remove()

        # save the file over itself
        pm.saveFile()

        # check if version5 still in version6.inputs
        self.assertTrue(self.version5 in self.version6.inputs)

        # create a new scene and reference the previous version and check if
        pm.newFile(f=True)
        self.maya_env.reference(self.version6)

        # the Version.inputs is updated correctly
        self.assertTrue(self.version5 not in self.version6.inputs)

    def test_check_referenced_versions_is_working_properly(self):
        """testing if check_referenced_versions will return a list of tuples
        holding info like which ref needs to be updated or which reference
        needs a new version, what is the corresponding Version instance and
        what is the final action

        Start Condition:

        version15
          version11 -> has a new version already using version6 (version12)
            version4 -> has a new published version (version6) using version3
              version2 -> has new published version (version3)
            version4 -> Referenced a second time
              version2 -> has new published version (version3)
          version11 -> Referenced a second time
            version4
              version2
            version4
              version2
          version21
            version16 -> has a new published version version18
          version38 -> no update
            version27 -> no update

        Expected Final Result (generates only one new version)
        version15 -> same version of version15
          version12
            version6
              version3
            version6
              version3
          version12
            version6
              version3
            version6
              version3
          version21 -> same version of version21
            version18
          version38 -> no update
            version27 -> no update
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # version4 references version2
        self.maya_env.open(self.version4)
        self.maya_env.reference(self.version2)
        pm.saveFile()
        self.version4.is_published = True
        pm.newFile(force=True)

        # version6 references version3
        self.maya_env.open(self.version6)
        self.maya_env.reference(self.version3)
        pm.saveFile()
        self.version6.is_published = True
        pm.newFile(force=True)

        # version11 references version5
        self.maya_env.open(self.version11)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)  # reference a second time
        pm.saveFile()
        self.version11.is_published = True
        pm.newFile(force=True)

        # version12 references version6
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version6)
        self.maya_env.reference(self.version6)  # reference a second time
        pm.saveFile()
        self.version12.is_published = True
        pm.newFile(force=True)

        # version21 references version16
        self.maya_env.open(self.version21)
        self.maya_env.reference(self.version16)
        pm.saveFile()
        self.version16.is_published = True
        self.version18.is_published = True
        self.version21.is_published = True
        pm.newFile(force=True)

        # version38 references version27
        self.maya_env.open(self.version38)
        self.maya_env.reference(self.version27)
        pm.saveFile()
        self.version38.is_published = True
        self.version27.is_published = True
        pm.newFile(force=True)

        # version15 references version11 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version11)
        self.maya_env.reference(self.version11)
        self.maya_env.reference(self.version21)
        self.maya_env.reference(self.version38)
        pm.saveFile()
        #pm.newFile(force=True)
        DBSession.commit()

        # check the setup
        visited_versions = []
        for v in self.version15.walk_inputs():
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version11, self.version4, self.version2,
             self.version21, self.version16, self.version38, self.version27]

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        root_refs = pm.listReferences()

        version11_ref_1 = root_refs[0]
        version4_ref_1 = pm.listReferences(version11_ref_1)[0]
        version2_ref_1 = pm.listReferences(version4_ref_1)[0]
        version4_ref_2 = pm.listReferences(version11_ref_1)[1]
        version2_ref_2 = pm.listReferences(version4_ref_2)[0]

        version11_ref_2 = root_refs[1]
        version4_ref_3 = pm.listReferences(version11_ref_2)[0]
        version2_ref_3 = pm.listReferences(version4_ref_3)[0]
        version4_ref_4 = pm.listReferences(version11_ref_2)[1]
        version2_ref_4 = pm.listReferences(version4_ref_4)[0]

        version21_ref = root_refs[2]
        version16_ref = pm.listReferences(version21_ref)[0]

        version38_ref = root_refs[3]
        version27_ref = pm.listReferences(version38_ref)[0]

        self.assertFalse(self.version2.is_latest_published_version())

        expected_reference_resolution = {
            'root': [
                self.version38,
                self.version11,
                self.version21
            ],
            'leave': [
                self.version27,
                self.version38
            ],
            'update': [
                self.version16,
                self.version2,
                self.version4,
                self.version11
            ],
            'create': [
                self.version21
            ]
        }

        result = \
            self.maya_env.check_referenced_versions()

        # print('self.version27: %s' % self.version27)
        # print('self.version38: %s' % self.version38)
        # print('self.version16: %s' % self.version16)
        # print('self.version21: %s' % self.version21)
        # print('self.version2 : %s' % self.version2)
        # print('self.version4 : %s' % self.version4)
        # print('self.version11: %s' % self.version11)
        # print('self.version15: %s' % self.version15)
        #
        # print(expected_reference_resolution)
        # print('--------------------------')
        # print(result)

        self.assertEqual(
            sorted(expected_reference_resolution['root'],
                   key=lambda x: x.name),
            sorted(result['root'], key=lambda x: x.name)
        )
        self.assertEqual(
            sorted(expected_reference_resolution['leave'],
                   key=lambda x: x.name),
            sorted(result['leave'],
                   key=lambda x: x.name)
        )
        self.assertEqual(
            sorted(expected_reference_resolution['update'],
                   key=lambda x: x.name),
            sorted(result['update'],
                   key=lambda x: x.name)
        )
        self.assertEqual(
            sorted(expected_reference_resolution['create'],
                   key=lambda x: x.name),
            sorted(result['create'],
                   key=lambda x: x.name)
        )

    def test_check_referenced_versions_is_working_properly_case_2(self):
        """testing if check_referenced_versions will return a dictionary holding
        info like which ref needs to be updated or which reference needs a new
        version, what is the corresponding Version instance and what is the
        final action, even if the 2nd level of references has an update

        Start Condition:

        version15 -> has no new version
          version11 -> has no new version
            version4 -> has no new version
              version2 -> has new published version (version3)

        Expected Final Result (generates only one new version)
        version15 -> create
          version11 -> create
            version4 -> create
              version2 -> update
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # version4 references version2
        self.maya_env.open(self.version4)
        self.maya_env.reference(self.version2)
        pm.saveFile()
        self.version4.is_published = True
        pm.newFile(force=True)

        # version11 references version4
        self.maya_env.open(self.version11)
        self.maya_env.reference(self.version4)
        pm.saveFile()
        self.version11.is_published = True
        pm.newFile(force=True)

        # version15 references version11 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version11)
        pm.saveFile()

        DBSession.commit()

        # check the setup
        visited_versions = []
        for v in self.version15.walk_inputs():
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version11, self.version4, self.version2]

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        expected_reference_resolution = {
            'root': [self.version11],
            'leave': [],
            'update': [self.version2],
            'create': [self.version4, self.version11]
        }

        result = \
            self.maya_env.check_referenced_versions()

        # print('self.version15.id: %s' % self.version15.id)
        # print('self.version11.id: %s' % self.version11.id)
        # print('self.version4.id : %s' % self.version4.id)
        # print('self.version2.id : %s' % self.version2.id)
        #
        # print(expected_reference_resolution)
        # print('--------------------------')
        # print(result)

        self.assertEqual(
            sorted(expected_reference_resolution['root'],
                   key=lambda x: x.name),
            sorted(result['root'], key=lambda x: x.name)
        )
        self.assertEqual(
            sorted(expected_reference_resolution['leave'],
                   key=lambda x: x.name),
            sorted(result['leave'], key=lambda x: x.name)
        )
        self.assertEqual(
            sorted(expected_reference_resolution['update'],
                   key=lambda x: x.name),
            sorted(result['update'], key=lambda x: x.name)
        )
        self.assertEqual(
            sorted(expected_reference_resolution['create'],
                   key=lambda x: x.name),
            sorted(result['create'], key=lambda x: x.name)
        )


class MayaFixReferenceNamespaceTestCase(MayaTestBase):
    """Tests Maya.fix_reference_namespace() method
    """

    def test_fix_reference_namespace_is_working_properly(self):
        """testing if the fix_reference_namespace method is working properly

        version15 -> has no new version
          version11 -> has no new version
            version4 -> has no new version
              version2 -> has no new version

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pm.spaceLocator()
        loc.t.set(0, 0, 0)
        pm.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # lookdev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pm.saveFile()

        pm.newFile(force=True)
        # version11 references version4
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pm.listReferences()
        version4_ref_node = refs[0]
        version4_ref_node.namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there is only one locator in the current scene
        loc = pm.ls(type=pm.nt.Transform)
        loc[0].t.set(1, 0, 0)
        # we should have created an edit
        version2_ref_node = pm.listReferences(version4_ref_node)[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pm.saveFile()
        pm.newFile(force=True)

        # version15 references version11 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version11)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version11.filename.replace('.', '_')
        pm.saveFile()

        DBSession.commit()

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now let it be fixed
        self.maya_env.fix_reference_namespaces()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, scs=1)),
            1
        )

        # and check if the locator is in 1, 0, 0
        loc = pm.ls(type=pm.nt.Transform)[0]
        self.assertEqual(loc.tx.get(), 1.0)
        self.assertEqual(loc.ty.get(), 0.0)
        self.assertEqual(loc.tz.get(), 0.0)
        pm.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_duplicate_refs(self):
        """testing if the fix_reference_namespace method is working properly
        with duplicate references

        version15 -> has no new version
          version11 -> has no new version
            version4 -> has no new version
              version2 -> has no new version
          version11 -> has no new version
            version4 -> has no new version
              version2 -> has no new version

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pm.spaceLocator()
        loc.t.set(0, 0, 0)
        pm.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # lookdev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pm.saveFile()

        # version11 references version4
        pm.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pm.listReferences()
        version4_ref_node = refs[0]
        version4_ref_node.namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be two locators in the current scene
        loc = pm.ls(type=pm.nt.Transform)
        loc[0].t.set(1, 0, 0)

        # we should have created an edit
        version2_ref_node = pm.listReferences(version4_ref_node)[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pm.saveFile()
        pm.newFile(force=True)

        # version15 references version11 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version11)
        self.maya_env.reference(self.version11)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version11.filename.replace('.', '_')
        refs[1].namespace = self.version11.filename.replace('.', '_')
        pm.saveFile()

        DBSession.commit()

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # the second copy
        self.assertEqual(
            all_refs[3].namespace,
            '%s1' % self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[4].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[5].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now let it be fixed
        self.maya_env.fix_reference_namespaces()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[3].namespace,
            'Test_Task_1_Test_Task_5_Take2'
        )

        self.assertEqual(
            all_refs[4].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[5].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # now check we don't have any failed edits
        self.assertEqual(
            len(pm.referenceQuery(all_refs[3], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[4], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[5], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, scs=1)),
            1
        )

        # and we have all successful edits
        self.assertEqual(
            len(pm.referenceQuery(all_refs[3], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[4], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[5], es=1, scs=1)),
            1
        )

        # and check if the locator is in 1, 0, 0
        locs = pm.ls(type=pm.nt.Transform)
        self.assertEqual(locs[0].tx.get(), 1.0)
        self.assertEqual(locs[0].ty.get(), 0.0)
        self.assertEqual(locs[0].tz.get(), 0.0)

        # the second locator
        self.assertEqual(locs[1].tx.get(), 1.0)
        self.assertEqual(locs[1].ty.get(), 0.0)
        self.assertEqual(locs[1].tz.get(), 0.0)
        pm.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_shallower_duplicate_refs(self):
        """testing if the fix_reference_namespace method is working properly
        with duplicate references

          version11 -> has no new version ->Layout
            version4 -> has no new version -> LookDev
              version2 -> has no new version -> Model
            version4 -> has no new version
              version2 -> has no new version
            version4 -> has no new version
              version2 -> has no new version
            version4 -> has no new version
              version2 -> has no new version

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pm.spaceLocator()
        loc.t.set(0, 0, 0)
        pm.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pm.saveFile()

        # version11 references version4 four times
        pm.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        refs[1].namespace = self.version4.filename.replace('.', '_')
        refs[2].namespace = self.version4.filename.replace('.', '_')
        refs[3].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be four locators in the current scene
        loc = pm.ls(type=pm.nt.Transform)
        loc[0].t.set(1, 0, 0)
        loc[1].t.set(2, 0, 0)
        loc[2].t.set(3, 0, 0)
        loc[3].t.set(4, 0, 0)

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        version2_ref_node = pm.listReferences(refs[1])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        version2_ref_node = pm.listReferences(refs[2])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        version2_ref_node = pm.listReferences(refs[3])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pm.saveFile()
        DBSession.commit()

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        # the second copy
        self.assertEqual(
            all_refs[2].namespace,
            '%s%s' % (self.version4.filename.replace('.', '_'),
                      all_refs[2].copyNumberList()[1])
        )

        self.assertEqual(
            all_refs[3].namespace,
            self.version2.filename.replace('.', '_')
        )

        # the third copy
        self.assertEqual(
            all_refs[4].namespace,
            '%s%s' % (self.version4.filename.replace('.', '_'),
                      all_refs[4].copyNumberList()[2])
        )

        self.assertEqual(
            all_refs[5].namespace,
            self.version2.filename.replace('.', '_')
        )

        # the forth copy
        self.assertEqual(
            all_refs[6].namespace,
            '%s%s' % (self.version4.filename.replace('.', '_'),
                      all_refs[6].copyNumberList()[3])
        )

        self.assertEqual(
            all_refs[7].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now let it be fixed
        self.maya_env.fix_reference_namespaces()
        pm.saveFile()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.latest_published_version.nice_name
        )

        # second copy
        self.assertEqual(
            all_refs[2].namespace,
            'Asset_2_Take2'
        )

        self.assertEqual(
            all_refs[3].namespace,
            self.version2.latest_published_version.nice_name
        )

        # third copy
        self.assertEqual(
            all_refs[4].namespace,
            'Asset_2_Take3'
        )

        self.assertEqual(
            all_refs[5].namespace,
            self.version2.latest_published_version.nice_name
        )

        # forth copy
        self.assertEqual(
            all_refs[6].namespace,
            'Asset_2_Take4'
        )

        self.assertEqual(
            all_refs[7].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        # second copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[3], es=1, fld=1)),
            0
        )

        # third copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[4], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[5], es=1, fld=1)),
            0
        )

        # forth copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[6], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[7], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        # second copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[3], es=1, scs=1)),
            1
        )

        # third copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[4], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[5], es=1, scs=1)),
            1
        )

        # forth copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[6], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[7], es=1, scs=1)),
            1
        )

        # and check if the locator are where they should be
        locs = pm.ls(type=pm.nt.Transform)
        self.assertTrue(locs[0].tx.get() > 0.5)
        self.assertTrue(locs[1].tx.get() > 0.5)
        self.assertTrue(locs[2].tx.get() > 0.5)
        self.assertTrue(locs[3].tx.get() > 0.5)
        pm.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_refs_with_new_versions(self):
        """testing if the fix_reference_namespace method is working properly
        with references which has new versions

          version11 -> has no new version ->Layout
            version4 -> has no new version -> LookDev
              version2 -> has no new version -> Model -> has a new version3

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version3.is_published = True

        self.version4.is_published = True
        self.version11.is_published = True
        DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pm.spaceLocator()
        loc.t.set(0, 0, 0)
        pm.saveFile()

        # save as version3
        self.maya_env.save_as(self.version3)

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pm.saveFile()

        # version11 references version4 four times
        pm.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be four locators in the current scene
        loc = pm.ls(type=pm.nt.Transform)
        loc[0].t.set(1, 0, 0)

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pm.saveFile()
        DBSession.commit()

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now let it be fixed
        self.maya_env.fix_reference_namespaces()
        pm.saveFile()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.latest_published_version.nice_name
        )

        # check if the reference is created from version2
        self.assertEqual(
            self.maya_env.get_version_from_full_path(all_refs[1].path).parent,
            self.version2
        )

        # and it is version3
        self.assertEqual(
            self.maya_env.get_version_from_full_path(all_refs[1].path),
            self.version3
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        # and check if the locator are where they should be
        locs = pm.ls(type=pm.nt.Transform)
        self.assertEqual(1.0, locs[0].tx.get())
        pm.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_refs_updated_in_a_previous_scene(self):
        """testing if the fix_reference_namespace method is working properly
        with references which are updated in another scene

          version11 -> has no new version ->Layout
            version4 -> has no new version -> LookDev
              version2 -> has no new version -> Model

          version15 -> another scene which is referencing version4
            version4
              version2

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pm.spaceLocator()
        loc.t.set(0, 0, 0)
        pm.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pm.saveFile()

        # version11 references version4
        pm.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        loc = pm.ls(type=pm.nt.Transform)
        loc[0].t.set(1, 0, 0)

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pm.saveFile()
        DBSession.commit()

        # version15 also references version4
        pm.newFile(force=True)
        self.maya_env.open(self.version15)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        loc = pm.ls(type=pm.nt.Transform)
        loc[0].t.set(0, 1, 0)
        pm.saveFile()

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)
        DBSession.commit()

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now fix the namespaces in version15 let it be fixed
        self.maya_env.fix_reference_namespaces()
        pm.saveFile()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)

        version15_version4_path = all_refs[0].path
        version15_version2_path = all_refs[1].path

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        # and check if the locator are where they should be
        locs = pm.ls(type=pm.nt.Transform)
        self.assertEqual(1.0, locs[0].ty.get())
        pm.saveFile()

        # now open version11 and try to fix it also there
        self.maya_env.open(self.version11)

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pm.saveFile()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)

        version11_version4_path = all_refs[0].path
        version11_version2_path = all_refs[1].path

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        # and check if the locator are where they should be
        locs = pm.ls(type=pm.nt.Transform)
        self.assertEqual(1.0, locs[0].tx.get())
        pm.saveFile()

        # check if the two scenes are using the same assets
        self.assertEqual(
            version15_version4_path,
            version11_version4_path
        )
        self.assertEqual(
            version15_version2_path,
            version11_version2_path
        )

    def test_fix_reference_namespace_is_working_properly_with_refs_updated_in_a_previous_scene_deeper(self):
        """testing if the fix_reference_namespace method is working properly
        with references which are updated in another scene

        version15 -> Bigger Layout
          version11 -> Layout
            version4 -> LookDev
              version2 -> Model

          version23 -> Another Bigger Layout
            version18 -> Another Layout referencing version4
              version4 -> LookDev
                version2 -> Model

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True
        self.version18.is_published = True
        self.version23.is_published = True
        DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pm.spaceLocator()
        loc.t.set(0, 0, 0)
        pm.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pm.saveFile()

        # version11 references version4
        pm.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        loc = pm.ls(type=pm.nt.Transform)
        loc[0].t.set(1, 0, 0)
        pm.saveFile()

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # version15 references version11
        pm.newFile(force=True)
        self.maya_env.open(self.version15)  # bigger layout
        self.maya_env.reference(self.version11)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version11.filename.replace('.', '_')
        # now do some other edits here
        loc = pm.ls(type=pm.nt.Transform)
        loc[0].t.set(0, 1, 0)
        pm.saveFile()

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # version18 references version4
        pm.newFile(force=True)
        self.maya_env.open(self.version18)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        loc = pm.ls(type=pm.nt.Transform)
        loc[0].t.set(0, 0, 1)
        pm.saveFile()

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # version23 references version18
        pm.newFile(force=True)
        self.maya_env.open(self.version23)  # bigger layout
        self.maya_env.reference(self.version18)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version18.filename.replace('.', '_')
        # now do some other edits here
        loc = pm.ls(type=pm.nt.Transform)
        loc[0].t.set(0, 0, 2)
        pm.saveFile()

        DBSession.commit()

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version18.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # check edits
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, scs=1)),
            2
        )

        # now fix the namespaces in version23 let it be fixed
        self.maya_env.fix_reference_namespaces()
        pm.saveFile()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)

        version23_version4_path = all_refs[1].path
        version23_version2_path = all_refs[2].path

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version18.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, scs=1)),
            2
        )

        # and check if the locator are where they should be
        locs = pm.ls(type=pm.nt.Transform)
        self.assertEqual(2.0, locs[0].tz.get())
        pm.saveFile()

        # now open version11 and try to fix it also there
        self.maya_env.open(self.version15)

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pm.saveFile()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)

        version15_version4_path = all_refs[1].path
        version15_version2_path = all_refs[2].path

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, scs=1)),
            2
        )

        # and check if the locator are where they should be
        locs = pm.ls(type=pm.nt.Transform)
        self.assertEqual(1.0, locs[0].ty.get())
        pm.saveFile()

        # check if the two scenes are using the same assets
        self.assertEqual(
            version15_version4_path,
            version23_version4_path
        )
        self.assertEqual(
            version15_version2_path,
            version23_version2_path
        )

    def test_fix_reference_namespace_returns_a_list_of_newly_created_versions(self):
        """testing if the fix_reference_namespace method will return newly
        created version instances in a list.

          version11 -> has no new version ->Layout
            version4 -> has no new version -> LookDev
              version2 -> has no new version -> Model -> has a new version3

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version3.is_published = True

        self.version4.is_published = True
        self.version11.is_published = True
        DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pm.spaceLocator()
        loc.t.set(0, 0, 0)
        pm.saveFile()

        # save as version3
        self.maya_env.save_as(self.version3)

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pm.saveFile()

        # version11 references version4 four times
        pm.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be four locators in the current scene
        loc = pm.ls(type=pm.nt.Transform)
        loc[0].t.set(1, 0, 0)

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pm.saveFile()
        DBSession.commit()

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now let it be fixed
        list_of_versions = self.maya_env.fix_reference_namespaces()

        self.assertEqual(
            list_of_versions,
            [self.version4.latest_published_version]
        )

    def test_fix_reference_namespace_returned_versions_have_correct_description(self):
        """testing if the fix_reference_namespace method will return newly
        created version instances in a list.

          version11 -> has no new version ->Layout
            version4 -> has no new version -> LookDev
              version2 -> has no new version -> Model -> has a new version3

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version3.is_published = True

        self.version4.is_published = True
        self.version11.is_published = True
        DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pm.spaceLocator()
        loc.t.set(0, 0, 0)
        pm.saveFile()

        # save as version3
        self.maya_env.save_as(self.version3)

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pm.saveFile()

        # version11 references version4 four times
        pm.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be four locators in the current scene
        loc = pm.ls(type=pm.nt.Transform)
        loc[0].t.set(1, 0, 0)

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pm.saveFile()
        DBSession.commit()

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now let it be fixed
        list_of_versions = self.maya_env.fix_reference_namespaces()

        self.assertEqual(
            'Automatically created with Fix Reference Namespace',
            self.version4.latest_published_version.description
        )

    def test_fix_reference_namespace_is_working_properly_with_complex_edits(self):
        """testing if the fix_reference_namespace method is working properly
        with references which are updated in another scene

        version15 -> Bigger Layout -> Move the parent
          version11 -> Layout -> Parent it under a group
            version4 -> LookDev -> Assign new Material
              version2 -> Model

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True
        DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        cube = pm.polyCube(name='test_cube')
        cube[0].t.set(0, 0, 0)
        pm.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        # assign a new material
        cube = pm.ls('*:test_cube', type=pm.nt.Transform)[0]
        blinn, blinnSG = pm.createSurfaceShader('blinn')
        pm.sets(blinnSG, e=True, fe=[cube])
        pm.saveFile()

        # version11 references version4
        pm.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        cube = pm.ls('*:*:test_cube', type=pm.nt.Transform)[0]
        # parent it to something else
        group = pm.group(cube, name='test_group')
        cube.t.set(1, 0, 0)
        pm.saveFile()

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # version15 references version11
        pm.newFile(force=True)
        self.maya_env.open(self.version15)  # bigger layout
        self.maya_env.reference(self.version11)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version11.filename.replace('.', '_')
        # now do some other edits here
        group = pm.ls(
            '*:test_group',
            type=pm.nt.Transform
        )[0]
        # move the one with no parent to somewhere in the scene
        group.t.set(10, 0, 0)
        pm.saveFile()

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pm.saveFile()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            2
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, scs=1)),
            4
        )

        # and check if the locator are where they should be
        group = pm.ls('*:test_group', type=pm.nt.Transform)[0]
        self.assertEqual(10.0, group.tx.get())
        pm.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_references_with_no_namespaces(self):
        """testing if the fix_reference_namespace method is working properly
        with references which are not using namespaces

        version15 -> Bigger Layout -> Move the parent / Uses no namespaces
          version11 -> Layout -> Parent it under a group
            version4 -> LookDev -> Assign new Material
              version2 -> Model

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True
        DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        cube = pm.polyCube(name='test_cube')
        cube[0].t.set(0, 0, 0)
        pm.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        # assign a new material
        cube = pm.ls('*:test_cube', type=pm.nt.Transform)[0]
        blinn, blinnSG = pm.createSurfaceShader('blinn')
        pm.sets(blinnSG, e=True, fe=[cube])
        pm.saveFile()

        # version11 references version4
        pm.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pm.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        cube = pm.ls('*:*:test_cube', type=pm.nt.Transform)[0]
        # parent it to something else
        group = pm.group(cube, name='test_group')
        # pm.parent(cube, group)
        cube.t.set(1, 0, 0)
        pm.saveFile()

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # version15 references version11
        pm.newFile(force=True)
        self.maya_env.open(self.version15)  # bigger layout
        self.maya_env.reference(self.version11, use_namespace=False)
        # use no namespace for version11 (so do not edit to old version)
        # now do some other edits here
        group = pm.ls(
            'test_group',
            type=pm.nt.Transform
        )[0]
        # move the one with no parent to somewhere in the scene
        group.t.set(10, 0, 0)
        pm.saveFile()

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.split('.')[0]  # maya uses filename
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.split('.')[0]  # still using filename
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pm.saveFile()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.split('.')[0]
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # # and we have all successful edits
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            2
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, scs=1)),
            4
        )

        # and check if the locator are where they should be
        group = pm.ls('test_group', type=pm.nt.Transform)[0]
        self.assertEqual(10.0, group.tx.get())
        pm.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_references_with_same_namespaces_with_its_children_ref(self):
        """testing if the fix_reference_namespace method is working properly
        with references that has the same namespace with its children

        version15 -> Bigger Layout -> Move the parent
          version11 -> Layout -> Parent it under a group
            version4 -> LookDev -> Assign new Material / using the same
                        namespace with its child
              version2 -> Model

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True
        DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        cube = pm.polyCube(name='test_cube')
        cube[0].t.set(0, 0, 0)
        pm.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        # assign a new material
        cube = pm.ls('*:test_cube', type=pm.nt.Transform)[0]
        blinn, blinnSG = pm.createSurfaceShader('blinn')
        pm.sets(blinnSG, e=True, fe=[cube])
        pm.saveFile()

        # version11 references version4
        pm.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use version2 namespace in version4
        refs = pm.listReferences()
        refs[0].namespace = self.version2.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        cube = pm.ls('*:*:test_cube', type=pm.nt.Transform)[0]
        # parent it to something else
        group = pm.group(cube, name='test_group')
        # pm.parent(cube, group)
        cube.t.set(1, 0, 0)
        pm.saveFile()

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # version15 references version11
        pm.newFile(force=True)
        self.maya_env.open(self.version15)  # bigger layout
        self.maya_env.reference(self.version11)
        # use old style namespace here
        refs = pm.listReferences()
        refs[0].namespace = self.version11.filename.replace('.', '_')
        # now do some other edits here
        group = pm.ls(
            '*:test_group',
            type=pm.nt.Transform
        )[0]
        # move the one with no parent to somewhere in the scene
        group.t.set(10, 0, 0)
        pm.saveFile()

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        # version4 is using version2 namespace
        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # check namespaces
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        # version4 is using version2 filename
        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pm.saveFile()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            2
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, scs=1)),
            4
        )

        # and check if the locator are where they should be
        group = pm.ls('*:test_group', type=pm.nt.Transform)[0]
        self.assertEqual(10.0, group.tx.get())
        pm.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_references_with_same_namespaces_with_its_children_ref_in_a_shallower_setup(self):
        """testing if the fix_reference_namespace method is working properly
        with references that has the same namespace with its children in a
        shallower setup

        version11 -> Layout -> Parent it under a group
          version4 -> LookDev -> Assign new Material / using the same
                      namespace with its child
            version2 -> Model

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        cube = pm.polyCube(name='test_cube')
        cube[0].t.set(0, 0, 0)
        pm.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        # assign a new material
        cube = pm.ls('*:test_cube', type=pm.nt.Transform)[0]
        blinn, blinnSG = pm.createSurfaceShader('blinn')
        pm.sets(blinnSG, e=True, fe=[cube])
        pm.saveFile()

        # version11 references version4
        pm.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use version2 namespace in version4
        refs = pm.listReferences()
        refs[0].namespace = self.version2.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        cube = pm.ls('*:*:test_cube', type=pm.nt.Transform)[0]
        # parent it to something else
        group = pm.group(cube, name='test_group')
        cube.t.set(1, 0, 0)
        pm.saveFile()

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # check namespaces
        all_refs = pm.listReferences(recursive=1)

        # version4 is using version2 namespace
        self.assertEqual(
            all_refs[0].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        # check namespaces
        # version4 is using version2 filename
        self.assertEqual(
            all_refs[0].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pm.saveFile()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            1
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            4
        )

        # and check if the locator are where they should be
        pm.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_references_with_correct_namespaces_but_has_wrong_namespace_children(self):
        """testing if the fix_reference_namespace method is working properly
        with references that has the same namespace with its children

        version15 -> Bigger Layout
          version11 -> Layout -> uses correct namespace
            version4 -> LookDev -> uses correct namespace
              version2 -> Model -> uses wrong namespace

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True
        DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        cube = pm.polyCube(name='test_cube')
        cube[0].t.set(0, 0, 0)
        pm.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pm.listReferences()
        ref = refs[0]
        isinstance(ref, pm.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        # assign a new material
        cube = pm.ls('*:test_cube', type=pm.nt.Transform)[0]
        blinn, blinnSG = pm.createSurfaceShader('blinn')
        pm.sets(blinnSG, e=True, fe=[cube])
        pm.saveFile()

        # version11 references version4
        pm.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use version2 namespace in version4
        refs = pm.listReferences()
        # refs[0].namespace = self.version4.nice_name
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        cube = pm.ls('*:*:test_cube', type=pm.nt.Transform)[0]
        # parent it to something else
        group = pm.group(cube, name='test_group')
        cube.t.set(1, 0, 0)
        pm.saveFile()

        # we should have created an edit
        version2_ref_node = pm.listReferences(refs[0])[0]
        edits = pm.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # version15 references version11
        pm.newFile(force=True)
        self.maya_env.open(self.version15)  # bigger layout
        self.maya_env.reference(self.version11)
        # use old style namespace here
        refs = pm.listReferences()
        # refs[0].namespace = self.version11.nice_name
        # now do some other edits here
        group = pm.ls(
            '*:test_group',
            type=pm.nt.Transform
        )[0]
        # move the one with no parent to somewhere in the scene
        group.t.set(10, 0, 0)
        pm.saveFile()

        # check namespaces
        # version11 is using correct namespace
        all_refs = pm.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.nice_name
        )

        # version4 is using correct namespace
        self.assertEqual(
            all_refs[1].namespace,
            self.version4.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pm.saveFile()

        # check if the namespaces are fixed
        all_refs = pm.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        self.assertEqual(
            len(pm.referenceQuery(all_refs[0], es=1, scs=1)),
            2
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        self.assertEqual(
            len(pm.referenceQuery(all_refs[2], es=1, scs=1)),
            4
        )

        # and check if the locator are where they should be
        group = pm.ls('*:test_group', type=pm.nt.Transform)[0]
        self.assertEqual(10.0, group.tx.get())
        pm.saveFile()


class FileReferenceRepresentationsTestCase(MayaTestBase):
    """tests the FileReference with Representations
    """

    def setUp(self):
        """additional setup
        """
        # call the supers setUp first
        super(FileReferenceRepresentationsTestCase, self).setUp()

        # now do your addition
        # create ass take for asset2
        self.repr_version1 = self.create_version(self.asset2, 'Main@ASS', self.version3)
        self.repr_version2 = self.create_version(self.asset2, 'Main@ASS', self.version3)
        self.repr_version3 = self.create_version(self.asset2, 'Main@ASS', self.version3)

        self.repr_version1.is_published = True
        self.repr_version3.is_published = True

        self.repr_version4 = self.create_version(self.asset2, 'Main@BBox', self.version3)
        self.repr_version5 = self.create_version(self.asset2, 'Main@BBox', self.version3)
        self.repr_version6 = self.create_version(self.asset2, 'Main@BBox', self.version3)

        self.repr_version4.is_published = True
        self.repr_version6.is_published = True

        self.repr_version7 = self.create_version(self.asset2, 'Main@GPU', self.version3)
        self.repr_version8 = self.create_version(self.asset2, 'Main@GPU', self.version3)
        self.repr_version9 = self.create_version(self.asset2, 'Main@GPU', self.version3)

        self.repr_version9.is_published = True

        self.repr_version10 = self.create_version(self.asset2, 'Take1@ASS', self.version3)
        self.repr_version11 = self.create_version(self.asset2, 'Take1@ASS', self.version3)
        self.repr_version12 = self.create_version(self.asset2, 'Take1@ASS', self.version3)

        self.repr_version11.is_published = True

        self.repr_version13 = self.create_version(self.asset2, 'Take1@BBox', self.version3)
        self.repr_version14 = self.create_version(self.asset2, 'Take1@BBox', self.version3)
        self.repr_version15 = self.create_version(self.asset2, 'Take1@BBox', self.version3)

        self.repr_version14.is_published = True

        self.repr_version16 = self.create_version(self.asset2, 'Take1@GPU', self.version3)
        self.repr_version17 = self.create_version(self.asset2, 'Take1@GPU', self.version3)
        self.repr_version18 = self.create_version(self.asset2, 'Take1@GPU', self.version3)

        self.repr_version16.is_published = True
        self.repr_version17.is_published = True
        self.repr_version18.is_published = True

        # a reference with only ASS representation
        self.repr_version19 = self.create_version(self.asset2, 'Take2')
        self.repr_version20 = self.create_version(self.asset2, 'Take2')
        self.repr_version21 = self.create_version(self.asset2, 'Take2')

        self.repr_version21.is_published = True

        self.repr_version22 = self.create_version(self.asset2, 'Take2@ASS', self.version21)
        self.repr_version23 = self.create_version(self.asset2, 'Take2@ASS', self.version21)
        self.repr_version24 = self.create_version(self.asset2, 'Take2@ASS', self.version21)

        self.repr_version24.is_published = True

        self.version1.is_published = True
        self.version3.is_published = True

        DBSession.commit()

        pm.newFile(force=True)

    def test_FileReference_class_has_to_repr_method(self):
        """testing if FileReference has a to_repr() method
        """
        from pymel.core.system import FileReference
        self.assertTrue(hasattr(FileReference, 'to_repr'))

    def test_FileReference_class_has_list_all_repr_method(self):
        """testing if FileReference has a list_all_repr() method
        """
        from pymel.core.system import FileReference
        self.assertTrue(hasattr(FileReference, 'list_all_repr'))

    def test_FileReference_class_has_list_find_repr_method(self):
        """testing if FileReference has a find_repr() method
        """
        from pymel.core.system import FileReference
        self.assertTrue(hasattr(FileReference, 'find_repr'))

    def test_to_repr_is_working_properly(self):
        """testing if FileReference.to_repr() is working properly
        """
        # reference version1 to the scene
        ref = self.maya_env.reference(self.version1)

        self.assertEqual(ref.path, self.version1.absolute_full_path)
        # now invoke to_repr on the FileReference node
        ref.to_repr('ASS')

        # and expect its path to be replaced with self.repr_version3
        self.assertEqual(ref.path, self.repr_version3.absolute_full_path)

    def test_to_base_is_working_properly(self):
        """testing if FileReference.to_base() is working properly
        """
        # reference version1 to the scene
        ref = self.maya_env.reference(self.repr_version1)

        self.assertEqual(ref.path, self.repr_version1.absolute_full_path)
        # now invoke to_base on the FileReference node
        ref.to_base()

        # and expect its path to be replaced with self.repr_version3
        self.assertEqual(ref.path, self.version3.absolute_full_path)

    def test_list_all_repr_is_working_properly(self):
        """testing if list_all_repr is working properly
        """
        ref = self.maya_env.reference(self.repr_version1)

        self.assertEqual(ref.path, self.repr_version1.absolute_full_path)

        result = ref.list_all_repr()
        self.assertEqual(
            sorted(['Base', 'ASS', 'BBox', 'GPU']),
            sorted(result)
        )

    def test_find_repr_is_working_properly(self):
        """testing if find_repr is working properly
        """
        ref = self.maya_env.reference(self.repr_version1)

        self.assertEqual(ref.path, self.repr_version1.absolute_full_path)

        result = ref.find_repr('GPU')
        self.assertEqual(
            result,
            self.repr_version9
        )

    def test_is_base_is_working_properly(self):
        """testing if is_base is working properly
        """
        ref = self.maya_env.reference(self.repr_version1)
        self.assertEqual(ref.path, self.repr_version1.absolute_full_path)
        self.assertFalse(ref.is_base())

        ref = self.maya_env.reference(self.version1)
        self.assertEqual(ref.path, self.version1.absolute_full_path)
        self.assertTrue(ref.is_base())

    def test_get_base_is_working_properly(self):
        """testing if get_base is working properly
        """
        ref = self.maya_env.reference(self.repr_version1)
        self.assertEqual(ref.path, self.repr_version1.absolute_full_path)
        self.assertFalse(ref.is_base())
        v = ref.get_base()
        self.assertEqual(v, self.version3)

    def test_is_repr_method_is_working_properly(self):
        """testing if is_repr is working properly
        """
        ref = self.maya_env.reference(self.repr_version1)
        self.assertEqual(ref.path, self.repr_version1.absolute_full_path)
        self.assertFalse(ref.is_repr('Base'))
        self.assertTrue(ref.is_repr('ASS'))

    def test_repr_property_is_working_properly(self):
        """testing if ``repr`` property is working properly
        """
        ref = self.maya_env.reference(self.repr_version1)
        self.assertEqual(ref.path, self.repr_version1.absolute_full_path)
        self.assertEqual(ref.repr, 'ASS')


class ToolboxRepresentationToolsTestCase(MayaTestBase):
    """tests anima.dcc.mayaEnv.toolbox representation tools
    """

    def setUp(self):
        """set up class level
        """
        super(ToolboxRepresentationToolsTestCase, self).setUp()

        # login
        from stalker import User, LocalSession
        u = User.query.first()
        l = LocalSession()
        l.store_user(u)
        l.save()

        # first path pm.confirmDialog
        self.orig_confirm_dialog = pm.confirmDialog

        def patched_confirm_dialog(*args, **kwargs):
            return 'Yes'

        pm.confirmDialog = patched_confirm_dialog

    def tearDown(self):
        """clean up
        """
        from stalker import LocalSession
        l = LocalSession()
        l.delete()

        # restore confirm dialog
        pm.confirmDialog = self.orig_confirm_dialog

    def test_generating_all_representations_through_environment_layout_scene(self):
        """testing if generating all representations of all references from the
        environment layout scene is working properly
        """
        from anima.dcc.mayaEnv import toolbox

        # open up the environment | layout | hires
        self.maya_env.open(self.version102, force=True)

        # generate all from here
        anima.dcc.mayaEnv.reference.Reference.generate_repr_of_all_references()

        # expect all of the representations to be generated for all of the
        # referenced scenes

        # start from deepest
        r = Representation()

        # Building1 | Props | YAPI | Model | Hires
        r.version = self.version75
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

        # Building1 | Props | YAPI | LookDev
        r.version = self.version78
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

        # Building1 | Layout | Hires
        r.version = self.version66
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

        # Building2 | Props | YAPI | Model | Hires
        r.version = self.version93
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

        # Building2 | Props | YAPI | LookDev
        r.version = self.version96
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

        # Building2 | Layout | Hires
        r.version = self.version84
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

        # Vegetation
        r.version = self.version117
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

        # Layout | Hires
        r.version = self.version102
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)


class RepresentationGeneratorTestCase(MayaTestBase):
    """tests Representation generator
    """

    def setUp(self):
        """set up class level
        """
        super(RepresentationGeneratorTestCase, self).setUp()

        # login
        from stalker import User, LocalSession
        u = User.query.first()
        l = LocalSession()
        l.store_user(u)
        l.save()

    def tearDown(self):
        """clean up
        """
        from stalker import LocalSession
        l = LocalSession()
        l.delete()

    # GPU
    # - of a model
    # - of a look dev
    # - of a layout of a building
    # - of a look dev of a building
    # - of a layout of an environment
    # - of a look dev of an environment
    # - of a vegetation scene

    def test_generate_gpu_will_end_up_with_an_empty_scene(self):
        """testing if generate_gpu will end up with an empty scene
        """
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_gpu()

        # we should be on an untitled scene
        self.assertEqual(
            pm.sceneName(),
            ''
        )

    def test_generate_gpu_will_overwrite_previous_gpu_version(self):
        """testing if generate_gpu will overwrite to the previous GPU version
        """
        gen = RepresentationGenerator()

        gen.version = self.version75
        gen.generate_gpu()

        r = Representation(version=self.version75)
        v1 = r.find('GPU')
        self.assertTrue(v1 is not None)

        # generate again
        gen.generate_gpu()
        v2 = r.find('GPU')
        self.assertTrue(v2 is not None)

        # and they should be the same version
        self.assertEqual(v1, v2)

    def test_generate_gpu_scene_with_references_before_generating_gpu_of_references_first(self):
        """testing if a RuntimeError will be raised when trying to generate
        the GPU Repr of a scene before generating the GPU of all of the
        references
        """
        gen = RepresentationGenerator(version=self.version76)

        with self.assertRaises(RuntimeError) as cm:
            gen.generate_gpu()

        self.assertEqual(
            str(cm.exception),
            'Please generate the GPU Representation of the references '
            'first!!!\n%s' % self.version75.absolute_full_path
        )

    def test_generate_gpu_of_a_simple_model(self):
        """testing if generate_gpu will generate bounding boxes for each
        object with the same name in a model scene
        """
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_gpu()

        r = Representation(version=self.version75)
        v = r.find('GPU')
        self.maya_env.open(v, force=True)

        # the name of the GPU object should be the same
        node = pm.PyNode('duvarlar')

        self.assertTrue(node is not None)

        # and the type of the shape should be gpuCache
        self.assertEqual(node.getShape().type(), 'gpuCache')

    def test_generate_gpu_of_a_simple_look_dev(self):
        """testing if generate_gpu will just replace the references for a
        simple look dev scene
        """
        # start with building | props | yapi | model | hires
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_gpu()

        # building | props | yapi | look dev
        gen.version = self.version78
        gen.generate_gpu()

        r = Representation(version=self.version78)
        v = r.find('GPU')
        self.maya_env.open(v, force=True)

        # nothing special here, the reference should be replaced with GPU repr
        for ref in pm.listReferences():
            self.assertTrue(ref.is_repr('GPU'))

    def test_generate_gpu_of_a_layout_of_a_building(self):
        """testing if generate_gpu of the layout scene of a building is
        working properly
        """
        # start with building | props | yapi | model | hires
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_gpu()

        # building | props | yapi | look dev
        gen.version = self.version78
        gen.generate_gpu()

        # building | layout | hires
        gen.version = self.version66
        gen.generate_gpu()

        r = Representation(version=self.version66)
        v = r.find('GPU')
        self.maya_env.open(v, force=True)

        # nothing special here, the reference should be replaced with GPU repr
        for ref in pm.listReferences():
            self.assertTrue(ref.is_repr('GPU'))

    def test_generate_gpu_of_a_look_dev_of_a_building(self):
        """testing if generate_gpu of the look dev scene of a building is
        working properly
        """
        # start with building | props | yapi | model | hires
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_gpu()

        # building | props | yapi | look dev
        gen.version = self.version78
        gen.generate_gpu()

        # building | layout | hires
        gen.version = self.version66
        gen.generate_gpu()

        # building | look dev
        gen.version = self.version69
        gen.generate_gpu()

        r = Representation(version=self.version69)
        v = r.find('GPU')
        self.maya_env.open(v, force=True)

        # nothing special here, the reference should be replaced with GPU repr
        for ref in pm.listReferences():
            self.assertTrue(ref.is_repr('GPU'))

    def test_generate_gpu_of_a_layout_of_an_environment(self):
        """testing if generate_gpu of the layout scene of an environment is
        working properly
        """
        gen = RepresentationGenerator()
        # Prop1 (Model | Hires | Kisa)
        gen.version = self.version123
        gen.generate_all()

        # Prop1 (LookDev | Kisa)
        gen.version = self.version120
        gen.generate_all()

        # Building1
        # start with building | props | yapi | model | hires
        gen.version = self.version75
        gen.generate_gpu()

        # building | props | yapi | look dev
        gen.version = self.version78
        gen.generate_gpu()

        # building | layout | hires
        gen.version = self.version66
        gen.generate_gpu()

        # Building2
        # start with building | props | yapi | model | hires
        gen = RepresentationGenerator(version=self.version93)
        gen.generate_gpu()

        # building | props | yapi | look dev
        gen.version = self.version96
        gen.generate_gpu()

        # building | layout | hires
        gen.version = self.version84
        gen.generate_gpu()

        # vegetation
        gen.version = self.version117
        gen.generate_gpu()

        # Environment
        gen.version = self.version102
        gen.generate_gpu()

        r = Representation(version=self.version102)
        v = r.find('GPU')
        self.maya_env.open(v, force=True)

        # there should be no references
        self.assertTrue(len(pm.listReferences()) == 0)

    def test_generate_gpu_of_a_look_dev_of_an_environment(self):
        """testing if generate_gpu of the look dev scene of an environment is
        working properly
        """
        # Building1
        # start with building | props | yapi | model | hires
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_gpu()

        # building | props | yapi | look dev
        gen.version = self.version78
        gen.generate_gpu()

        # building | layout | hires
        gen.version = self.version66
        gen.generate_gpu()

        # Building2
        # start with building | props | yapi | model | hires
        gen = RepresentationGenerator(version=self.version93)
        gen.generate_gpu()

        # building | props | yapi | look dev
        gen.version = self.version96
        gen.generate_gpu()

        # building | layout | hires
        gen.version = self.version84
        gen.generate_gpu()

        # vegetation
        gen.version = self.version117
        gen.generate_gpu()

        # Environment Layout
        gen.version = self.version102
        gen.generate_gpu()

        # Environment Look dev
        gen.version = self.version105
        gen.generate_gpu()

        r = Representation(version=self.version105)
        v = r.find('GPU')
        self.maya_env.open(v, force=True)

        # nothing special here, the reference should be replaced with GPU repr
        for ref in pm.listReferences():
            self.assertTrue(ref.is_repr('GPU'))

    def test_generate_gpu_of_a_vegetation_scene(self):
        """testing if generate_gpu of the vegetation scene is working properly
        """
        gen = RepresentationGenerator(version=self.version117)
        gen.generate_gpu()

        r = Representation(version=self.version117)
        v = r.find('GPU')
        self.maya_env.open(v, force=True)

        # we should have all polygons converted to a bounding box object
        root_node = pm.PyNode('kksEnv___vegetation_ALL')
        self.assertTrue(root_node is not None)

        children = root_node.getChildren()
        # for child in children:
        #     print(child.name())
        self.assertEqual(len(children), 1)  # including paintableGeos group

        # pfx_polygons = children[2]
        # self.assertEqual(pfx_polygons.name(), 'kks___vegetation_pfxPolygons')

        # and they should have a gpuCache shape
        # self.assertTrue(
        #     pfx_polygons.getShape().type(), 'gpuCache'
        # )

    # ASS
    # - of a model
    # - of a look dev
    # - of a layout of a building
    # - of a look dev of a building
    # - of a layout of an environment
    # - of a look dev of an environment
    # - of a vegetation scene

    def test_generate_ass_will_end_up_with_an_empty_scene(self):
        """testing if generate_ass will end up with a new empty scene
        """
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_ass()

        # we should be on an untitled scene
        self.assertEqual(
            pm.sceneName(),
            ''
        )

    def test_generate_ass_will_overwrite_previous_ass_version(self):
        """testing if generate_ass will overwrite to the previous ASS version
        """
        gen = RepresentationGenerator()

        gen.version = self.version75
        gen.generate_ass()

        r = Representation(version=self.version75)
        v1 = r.find('ASS')
        self.assertTrue(v1 is not None)

        # generate again
        gen.generate_ass()
        v2 = r.find('ASS')
        self.assertTrue(v2 is not None)

        # and they should be the same version
        self.assertEqual(v1, v2)

    def test_generate_ass_repr_for_building_yapi_look_dev_without_creating_model_first(self):
        """testing if a RuntimeError will be raised when trying to generate a
        the ASS Repr for a Look Dev task before generating ASS for the model
        first
        """
        gen = RepresentationGenerator(version=self.version76)

        with self.assertRaises(RuntimeError) as cm:
            gen.generate_ass()

        self.assertEqual(
            str(cm.exception),
            'Please generate the ASS Representation of the references '
            'first!!!\n%s' % self.version75.absolute_full_path
        )

    def test_generate_ass_repr_for_building_layout_without_creating_building_look_dev_first(self):
        """testing if a RuntimeError will be raised when trying to generate a
        the ASS Repr for a Layout task before generating ASS for the Look Dev
        first
        """
        gen = RepresentationGenerator(version=self.version66)

        with self.assertRaises(RuntimeError) as cm:
            gen.generate_ass()

        self.assertEqual(
            str(cm.exception),
            'Please generate the ASS Representation of the references '
            'first!!!\n%s' % self.version78.absolute_full_path
        )

    def test_generate_ass_repr_for_building_yapi_model(self):
        """testing if creating ASS repr for a model is working properly
        """
        gen = RepresentationGenerator(version=self.version73)
        gen.generate_ass()

        # check if a proper ASS repr is generated
        repr = Representation(version=self.version73)
        ass_v = repr.find('ASS')
        self.assertTrue(ass_v is not None)
        self.assertTrue('@ASS' in ass_v.take_name)
        self.assertTrue(os.path.exists(ass_v.absolute_full_path))

        # open the file and check content
        self.maya_env.open(ass_v, force=True)
        yapi = pm.ls('building1_yapi')[0]

        # it should have only one child
        all_children = yapi.getChildren()
        self.assertEqual(len(all_children), 1)

        # and it should have an aiStandIn node as the shape
        bina = all_children[0]
        self.assertEqual(len(bina.getChildren()), 1)
        stand_in = bina.getChildren()[0]
        self.assertEqual(stand_in.type(), 'aiStandIn')
        self.assertTrue(stand_in.getAttr('dso') is None)

    def test_generate_ass_repr_for_building_yapi_look_dev_is_working_properly(self):
        """testing if ASS repr generation is working properly for a look dev
        version
        """
        # first generate for the model
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_ass()

        # then for the look dev version
        gen.version = self.version76
        gen.generate_ass()

        # open the file
        r = Representation(version=self.version76)
        # get the ASS repr
        v = r.find('ASS')
        self.maya_env.open(v, force=True)

        # check if "alles in ordnung!"
        # the reference should be a ASS repr of the model
        ref = pm.listReferences()[0]
        self.assertTrue(ref.is_repr('ASS'))

        # there should be Stand-In nodes under the referenced nodes
        all_stand_ins = pm.ls(type='aiStandIn')
        self.assertEqual(len(all_stand_ins), 1)

        # it should be a referenced node
        parent = all_stand_ins[0].getParent()
        self.assertEqual(
            parent.referenceFile(),
            ref
        )

        # the standIn node it self should be coming from the model
        self.assertEqual(
            all_stand_ins[0].referenceFile(),
            ref
        )

        # and the path of hte aiStandIn is pointing to a ass file under the
        # LookDev/Outputs
        self.assertTrue(
            'LookDev/Outputs' in all_stand_ins[0].getAttr('dso')
        )
        self.assertTrue(
            '.ass.gz' in all_stand_ins[0].getAttr('dso')
        )

    def test_generate_ass_repr_for_building_layout_is_working_properly(self):
        """testing if a generating the ASS Repr for a Layout task is working
        properly
        """
        # generate for the model first
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_ass()

        # then look dev
        gen.version = self.version78
        gen.generate_ass()

        # then for the layout
        gen.version = self.version66
        gen.generate_ass()

        # open the Layout:Main@ASS
        r = Representation(version=self.version66)
        v = r.find('ASS')
        self.assertTrue(v is not None)
        self.maya_env.open(v, force=True)

        # there should be nothing so special, instead of the regular look dev
        # the ASS repr of the look dev should have been referenced
        ref = pm.listReferences()[0]
        self.assertTrue(ref.is_repr('ASS'))

    def test_generate_ass_repr_for_building_look_dev_is_working_properly(self):
        """testing if generate_ass() will properly generate an ASS repr for the
        look dev of a building
        """
        #Building1
        # generate for the model first
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_ass()

        # then building | yapi | look dev
        gen.version = self.version78
        gen.generate_ass()

        # then for the building | layout | hires
        gen.version = self.version66
        gen.generate_ass()

        # then the building | look dev
        gen.version = self.version69
        gen.generate_ass()

        # open up the ASS file
        r = Representation(version=self.version69)
        v = r.find('ASS')
        self.maya_env.open(v, force=True)

        # now check references
        ref = pm.listReferences()[0]
        self.assertTrue(ref.is_repr('ASS'))

    def test_generate_ass_repr_for_vegetation_scene(self):
        """testing if generating ass of a vegetation scene is working properly
        """
        gen = RepresentationGenerator(version=self.version117)
        gen.generate_ass()

        # open the ASS scene
        r = Representation(version=self.version117)
        v = r.find('ASS')
        self.maya_env.open(v, force=True)

        # there should be only "pfxPolygons" group
        root_node = pm.PyNode('kksEnv___vegetation_ALL')
        children = root_node.getChildren()

        self.assertEqual(len(children), 1)

        # and there should be 2 other
        # transform nodes under it (for our test case)
        pfx_polygons = children[0]
        self.assertEqual(pfx_polygons.name(), 'kks___vegetation_pfxPolygons')

        children = pfx_polygons.getChildren()
        self.assertEqual(len(children), 2)

        # they should have a transform node with aiStandIn shape
        for child in children:
            mesh_group = child.getChildren()[0]
            self.assertTrue(
                mesh_group.getShape().type(),
                'aiStandIn'
            )

    def test_generate_ass_of_a_layout_of_an_environment(self):
        """testing if generate_ass() will properly generate an ASS repr for the
        environment layout
        """
        #Building1
        # generate for the model first
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_ass()

        # then building | yapi | look dev
        gen.version = self.version78
        gen.generate_ass()

        # then for the building | layout | hires
        gen.version = self.version66
        gen.generate_ass()

        #Building2
        # generate for the model first
        gen = RepresentationGenerator(version=self.version93)
        gen.generate_ass()

        # then building | yapi | look dev
        gen.version = self.version96
        gen.generate_ass()

        # then for the building | layout | hires
        gen.version = self.version84
        gen.generate_ass()

        # The vegetation
        gen.version = self.version117
        gen.generate_ass()

        # Environment | Layout | Hires
        gen.version = self.version102
        gen.generate_ass()

        # open up the ASS file
        r = Representation(version=self.version102)
        v = r.find('ASS')
        self.maya_env.open(v, force=True)

        # now check references
        self.assertTrue(len(pm.listReferences()) == 0)

        # but there should be aiStandIn nodes
        self.assertTrue(len(pm.ls(type='aiStandIn')) > 0)

    # ALL
    # - of a model
    # - of a look dev
    # - of a layout of a building
    # - of a look dev of a building
    # - of a layout of an environment
    # - of a look dev of an environment
    # - of a vegetation scene

    def test_generate_all_will_end_up_with_an_empty_scene(self):
        """testing if generate_all will end up with an empty scene
        """
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_all()

        # we should be on an untitled scene
        self.assertEqual(
            pm.sceneName(),
            ''
        )

    def test_generate_all_scene_with_references_before_generating_all_of_references_first(self):
        """testing if a RuntimeError will be raised when trying to generate
        the all representations of a scene before generating all of the
        representations of all of the references
        """
        gen = RepresentationGenerator(version=self.version76)

        with self.assertRaises(RuntimeError) as cm:
            gen.generate_all()

        # BBOX will complain first
        self.assertEqual(
            str(cm.exception),
            'Please generate the GPU Representation of the references '
            'first!!!\n%s' % self.version75.absolute_full_path
        )

    def test_generate_all_of_a_simple_model(self):
        """testing if generate_all will generate all representations of a model
        scene
        """
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_all()

        r = Representation(version=self.version75)
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

    def test_generate_all_of_a_simple_look_dev(self):
        """testing if generate_all generate all of the representations of a
        simple look dev scene
        """
        # start with building | props | yapi | model | hires
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_all()

        # building | props | yapi | look dev
        gen.version = self.version78
        gen.generate_all()

        r = Representation(version=self.version78)
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

    def test_generate_all_of_a_layout_of_a_building(self):
        """testing if generate_all of the layout scene of a building is working
        properly
        """
        # start with building | props | yapi | model | hires
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_all()

        # building | props | yapi | look dev
        gen.version = self.version78
        gen.generate_all()

        # building | layout | hires
        gen.version = self.version66
        gen.generate_all()

        r = Representation(version=self.version66)
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

    def test_generate_all_of_a_look_dev_of_a_building(self):
        """testing if generate_all of the look dev scene of a building is
        working properly
        """
        # start with building | props | yapi | model | hires
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_all()

        # building | props | yapi | look dev
        gen.version = self.version78
        gen.generate_all()

        # building | layout | hires
        gen.version = self.version66
        gen.generate_all()

        # building | look dev
        gen.version = self.version69
        gen.generate_all()

        r = Representation(version=self.version69)
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

    def test_generate_all_of_a_layout_of_an_environment(self):
        """testing if generate_all of the layout scene of an environment is
        working properly
        """
        gen = RepresentationGenerator()
        # Prop1 (Model | Hires | Kisa)
        gen.version = self.version123
        gen.generate_all()

        # Prop1 (LookDev | Kisa)
        gen.version = self.version120
        gen.generate_all()

        # Building1
        # start with building | props | yapi | model | hires
        gen.version = self.version75
        gen.generate_all()

        # building | props | yapi | look dev
        gen.version = self.version78
        gen.generate_all()

        # building | layout | hires
        gen.version = self.version66
        gen.generate_all()

        # Building2
        # start with building | props | yapi | model | hires
        gen = RepresentationGenerator(version=self.version93)
        gen.generate_all()

        # building | props | yapi | look dev
        gen.version = self.version96
        gen.generate_all()

        # building | layout | hires
        gen.version = self.version84
        gen.generate_all()

        # vegetation
        gen.version = self.version117
        gen.generate_all()

        # Environment
        gen.version = self.version102
        gen.generate_all()

        r = Representation(version=self.version102)
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

    def test_generate_all_of_a_look_dev_of_an_environment(self):
        """testing if generate_all of the look dev scene of an environment is
        working properly
        """
        # Building1
        # start with building | props | yapi | model | hires
        gen = RepresentationGenerator(version=self.version75)
        gen.generate_all()

        # building | props | yapi | look dev
        gen.version = self.version78
        gen.generate_all()

        # building | layout | hires
        gen.version = self.version66
        gen.generate_all()

        # Building2
        # start with building | props | yapi | model | hires
        gen = RepresentationGenerator(version=self.version93)
        gen.generate_all()

        # building | props | yapi | look dev
        gen.version = self.version96
        gen.generate_all()

        # building | layout | hires
        gen.version = self.version84
        gen.generate_all()

        # vegetation
        gen.version = self.version117
        gen.generate_all()

        # Environment Layout
        gen.version = self.version102
        gen.generate_all()

        # Environment Look dev
        gen.version = self.version105
        gen.generate_all()

        r = Representation(version=self.version105)
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)

    def test_generate_all_of_a_vegetation_scene(self):
        """testing if generate_all of the vegetation scene is working properly
        """
        gen = RepresentationGenerator(version=self.version117)
        gen.generate_all()

        r = Representation(version=self.version117)
        v_gpu = r.find('GPU')
        v_ass = r.find('ASS')

        self.assertTrue(v_gpu is not None)
        self.assertTrue(v_ass is not None)


class PublisherTestCase(MayaTestBase):
    """tests maya DCC with publishers
    """
    backup_publishers = None

    @classmethod
    def setUpClass(cls):
        """setup once
        """
        super(PublisherTestCase, cls).setUpClass()

        cls.backup_publishers = publish.publishers
        publish.clear_publishers()

    @classmethod
    def tearDownClass(cls):
        """clean up once
        """
        super(PublisherTestCase, cls).tearDownClass()

        # also restore publishers
        publish.publishers = cls.backup_publishers

    def setUp(self):
        """clean up tests
        """
        super(PublisherTestCase, self).setUp()
        publish.clear_publishers()

    def tearDown(self):
        """clean up tests
        """
        super(PublisherTestCase, self).tearDown()
        publish.clear_publishers()

    def test_save_as_calls_publishers_for_published_versions(self):
        """testing if Maya.save_as() runs the registered publishers for
        published versions before really saving the file.
        """
        # register two new publishers
        publishers_called = []

        @publish.publisher('LookDev')
        def publisher1():
            publishers_called.append('publisher1')

        @publish.publisher('Model')
        def publisher2():
            publishers_called.append('publisher2')

        # now save a new version to a task which is a LookDev task
        pm.newFile(force=True)

        self.task6.type = Type(
            name='LookDev',
            code='LookDev',
            target_entity_type='Task'
        )

        v = Version(task=self.task6)
        v.is_published = True
        DBSession.add(v)

        # check called publishers
        self.assertEqual(publishers_called, [])
        self.maya_env.save_as(v)
        self.assertEqual(publishers_called, ['publisher1'])

    def test_save_as_does_not_call_publishers_for_published_versions(self):
        """testing if Maya.save_as() runs the registered publishers for
        published versions before really saving the file.
        """
        # register two new publishers
        publishers_called = []

        @publish.publisher('LookDev')
        def publisher1():
            publishers_called.append('publisher1')

        @publish.publisher('Model')
        def publisher2():
            publishers_called.append('publisher2')

        # now save a new version to a task which is a LookDev task
        pm.newFile(force=True)

        v = Version(task=self.task6)
        DBSession.add(v)

        # check called publishers
        self.assertEqual(publishers_called, [])
        self.maya_env.save_as(v)
        self.assertEqual(publishers_called, [])


class ArchiverTestCase(MayaTestBase):
    """Tests the anima.dcc.mayaEnv.archive.Archiver class
    """

    @classmethod
    def setUpClass(cls):
        """setup once
        """
        cls.logger = logging.getLogger('anima.dcc.mayaEnv.archive')
        cls.logger.setLevel(logging.DEBUG)

    @classmethod
    def tearDownClass(cls):
        """clean up once
        """
        cls.logger = logging.getLogger('anima.dcc.mayaEnv.archive')
        cls.logger.setLevel(logging.WARNING)

    def test_create_default_project_will_create_a_folder(self):
        """testing if the create_default_project will create a
        default maya project structure and return the path
        """
        arch = Archiver()
        tempdir = tempfile.gettempdir()

        project_path = arch.create_default_project(tempdir)
        self.remove_these_files_buffer.append(project_path)

        self.assertTrue(os.path.exists(project_path))

    def test_create_default_project_will_create_a_workspace_mel_file(self):
        """testing if the create_default_project will create a
        default maya project structure with a proper workspace.mel
        """
        arch = Archiver()
        tempdir = tempfile.gettempdir()

        project_path = arch.create_default_project(tempdir)
        self.remove_these_files_buffer.append(project_path)

        workspace_mel_path = os.path.join(project_path, 'workspace.mel')

        self.assertTrue(os.path.exists(workspace_mel_path))

    def test_create_default_project_workspace_mel_content_is_correct(self):
        """testing if the content of the workspace.mel file is correct when the
        create_default_project method is used.
        """
        arch = Archiver()
        tempdir = tempfile.gettempdir()

        project_path = arch.create_default_project(tempdir)
        self.remove_these_files_buffer.append(project_path)

        workspace_mel_path = os.path.join(project_path, 'workspace.mel')

        with open(workspace_mel_path) as f:
            content = f.readlines()

        content = '\n'.join(content)

        expected_result = """// Anima Archiver Default Project Definition

workspace -fr "translatorData" "data";
workspace -fr "offlineEdit" "scenes/edits";
workspace -fr "renderData" "renderData";
workspace -fr "scene" "scenes";
workspace -fr "3dPaintTextures" "sourceimages/3dPaintTextures";
workspace -fr "eps" "data";
workspace -fr "OBJexport" "data";
workspace -fr "mel" "scripts";
workspace -fr "furShadowMap" "renderData/fur/furShadowMap";
workspace -fr "particles" "cache/particles";
workspace -fr "audio" "sound";
workspace -fr "scripts" "scripts";
workspace -fr "sound" "sound";
workspace -fr "DXF_FBX export" "data";
workspace -fr "furFiles" "renderData/fur/furFiles";
workspace -fr "depth" "renderData/depth";
workspace -fr "autoSave" "autosave";
workspace -fr "furAttrMap" "renderData/fur/furAttrMap";
workspace -fr "diskCache" "data";
workspace -fr "fileCache" "cache/nCache";
workspace -fr "ASS Export" "data";
workspace -fr "FBX export" "data";
workspace -fr "sourceImages" "sourceimages";
workspace -fr "FBX" "data";
workspace -fr "DAE_FBX export" "data";
workspace -fr "movie" "movies";
workspace -fr "Alembic" "data";
workspace -fr "DAE_FBX" "data";
workspace -fr "iprImages" "renderData/iprImages";
workspace -fr "mayaAscii" "scenes";
workspace -fr "furImages" "renderData/fur/furImages";
workspace -fr "furEqualMap" "renderData/fur/furEqualMap";
workspace -fr "illustrator" "data";
workspace -fr "DXF_FBX" "data";
workspace -fr "mayaBinary" "scenes";
workspace -fr "move" "data";
workspace -fr "images" "images";
workspace -fr "fluidCache" "cache/nCache/fluid";
workspace -fr "clips" "clips";
workspace -fr "ASS" "data";
workspace -fr "OBJ" "data";
workspace -fr "templates" "assets";
workspace -fr "shaders" "renderData/shaders";
"""

    def test_create_default_project_workspace_mel_already_exists(self):
        """testing if no error will be raised when the workspace.mel file is
        already there
        """
        arch = Archiver()
        tempdir = tempfile.gettempdir()

        # there should be no error to call it multiple times
        project_path = arch.create_default_project(tempdir)
        self.remove_these_files_buffer.append(project_path)

        project_path = arch.create_default_project(tempdir)
        project_path = arch.create_default_project(tempdir)

    def test_flatten_is_working_properly_with_no_references(self):
        """testing if the Archiver.flatten() is working properly for a scene
        with no references.
        """
        arch = Archiver()
        project_path = arch.flatten(self.version1.absolute_full_path)
        self.remove_these_files_buffer.append(project_path)

        # the returned path should be a maya project directory
        self.assertTrue(os.path.exists(project_path))

        # there should be a workspace.mel file
        self.assertTrue(os.path.exists(os.path.join(project_path, 'workspace.mel')))

        # there should be a maya scene file under path/scenes with the same
        # name of the source file
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    project_path, 'scenes', self.version1.filename
                )
            )
        )

    def test_flatten_is_working_properly_with_only_one_level_of_references(self):
        """testing if the Archiver.flatten() is working properly for a scene
        with only one level of references.
        """
        # open self.version1
        self.maya_env.open(self.version1, force=True)

        # and reference self.version4 to it
        self.maya_env.reference(self.version4)

        # and save it
        pm.saveFile()

        # renew the scene
        pm.newFile(force=1)

        # create an archiver
        arch = Archiver()

        project_path = arch.flatten(self.version1.absolute_full_path)
        self.remove_these_files_buffer.append(project_path)

        # now check if we have two files under the path/scenes directory
        archived_version1_path = \
            os.path.join(project_path, 'scenes', self.version1.filename)

        archived_version4_unresolved_path = \
            os.path.join('scenes/refs', self.version4.filename)

        archived_version4_path = \
            os.path.join(project_path, archived_version4_unresolved_path)

        self.assertTrue(os.path.exists(archived_version1_path))
        self.assertTrue(os.path.exists(archived_version4_path))

        # open the archived version1
        pm.workspace.open(project_path)
        pm.openFile(archived_version1_path)

        # expect it to have one reference
        all_refs = pm.listReferences()
        self.assertEqual(len(all_refs), 1)

        # and the path is matching to archived version4 path
        ref = all_refs[0]
        self.assertEqual(ref.path, archived_version4_path)
        self.assertEqual(
            ref.unresolvedPath(),
            archived_version4_unresolved_path
        )

    def test_flatten_is_working_properly_with_only_one_level_of_multiple_references_to_the_same_file(self):
        """testing if the Archiver.flatten() is working properly for a scene
        with only one level of multiple references to the same file.
        """
        # open self.version1
        self.maya_env.open(self.version1, force=True)

        # and reference self.version4 more than once to it
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)

        # and save it
        pm.saveFile()

        # renew the scene
        pm.newFile(force=1)

        # create an archiver
        arch = Archiver()

        project_path = arch.flatten(self.version1.absolute_full_path)
        self.remove_these_files_buffer.append(project_path)

        # now check if we have two files under the path/scenes directory
        archived_version1_path = \
            os.path.join(project_path, 'scenes', self.version1.filename)

        archived_version4_unresolved_path = \
            os.path.join('scenes/refs', self.version4.filename)

        archived_version4_path = \
            os.path.join(project_path, archived_version4_unresolved_path)

        self.assertTrue(os.path.exists(archived_version1_path))
        self.assertTrue(os.path.exists(archived_version4_path))

        # open the archived version1
        pm.workspace.open(project_path)
        pm.openFile(archived_version1_path)

        # expect it to have three references
        all_refs = pm.listReferences()
        self.assertEqual(len(all_refs), 3)

        # and the path is matching to archived version4 path
        ref = all_refs[0]
        self.assertEqual(ref.path, archived_version4_path)
        self.assertEqual(
            ref.unresolvedPath(),
            archived_version4_unresolved_path
        )

        ref = all_refs[1]
        self.assertEqual(ref.path, archived_version4_path)
        self.assertEqual(
            ref.unresolvedPath(),
            archived_version4_unresolved_path
        )

        ref = all_refs[2]
        self.assertEqual(ref.path, archived_version4_path)
        self.assertEqual(
            ref.unresolvedPath(),
            archived_version4_unresolved_path
        )

    def test_flatten_is_working_properly_with_multiple_level_of_references(self):
        """testing if the Archiver.flatten() is working properly for a scene
        with multiple levels of references.
        """
        # open self.version4
        self.maya_env.open(self.version4, force=True)

        # and reference self.version7 to it
        self.maya_env.reference(self.version7)

        # and save it
        pm.saveFile()

        # open self.version1
        self.maya_env.open(self.version1, force=True)

        # and reference self.version4 to it
        self.maya_env.reference(self.version4)

        # and save it
        pm.saveFile()

        # renew the scene
        pm.newFile(force=1)

        # create an archiver
        arch = Archiver()

        project_path = arch.flatten(self.version1.absolute_full_path)
        self.remove_these_files_buffer.append(project_path)

        # now check if we have two files under the path/scenes directory
        archived_version1_path = \
            os.path.join(project_path, 'scenes', self.version1.filename)

        archived_version4_path = \
            os.path.join(project_path, 'scenes/refs', self.version4.filename)

        archived_version4_unresolved_path = \
            os.path.join('scenes/refs', self.version4.filename)

        archived_version7_path = \
            os.path.join(project_path, 'scenes/refs', self.version7.filename)

        archived_version7_unresolved_path = \
            os.path.join('scenes/refs', self.version7.filename)

        self.assertTrue(os.path.exists(archived_version1_path))
        self.assertTrue(os.path.exists(archived_version4_path))
        self.assertTrue(os.path.exists(archived_version7_path))

        # open the archived version1
        pm.workspace.open(project_path)
        pm.openFile(archived_version1_path)

        # expect it to have one reference
        all_refs = pm.listReferences()
        self.assertEqual(len(all_refs), 1)

        # and the path is matching to archived version4 path
        ref = all_refs[0]
        self.assertEqual(ref.path, archived_version4_path)
        self.assertEqual(
            ref.unresolvedPath(),
            archived_version4_unresolved_path
        )

        # check the deeper level references
        deeper_ref = pm.listReferences(parentReference=ref)[0]
        self.assertEqual(deeper_ref.path, archived_version7_path)
        self.assertEqual(
            deeper_ref.unresolvedPath(),
            archived_version7_unresolved_path
        )

    def test_flatten_is_working_properly_with_the_external_files_of_the_references(self):
        """testing if the Archiver.flatten() is working properly for a scene
        with references that has external files like textures, sound etc.
        """
        # open self.version7
        self.maya_env.open(self.version7, force=True)

        # create an image file at the project root
        image_filename = 'test.jpg'
        image_path = os.path.join(self.version7.absolute_path, 'Textures')
        image_full_path = os.path.join(image_path, image_filename)

        # create the file
        os.makedirs(image_path)
        with open(image_full_path, 'w+') as f:
            f.writelines([''])

        audio_filename = 'test.wav'
        audio_path = os.path.join(self.version7.absolute_path, 'Sounds')
        audio_full_path = os.path.join(audio_path, audio_filename)

        # create the file
        os.makedirs(audio_path)
        with open(audio_full_path, 'w+') as f:
            f.writelines([''])

        # create one image and one audio node
        pm.createNode('file').attr('fileTextureName').set(image_full_path)
        pm.createNode('audio').attr('filename').set(audio_full_path)

        # save it
        # replace external paths
        self.maya_env.replace_external_paths()
        pm.saveFile()

        # open self.version4
        self.maya_env.open(self.version4, force=True)

        # and reference self.version7 to it
        self.maya_env.reference(self.version7)

        # and save it
        pm.saveFile()

        # open self.version1
        self.maya_env.open(self.version1, force=True)

        # and reference self.version4 to it
        self.maya_env.reference(self.version4)

        # and save it
        pm.saveFile()

        # renew the scene
        pm.newFile(force=1)

        # create an archiver
        arch = Archiver()

        project_path = arch.flatten(self.version1.absolute_full_path)
        self.remove_these_files_buffer.append(project_path)

        # now check if we have the files under the path/scenes directory
        archived_version1_path = \
            os.path.join(project_path, 'scenes', self.version1.filename)

        # and references under path/scenes/refs path
        archived_version4_path = \
            os.path.join(project_path, 'scenes/refs', self.version4.filename)

        archived_version4_unresolved_path = \
            os.path.join('scenes/refs', self.version4.filename)

        archived_version7_path = \
            os.path.join(project_path, 'scenes/refs', self.version7.filename)

        archived_version7_unresolved_path = \
            os.path.join('scenes/refs', self.version7.filename)

        archived_image_path = \
            os.path.join(project_path, 'scenes/refs', image_filename)

        archived_audio_path = \
            os.path.join(project_path, 'scenes/refs', audio_filename)

        self.assertTrue(os.path.exists(archived_version1_path))
        self.assertTrue(os.path.exists(archived_version4_path))
        self.assertTrue(os.path.exists(archived_version7_path))
        self.assertTrue(os.path.exists(archived_image_path))
        self.assertTrue(os.path.exists(archived_audio_path))

        # open the archived version1
        pm.workspace.open(project_path)
        pm.openFile(archived_version1_path)

        # expect it to have one reference
        all_refs = pm.listReferences()
        self.assertEqual(len(all_refs), 1)

        # and the path is matching to archived version4 path
        ref = all_refs[0]
        self.assertEqual(ref.path, archived_version4_path)
        self.assertEqual(
            ref.unresolvedPath(),
            archived_version4_unresolved_path
        )

        # check the deeper level references
        deeper_ref = pm.listReferences(parentReference=ref)[0]
        self.assertEqual(deeper_ref.path, archived_version7_path)
        self.assertEqual(
            deeper_ref.unresolvedPath(),
            archived_version7_unresolved_path
        )

        # and deeper level files
        ref_image_path = pm.ls(type='file')[0].attr('fileTextureName').get()
        self.assertEqual(
            ref_image_path,
            os.path.join(project_path, 'scenes/refs', image_filename)
        )
        ref_audio_path = pm.ls(type='audio')[0].attr('filename').get()
        self.assertEqual(
            ref_audio_path,
            os.path.join(project_path, 'scenes/refs', audio_filename)
        )

    def test_flatten_is_working_properly_with_exclude_mask(self):
        """testing if the Archiver.flatten() is working properly for a scene
        with references that has external files like textures, sound etc. and
        there is also an exclude_mask
        """
        # open self.version7
        self.maya_env.open(self.version7, force=True)

        # create an image file at the project root
        image_filename = 'test.jpg'
        image_path = os.path.join(self.version7.absolute_path, 'Textures')
        image_full_path = os.path.join(image_path, image_filename)

        # create the file
        os.makedirs(image_path)
        with open(image_full_path, 'w+') as f:
            f.writelines([''])

        audio_filename = 'test.wav'
        audio_path = os.path.join(self.version7.absolute_path, 'Sounds')
        audio_full_path = os.path.join(audio_path, audio_filename)

        # create the file
        os.makedirs(audio_path)
        with open(audio_full_path, 'w+') as f:
            f.writelines([''])

        # create one image and one audio node
        pm.createNode('file').attr('fileTextureName').set(image_full_path)
        pm.createNode('audio').attr('filename').set(audio_full_path)

        # save it
        # replace external paths
        self.maya_env.replace_external_paths()
        pm.saveFile()

        # open self.version4
        self.maya_env.open(self.version4, force=True)

        # and reference self.version7 to it
        self.maya_env.reference(self.version7)

        # and save it
        pm.saveFile()

        # open self.version1
        self.maya_env.open(self.version1, force=True)

        # and reference self.version4 to it
        self.maya_env.reference(self.version4)

        # and save it
        pm.saveFile()

        # renew the scene
        pm.newFile(force=1)

        # create an archiver
        arch = Archiver(exclude_mask=['.png', '.jpg', '.tga'])

        project_path = arch.flatten(self.version1.absolute_full_path)
        self.remove_these_files_buffer.append(project_path)

        # now check if we have the files under the path/scenes directory
        archived_version1_path = \
            os.path.join(project_path, 'scenes', self.version1.filename)

        # and references under path/scenes/refs path
        archived_version4_path = \
            os.path.join(project_path, 'scenes/refs', self.version4.filename)

        archived_version4_unresolved_path = \
            os.path.join('scenes/refs', self.version4.filename)

        archived_version7_path = \
            os.path.join(project_path, 'scenes/refs', self.version7.filename)

        archived_version7_unresolved_path = \
            os.path.join('scenes/refs', self.version7.filename)

        archived_image_path = \
            os.path.join(project_path, 'scenes/refs', image_filename)

        archived_audio_path = \
            os.path.join(project_path, 'scenes/refs', audio_filename)

        self.assertTrue(os.path.exists(archived_version1_path))
        self.assertTrue(os.path.exists(archived_version4_path))
        self.assertTrue(os.path.exists(archived_version7_path))
        # jpg should not be included
        self.assertFalse(os.path.exists(archived_image_path))
        self.assertTrue(os.path.exists(archived_audio_path))

        # open the archived version1
        pm.workspace.open(project_path)
        pm.openFile(archived_version1_path)

        # expect it to have one reference
        all_refs = pm.listReferences()
        self.assertEqual(len(all_refs), 1)

        # and the path is matching to archived version4 path
        ref = all_refs[0]
        self.assertEqual(ref.path, archived_version4_path)
        self.assertEqual(
            ref.unresolvedPath(),
            archived_version4_unresolved_path
        )

        # check the deeper level references
        deeper_ref = pm.listReferences(parentReference=ref)[0]
        self.assertEqual(deeper_ref.path, archived_version7_path)
        self.assertEqual(
            deeper_ref.unresolvedPath(),
            archived_version7_unresolved_path
        )

        # and deeper level files
        ref_image_path = pm.ls(type='file')[0].attr('fileTextureName').get()

        # the path of the jpg should be intact
        self.assertEqual(
            ref_image_path,
            os.path.join(self.version7.path, 'Textures', image_filename)
        )
        ref_audio_path = pm.ls(type='audio')[0].attr('filename').get()
        self.assertEqual(
            ref_audio_path,
            os.path.join(project_path, 'scenes/refs', audio_filename)
        )

    def test_flatten_is_working_properly_with_multiple_reference_to_the_same_file_with_multiple_level_of_references(self):
        """testing if the Archiver.flatten() is working properly for a scene
        with multiple levels of references.
        """
        # open self.version4
        self.maya_env.open(self.version4, force=True)

        # and reference self.version7 to it
        self.maya_env.reference(self.version7)

        # and save it
        pm.saveFile()

        # open self.version1
        self.maya_env.open(self.version1, force=True)

        # and reference self.version4 multiple times to it
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)

        # and save it
        pm.saveFile()

        # renew the scene
        pm.newFile(force=1)

        # create an archiver
        arch = Archiver()

        project_path = arch.flatten(self.version1.absolute_full_path)
        self.remove_these_files_buffer.append(project_path)

        # now check if we have two files under the path/scenes directory
        archived_version1_path = \
            os.path.join(project_path, 'scenes', self.version1.filename)

        # version4
        archived_version4_unresolved_path = \
            os.path.join('scenes/refs', self.version4.filename)

        archived_version4_path = \
            os.path.join(project_path, archived_version4_unresolved_path)

        # version7
        archived_version7_unresolved_path = \
            os.path.join('scenes/refs', self.version7.filename)

        archived_version7_path = \
            os.path.join(project_path, archived_version7_unresolved_path)

        self.assertTrue(os.path.exists(archived_version1_path))
        self.assertTrue(os.path.exists(archived_version4_path))
        self.assertTrue(os.path.exists(archived_version7_path))

        # open the archived version1
        pm.workspace.open(project_path)
        pm.newFile(force=True)
        pm.openFile(archived_version1_path, force=True)

        # expect it to have three reference to the same file
        all_refs = pm.listReferences()
        self.assertEqual(len(all_refs), 3)

        # and the path is matching to archived version4 path
        # 1st
        ref = all_refs[0]
        self.assertEqual(ref.path, archived_version4_path)

        # check the unresolved path
        self.assertEqual(
            ref.unresolvedPath(),
            archived_version4_unresolved_path
        )

        # check the deeper level references
        deeper_ref = pm.listReferences(parentReference=ref)[0]
        self.assertEqual(deeper_ref.path, archived_version7_path)

        # check the unresolved path
        self.assertEqual(
            deeper_ref.unresolvedPath(),
            archived_version7_unresolved_path
        )

        # 2nd
        ref = all_refs[1]
        self.assertEqual(ref.path, archived_version4_path)

        # check the unresolved path
        self.assertEqual(
            ref.unresolvedPath(),
            archived_version4_unresolved_path
        )

        # check the deeper level references
        deeper_ref = pm.listReferences(parentReference=ref)[0]
        self.assertEqual(deeper_ref.path, archived_version7_path)

        # check the unresolved path
        self.assertEqual(
            deeper_ref.unresolvedPath(),
            archived_version7_unresolved_path
        )

        # 3rd
        ref = all_refs[2]
        self.assertEqual(ref.path, archived_version4_path)

        # check the unresolved path
        self.assertEqual(
            ref.unresolvedPath(),
            archived_version4_unresolved_path
        )

        # check the deeper level references
        deeper_ref = pm.listReferences(parentReference=ref)[0]
        self.assertEqual(deeper_ref.path, archived_version7_path)

        # check the unresolved path
        self.assertEqual(
            deeper_ref.unresolvedPath(),
            archived_version7_unresolved_path
        )

    def test_flatten_is_working_properly_for_external_files(self):
        """testing if the Archiver.flatten() is working properly for a scene
        with textures, audio etc. external files
        """
        # open self.version7
        self.maya_env.open(self.version7, force=True)

        # create an image file at the project root
        image_filename = 'test.jpg'
        image_path = os.path.join(self.version7.absolute_path, 'Textures')
        image_full_path = os.path.join(image_path, image_filename)

        # create the file
        os.makedirs(image_path)
        with open(image_full_path, 'w+') as f:
            f.writelines([''])

        audio_filename = 'test.wav'
        audio_path = os.path.join(self.version7.absolute_path, 'Sounds')
        audio_full_path = os.path.join(audio_path, audio_filename)

        # create the file
        os.makedirs(audio_path)
        with open(audio_full_path, 'w+') as f:
            f.writelines([''])

        # create one image and one audio node
        pm.createNode('file').attr('fileTextureName').set(image_full_path)
        pm.createNode('audio').attr('filename').set(audio_full_path)

        # save it
        # replace external paths
        self.maya_env.replace_external_paths()
        pm.saveFile()

        # renew the scene
        pm.newFile(force=1)

        # create an archiver
        arch = Archiver()

        project_path = arch.flatten(self.version7.absolute_full_path)
        self.remove_these_files_buffer.append(project_path)

        # now check if we have the files under the path/scenes directory
        archived_version7_path = \
            os.path.join(project_path, 'scenes', self.version7.filename)

        archived_image_path = \
            os.path.join(project_path, 'scenes/refs', image_filename)

        self.assertTrue(os.path.exists(archived_version7_path))
        self.assertTrue(os.path.exists(archived_image_path))

        # open the archived version1
        pm.workspace.open(project_path)
        pm.openFile(archived_version7_path)

        # and image files
        ref_image_path = pm.ls(type='file')[0].attr('fileTextureName').get()
        self.assertEqual(
            ref_image_path,
            os.path.join(project_path, 'scenes/refs', image_filename)
        )
        ref_audio_path = pm.ls(type='audio')[0].attr('filename').get()
        self.assertEqual(
            ref_audio_path,
            os.path.join(project_path, 'scenes/refs', audio_filename)
        )

    def test_flatten_will_restore_the_current_workspace(self):
        """testing if the Archiver.flatten() will restore the current workspace
        path after it has finished flattening
        """
        # open self.version1
        self.maya_env.open(self.version1, force=True)

        current_workspace = pm.workspace.path

        arch = Archiver()
        project_path = arch.flatten(self.version1.absolute_full_path)
        self.remove_these_files_buffer.append(project_path)

        # now check if the current workspace is intact
        self.assertEqual(current_workspace, pm.workspace.path)

    def test_archive_will_create_a_zip_file_from_the_given_directory(self):
        """testing if the Archiver.archive() will create a zip file and return
        the path of it
        """
        arch = Archiver()
        project_path = arch.flatten(self.version1.absolute_full_path)
        self.remove_these_files_buffer.append(project_path)

        parent_path = os.path.dirname(project_path) + '/'

        # create a list of paths
        original_files = []
        for current_dir_path, dir_names, file_names in os.walk(project_path):
            for dir_name in dir_names:
                original_files.append(
                    os.path.join(
                        current_dir_path,
                        dir_name
                    )[len(parent_path):].replace('\\', '/') + '/'
                )
            for file_name in file_names:
                original_files.append(
                    os.path.join(
                        current_dir_path,
                        file_name
                    )[len(parent_path):].replace('\\', '/')
                )

        # archive it
        archive_path = arch.archive(project_path)
        self.remove_these_files_buffer.append(archive_path)

        self.assertTrue(os.path.exists(archive_path))

        # and it is a valid zip file
        import zipfile
        with zipfile.ZipFile(archive_path) as z:
            all_names = z.namelist()

        self.assertEqual(
            sorted(original_files),
            sorted(all_names)
        )

    def test_bind_to_original_will_bind_the_references_to_their_original_counter_part_in_the_repository(self):
        """testing if bind_to_original will be able to switch first level
        references with their original counter part in the repository
        """
        # open self.version4
        self.maya_env.open(self.version4, force=True)

        # and reference self.version7 to it
        self.maya_env.reference(self.version7)

        # and save it
        pm.saveFile()

        # open self.version1
        self.maya_env.open(self.version1, force=True)

        # and reference self.version4 multiple times to it
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)

        # and save it
        pm.saveFile()

        # renew the scene
        pm.newFile(force=1)

        # create an archiver
        arch = Archiver()

        project_path = arch.flatten(self.version1.absolute_full_path)
        self.remove_these_files_buffer.append(project_path)

        # now check if we have two files under the path/scenes directory
        archived_version1_path = \
            os.path.join(project_path, 'scenes', self.version1.filename)

        # version4
        archived_version4_unresolved_path = \
            os.path.join('scenes/refs', self.version4.filename)

        archived_version4_path = \
            os.path.join(project_path, archived_version4_unresolved_path)

        # version7
        archived_version7_unresolved_path = \
            os.path.join('scenes/refs', self.version7.filename)

        archived_version7_path = \
            os.path.join(project_path, archived_version7_unresolved_path)

        self.assertTrue(os.path.exists(archived_version1_path))
        self.assertTrue(os.path.exists(archived_version4_path))
        self.assertTrue(os.path.exists(archived_version7_path))

        # open the archived version1
        pm.workspace.open(project_path)
        pm.newFile(force=True)
        pm.openFile(archived_version1_path, force=True)

        # expect it to have three reference to the same file
        all_refs = pm.listReferences()
        self.assertEqual(len(all_refs), 3)

        # check if the first level references are using the flattened files
        self.assertEqual(
            all_refs[0].unresolvedPath().replace('\\\, \/'),
            archived_version4_unresolved_path
        )
        self.assertEqual(
            all_refs[1].unresolvedPath(),
            archived_version4_unresolved_path
        )
        self.assertEqual(
            all_refs[2].unresolvedPath(),
            archived_version4_unresolved_path
        )

        # close the file
        pm.newFile(force=True)

        # now use bind to original to bind them to the originals
        arch.bind_to_original(archived_version1_path)

        # re-open the file and expect it to be bound to the originals
        pm.openFile(archived_version1_path, force=True)

        # list references
        repo = self.version4.task.project.repository

        all_refs = pm.listReferences()

        self.assertEqual(
            all_refs[0].unresolvedPath(),
            self.version4.full_path
        )
        self.assertEqual(
            all_refs[1].unresolvedPath(),
            self.version4.full_path
        )
        self.assertEqual(
            all_refs[2].unresolvedPath(),
            self.version4.full_path
        )
