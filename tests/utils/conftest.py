# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT


import pytest


@pytest.fixture('session')
def test_data():
    """reads test data
    """
    # reads the test data as text
    import os
    here = os.path.dirname(__file__)
    test_data_file_path = os.path.join(here, 'data', 'test_template.json')

    import json
    with open(test_data_file_path) as f:
        test_data = json.load(f)

    yield test_data


@pytest.fixture('session')
def create_db():
    """creates a test database
    """
    from stalker import db
    db.setup({'sqlalchemy.url': 'sqlite://'})
    db.init()


@pytest.fixture('session')
def create_project():
    """creates test data
    """
    from stalker.db.session import DBSession
    from stalker import (Task, Asset, Type, Sequence, Shot, Version,
                         FilenameTemplate, Repository, Project, Structure)

    repo = Repository(
        name='Test Repository',
        windows_path='T:/',
        linux_path='/mnt/T/',
        osx_path='/Volumes/T/'
    )

    task_filename_template = FilenameTemplate(
        name='Task Filename Template',
        path='$REPO{{project.repository.code}}/{{project.code}}/'
            '{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}'
            '/{%- endfor -%}',
        filename='{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}',
        target_entity_type='Task'
    )
    asset_filename_template = FilenameTemplate(
        name='Asset Filename Template',
        path='$REPO{{project.repository.code}}/{{project.code}}/'
            '{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}'
            '/{%- endfor -%}',
        filename='{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}',
        target_entity_type='Asset'
    )
    shot_filename_template = FilenameTemplate(
        name='Shot Filename Template',
        path='$REPO{{project.repository.code}}/{{project.code}}/'
            '{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}'
            '/{%- endfor -%}',
        filename='{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}',
        target_entity_type='Shot'
    )
    sequence_filename_template = FilenameTemplate(
        name='Sequence Filename Template',
        path='$REPO{{project.repository.code}}/{{project.code}}/'
            '{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}'
            '/{%- endfor -%}',
        filename='{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}',
        target_entity_type='Sequence'
    )

    structure = Structure(
        name='Default Project Structure',
        templates=[task_filename_template, asset_filename_template,
                   shot_filename_template, sequence_filename_template]
    )

    DBSession.add_all([
        structure,
        task_filename_template, asset_filename_template,
        shot_filename_template, sequence_filename_template
    ])
    DBSession.commit()

    project = Project(
        name='Test Project',
        code='TP',
        repository=repo,
        structure=structure,
    )
    DBSession.add(project)
    DBSession.commit()

    assets_task = Task(name='Assets', project=project)
    characters_task = Task(name='Characters', parent=assets_task)
    props_task = Task(name='Props', parent=assets_task)
    environments_task = Task(name='Environments', parent=assets_task)

    sequences_task = Task(name='Sequences', project=project)

    # Asset Types
    char_type = Type(name='Character', code='Char', target_entity_type='Asset')
    prop_type = Type(name='Prop', code='Prop', target_entity_type='Asset')
    exterior_type = Type(name='Exterior', code='Exterior',
                         target_entity_type='Asset')
    interior_type = Type(name='Interior', code='Interior',
                         target_entity_type='Asset')

    # Task Types
    model_type = Type(name='Model', code='Model', target_entity_type='Task')
    look_dev_type = Type(
        name='Look Development', code='LookDev', target_entity_type='Task'
    )
    rig_type = Type(name='Rig', code='Rig', target_entity_type='Task')
    layout_type = Type(name='Layout', code='Layout', target_entity_type='Task')

    anim_type = \
        Type(name='Animation', code='Animation', target_entity_type='Task')
    camera_type = Type(name='Camera', code='Camera', target_entity_type='Task')
    plate_type = Type(name='Plate', code='Plate', target_entity_type='Task')
    fx_type = Type(name='FX', code='FX', target_entity_type='Task')
    lighting_type = \
        Type(name='Lighting', code='Lighting', target_entity_type='Task')
    comp_type = Type(name='Comp', code='Comp', target_entity_type='Task')
    DBSession.add_all([
        char_type, prop_type, exterior_type, interior_type,
        model_type, look_dev_type, rig_type, layout_type,
        anim_type, camera_type,
        plate_type, fx_type, lighting_type, comp_type
    ])
    DBSession.commit()

    # char1
    char1 = Asset(
        name='Char1', code='Char1', parent=characters_task, type=char_type
    )
    model = Task(name='Model', type=model_type, parent=char1)
    look_dev_task = Task(name='LookDev', type=look_dev_type, parent=char1)
    rig = Task(name='Rig', type=rig_type, parent=char1)
    DBSession.add_all([char1, model, look_dev_task, rig])
    DBSession.commit()

    # char2
    char2 = Asset(
        name='Char2', code='Char2', parent=characters_task, type=char_type
    )
    model = Task(name='Model', type=model_type, parent=char2)
    look_dev_task = Task(name='LookDev', type=look_dev_type, parent=char2)
    rig = Task(name='Rig', type=rig_type, parent=char2)
    DBSession.add_all([char2, model, look_dev_task, rig])
    DBSession.commit()

    # prop1
    prop1 = \
        Asset(name='Prop2', code='Prop2', parent=props_task, type=prop_type)
    model = Task(name='Model', type=model_type, parent=prop1)
    look_dev_task = Task(name='LookDev', type=look_dev_type, parent=prop1)
    DBSession.add_all([prop1, model, look_dev_task])
    DBSession.commit()

    # prop2
    prop2 = \
        Asset(name='Prop2', code='Prop2', parent=props_task, type=prop_type)
    model = Task(name='Model', type=model_type, parent=prop2)
    look_dev_task = Task(name='LookDev', type=look_dev_type, parent=prop2)
    DBSession.add_all([prop2, model, look_dev_task])
    DBSession.commit()

    # environments
    # env1
    env1 = Asset(
        name='Env1', code='Env1', type=exterior_type, parent=environments_task
    )
    layout_task = Task(name='Layout', type=layout_type, parent=env1)
    props_task = Task(name='Props', parent=env1)
    yapi1_asset = \
        Asset(name='Yapi1', code='Yapi1', type=prop_type, parent=props_task)
    model_task = Task(name='Model', type=model_type, parent=yapi1_asset)
    look_dev_task = \
        Task(name='LookDev', type=look_dev_type, parent=yapi1_asset)

    DBSession.add_all([
        env1, layout_task, props_task, yapi1_asset, model_task, look_dev_task
    ])
    DBSession.commit()

    # env2
    env2 = Asset(
        name='Env2', code='Env2', type=exterior_type, parent=environments_task
    )
    layout_task = Task(name='Layout', type=layout_type, parent=env2)
    props_task = Task(name='Props', parent=env2)
    yapi1_asset = \
        Asset(name='Yapi2', code='Yapi2', type=prop_type, parent=props_task)
    model_task = Task(name='Model', type=model_type, parent=yapi1_asset)
    look_dev_task = \
        Task(name='LookDev', type=look_dev_type, parent=yapi1_asset)

    DBSession.add_all([
        env2, layout_task, props_task, yapi1_asset, model_task, look_dev_task
    ])
    DBSession.commit()

    # sequences and shots
    seq1 = Sequence(name='Seq1', code='Seq1', parent=sequences_task)
    edit_task = Task(name='Edit', parent=seq1)
    shots_task = Task(name='Shots', parent=seq1)

    DBSession.add_all([seq1, edit_task, shots_task])
    DBSession.commit()

    # shot1
    shot1 = Shot(name='Seq001_001_0010', code='Seq001_001_0010',
                 sequences=[seq1], parent=shots_task)

    anim_task = Task(name='Anim', type=anim_type, parent=shot1)
    camera_task = Task(name='Camera', type=camera_type, parent=shot1)
    plate_task = Task(name='Plate', type=plate_type, parent=shot1)
    fx_task = Task(name='FX', type=fx_type, parent=shot1)
    lighting_task = Task(name='Lighting', type=lighting_type, parent=shot1)
    comp_task = Task(name='Comp', type=comp_type, parent=shot1)

    DBSession.add_all([
        shot1, anim_task, camera_task, plate_task, fx_task, lighting_task,
        comp_task
    ])
    DBSession.commit()

    # shot2
    shot2 = Shot(name='Seq001_001_0020', code='Seq001_001_0020',
                 sequences=[seq1], parent=shots_task)

    anim_task = Task(name='Anim', type=anim_type, parent=shot2)
    camera_task = Task(name='Camera', type=camera_type, parent=shot2)
    plate_task = Task(name='Plate', type=plate_type, parent=shot2)
    fx_task = Task(name='FX', type=fx_type, parent=shot2)
    lighting_task = Task(name='Lighting', type=lighting_type, parent=shot2)
    comp_task = Task(name='Comp', type=comp_type, parent=shot2)

    DBSession.add_all([
        shot2, anim_task, camera_task, plate_task, fx_task, lighting_task,
        comp_task
    ])
    DBSession.commit()

    # shot3
    shot3 = Shot(name='Seq001_001_0030', code='Seq001_001_0030',
                 sequences=[seq1], parent=shots_task)

    anim_task = Task(name='Anim', type=anim_type, parent=shot3)
    camera_task = Task(name='Camera', type=camera_type, parent=shot3)
    plate_task = Task(name='Plate', type=plate_type, parent=shot3)
    fx_task = Task(name='FX', type=fx_type, parent=shot3)
    lighting_task = Task(name='Lighting', type=lighting_type, parent=shot3)
    comp_task = Task(name='Comp', type=comp_type, parent=shot3)

    DBSession.add_all([
        shot3, anim_task, camera_task, plate_task, fx_task, lighting_task,
        comp_task
    ])
    DBSession.commit()

    # Seq2
    # sequences and shots
    seq2 = Sequence(name='Seq2', code='Seq2', parent=sequences_task)
    edit_task = Task(name='Edit', parent=seq2)
    shots_task = Task(name='Shots', parent=seq2)

    DBSession.add_all([seq2, edit_task, shots_task])
    DBSession.commit()

    # shot1
    shot1 = Shot(name='Seq002_001_0010', code='Seq002_001_0010',
                 sequences=[seq2], parent=shots_task)

    anim_task = Task(name='Anim', type=anim_type, parent=shot1)
    camera_task = Task(name='Camera', type=camera_type, parent=shot1)
    plate_task = Task(name='Plate', type=plate_type, parent=shot1)
    fx_task = Task(name='FX', type=fx_type, parent=shot1)
    lighting_task = Task(name='Lighting', type=lighting_type, parent=shot1)
    comp_task = Task(name='Comp', type=comp_type, parent=shot1)

    DBSession.add_all([
        shot1, anim_task, camera_task, plate_task, fx_task, lighting_task,
        comp_task
    ])
    DBSession.commit()

    # shot2
    shot2 = Shot(name='Seq002_001_0020', code='Seq002_001_0020',
                 sequences=[seq2], parent=shots_task)

    anim_task = Task(name='Anim', type=anim_type, parent=shot2)
    camera_task = Task(name='Camera', type=camera_type, parent=shot2)
    plate_task = Task(name='Plate', type=plate_type, parent=shot2)
    fx_task = Task(name='FX', type=fx_type, parent=shot2)
    lighting_task = Task(name='Lighting', type=lighting_type, parent=shot2)
    comp_task = Task(name='Comp', type=comp_type, parent=shot2)

    DBSession.add_all([
        shot2, anim_task, camera_task, plate_task, fx_task, lighting_task,
        comp_task
    ])
    DBSession.commit()

    # shot3
    shot3 = Shot(name='Seq002_001_0030', code='Seq002_001_0030',
                 sequences=[seq2], parent=shots_task)

    anim_task = Task(name='Anim', type=anim_type, parent=shot3)
    camera_task = Task(name='Camera', type=camera_type, parent=shot3)
    plate_task = Task(name='Plate', type=plate_type, parent=shot3)
    fx_task = Task(name='FX', type=fx_type, parent=shot3)
    lighting_task = Task(name='Lighting', type=lighting_type, parent=shot3)
    comp_task = Task(name='Comp', type=comp_type, parent=shot3)

    DBSession.add_all([
        shot3, anim_task, camera_task, plate_task, fx_task, lighting_task,
        comp_task
    ])
    DBSession.commit()

    yield project


def test_database_is_correctly_created(create_db):
    """testing if the fixture is working properly
    """
    from stalker.db.session import DBSession
    assert str(DBSession.connection().engine.dialect.name) == 'sqlite'
