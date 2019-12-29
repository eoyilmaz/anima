# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Anima Istanbul
#
# This module is part of anima-tools and is released under the MIT
# License: http://www.opensource.org/licenses/MIT


def test_creating_test_data(create_db, create_project):
    """testing if the test project is created correctly
    """
    # now we should have some projects
    project = create_project
    from stalker import Project
    assert isinstance(project, Project)

    from stalker import Task
    all_tasks = Task.query.all()
    assert len(all_tasks) == 79


def test_stalker_entity_encoder_is_working_properly(create_db, create_project):
    """testing if JSON Encode
    """
    from stalker import Task
    project = create_project
    assets_task = Task.query\
        .filter(Task.project==project).filter(Task.name=='Assets').first()
    assert isinstance(assets_task, Task)

    import json
    from anima.utils import task_hierarchy_io
    data = json.dumps(assets_task, cls=task_hierarchy_io.StalkerEntityEncoder,
                      check_circular=False, indent=4)

    expected_data = """{
    "tasks": [
        {
            "tasks": [
                {
                    "asset_id": 56, 
                    "versions": [], 
                    "code": "Char1", 
                    "description": "", 
                    "entity_type": "Asset", 
                    "type_id": 37, 
                    "schedule_constraint": 0, 
                    "schedule_unit": "h", 
                    "tasks": [
                        {
                            "tasks": [], 
                            "description": "", 
                            "entity_type": "Task", 
                            "type_id": 41, 
                            "schedule_constraint": 0, 
                            "schedule_unit": "h", 
                            "name": "Model", 
                            "versions": [], 
                            "schedule_timing": 1.0, 
                            "path": "$REPO/TP/Assets/Characters/Char1/Model", 
                            "type": {
                                "code": "Model", 
                                "description": "", 
                                "entity_type": "Type", 
                                "type_id": null, 
                                "target_entity_type": "Task", 
                                "type_id_local": 41, 
                                "type": null, 
                                "name": "Model"
                            }, 
                            "schedule_model": "effort"
                        }, 
                        {
                            "tasks": [], 
                            "description": "", 
                            "entity_type": "Task", 
                            "type_id": 42, 
                            "schedule_constraint": 0, 
                            "schedule_unit": "h", 
                            "name": "LookDev", 
                            "versions": [], 
                            "schedule_timing": 1.0, 
                            "path": "$REPO/TP/Assets/Characters/Char1/LookDev", 
                            "type": {
                                "code": "LookDev", 
                                "description": "", 
                                "entity_type": "Type", 
                                "type_id": null, 
                                "target_entity_type": "Task", 
                                "type_id_local": 42, 
                                "type": null, 
                                "name": "Look Development"
                            }, 
                            "schedule_model": "effort"
                        }, 
                        {
                            "tasks": [], 
                            "description": "", 
                            "entity_type": "Task", 
                            "type_id": 43, 
                            "schedule_constraint": 0, 
                            "schedule_unit": "h", 
                            "name": "Rig", 
                            "versions": [], 
                            "schedule_timing": 1.0, 
                            "path": "$REPO/TP/Assets/Characters/Char1/Rig", 
                            "type": {
                                "code": "Rig", 
                                "description": "", 
                                "entity_type": "Type", 
                                "type_id": null, 
                                "target_entity_type": "Task", 
                                "type_id_local": 43, 
                                "type": null, 
                                "name": "Rig"
                            }, 
                            "schedule_model": "effort"
                        }
                    ], 
                    "schedule_timing": 1.0, 
                    "path": "$REPO/TP/Assets/Characters/Char1", 
                    "schedule_model": "effort", 
                    "type": {
                        "code": "Char", 
                        "description": "", 
                        "entity_type": "Type", 
                        "type_id": null, 
                        "target_entity_type": "Asset", 
                        "type_id_local": 37, 
                        "type": null, 
                        "name": "Character"
                    }, 
                    "name": "Char1"
                }, 
                {
                    "asset_id": 60, 
                    "versions": [], 
                    "code": "Char2", 
                    "description": "", 
                    "entity_type": "Asset", 
                    "type_id": 37, 
                    "schedule_constraint": 0, 
                    "schedule_unit": "h", 
                    "tasks": [
                        {
                            "tasks": [], 
                            "description": "", 
                            "entity_type": "Task", 
                            "type_id": 41, 
                            "schedule_constraint": 0, 
                            "schedule_unit": "h", 
                            "name": "Model", 
                            "versions": [], 
                            "schedule_timing": 1.0, 
                            "path": "$REPO/TP/Assets/Characters/Char2/Model", 
                            "type": {
                                "code": "Model", 
                                "description": "", 
                                "entity_type": "Type", 
                                "type_id": null, 
                                "target_entity_type": "Task", 
                                "type_id_local": 41, 
                                "type": null, 
                                "name": "Model"
                            }, 
                            "schedule_model": "effort"
                        }, 
                        {
                            "tasks": [], 
                            "description": "", 
                            "entity_type": "Task", 
                            "type_id": 42, 
                            "schedule_constraint": 0, 
                            "schedule_unit": "h", 
                            "name": "LookDev", 
                            "versions": [], 
                            "schedule_timing": 1.0, 
                            "path": "$REPO/TP/Assets/Characters/Char2/LookDev", 
                            "type": {
                                "code": "LookDev", 
                                "description": "", 
                                "entity_type": "Type", 
                                "type_id": null, 
                                "target_entity_type": "Task", 
                                "type_id_local": 42, 
                                "type": null, 
                                "name": "Look Development"
                            }, 
                            "schedule_model": "effort"
                        }, 
                        {
                            "tasks": [], 
                            "description": "", 
                            "entity_type": "Task", 
                            "type_id": 43, 
                            "schedule_constraint": 0, 
                            "schedule_unit": "h", 
                            "name": "Rig", 
                            "versions": [], 
                            "schedule_timing": 1.0, 
                            "path": "$REPO/TP/Assets/Characters/Char2/Rig", 
                            "type": {
                                "code": "Rig", 
                                "description": "", 
                                "entity_type": "Type", 
                                "type_id": null, 
                                "target_entity_type": "Task", 
                                "type_id_local": 43, 
                                "type": null, 
                                "name": "Rig"
                            }, 
                            "schedule_model": "effort"
                        }
                    ], 
                    "schedule_timing": 1.0, 
                    "path": "$REPO/TP/Assets/Characters/Char2", 
                    "schedule_model": "effort", 
                    "type": {
                        "code": "Char", 
                        "description": "", 
                        "entity_type": "Type", 
                        "type_id": null, 
                        "target_entity_type": "Asset", 
                        "type_id_local": 37, 
                        "type": null, 
                        "name": "Character"
                    }, 
                    "name": "Char2"
                }
            ], 
            "description": "", 
            "entity_type": "Task", 
            "type_id": null, 
            "schedule_constraint": 0, 
            "schedule_unit": "h", 
            "name": "Characters", 
            "versions": [], 
            "schedule_timing": 1.0, 
            "path": "$REPO/TP/Assets/Characters", 
            "type": null, 
            "schedule_model": "effort"
        }, 
        {
            "tasks": [
                {
                    "asset_id": 64, 
                    "versions": [], 
                    "code": "Prop2", 
                    "description": "", 
                    "entity_type": "Asset", 
                    "type_id": 38, 
                    "schedule_constraint": 0, 
                    "schedule_unit": "h", 
                    "tasks": [
                        {
                            "tasks": [], 
                            "description": "", 
                            "entity_type": "Task", 
                            "type_id": 41, 
                            "schedule_constraint": 0, 
                            "schedule_unit": "h", 
                            "name": "Model", 
                            "versions": [], 
                            "schedule_timing": 1.0, 
                            "path": "$REPO/TP/Assets/Props/Prop2/Model", 
                            "type": {
                                "code": "Model", 
                                "description": "", 
                                "entity_type": "Type", 
                                "type_id": null, 
                                "target_entity_type": "Task", 
                                "type_id_local": 41, 
                                "type": null, 
                                "name": "Model"
                            }, 
                            "schedule_model": "effort"
                        }, 
                        {
                            "tasks": [], 
                            "description": "", 
                            "entity_type": "Task", 
                            "type_id": 42, 
                            "schedule_constraint": 0, 
                            "schedule_unit": "h", 
                            "name": "LookDev", 
                            "versions": [], 
                            "schedule_timing": 1.0, 
                            "path": "$REPO/TP/Assets/Props/Prop2/LookDev", 
                            "type": {
                                "code": "LookDev", 
                                "description": "", 
                                "entity_type": "Type", 
                                "type_id": null, 
                                "target_entity_type": "Task", 
                                "type_id_local": 42, 
                                "type": null, 
                                "name": "Look Development"
                            }, 
                            "schedule_model": "effort"
                        }
                    ], 
                    "schedule_timing": 1.0, 
                    "path": "$REPO/TP/Assets/Props/Prop2", 
                    "schedule_model": "effort", 
                    "type": {
                        "code": "Prop", 
                        "description": "", 
                        "entity_type": "Type", 
                        "type_id": null, 
                        "target_entity_type": "Asset", 
                        "type_id_local": 38, 
                        "type": null, 
                        "name": "Prop"
                    }, 
                    "name": "Prop2"
                }, 
                null
            ], 
            "description": "", 
            "entity_type": "Task", 
            "type_id": null, 
            "schedule_constraint": 0, 
            "schedule_unit": "h", 
            "name": "Props", 
            "versions": [], 
            "schedule_timing": 1.0, 
            "path": "$REPO/TP/Assets/Props", 
            "type": null, 
            "schedule_model": "effort"
        }, 
        {
            "tasks": [
                {
                    "asset_id": 70, 
                    "versions": [], 
                    "code": "Env1", 
                    "description": "", 
                    "entity_type": "Asset", 
                    "type_id": 39, 
                    "schedule_constraint": 0, 
                    "schedule_unit": "h", 
                    "tasks": [
                        {
                            "tasks": [], 
                            "description": "", 
                            "entity_type": "Task", 
                            "type_id": 44, 
                            "schedule_constraint": 0, 
                            "schedule_unit": "h", 
                            "name": "Layout", 
                            "versions": [], 
                            "schedule_timing": 1.0, 
                            "path": "$REPO/TP/Assets/Environments/Env1/Layout", 
                            "type": {
                                "code": "Layout", 
                                "description": "", 
                                "entity_type": "Type", 
                                "type_id": null, 
                                "target_entity_type": "Task", 
                                "type_id_local": 44, 
                                "type": null, 
                                "name": "Layout"
                            }, 
                            "schedule_model": "effort"
                        }, 
                        {
                            "tasks": [
                                {
                                    "asset_id": 73, 
                                    "versions": [], 
                                    "code": "Yapi1", 
                                    "description": "", 
                                    "entity_type": "Asset", 
                                    "type_id": 38, 
                                    "schedule_constraint": 0, 
                                    "schedule_unit": "h", 
                                    "tasks": [
                                        {
                                            "tasks": [], 
                                            "description": "", 
                                            "entity_type": "Task", 
                                            "type_id": 41, 
                                            "schedule_constraint": 0, 
                                            "schedule_unit": "h", 
                                            "name": "Model", 
                                            "versions": [], 
                                            "schedule_timing": 1.0, 
                                            "path": "$REPO/TP/Assets/Environments/Env1/Props/Yapi1/Model", 
                                            "type": {
                                                "code": "Model", 
                                                "description": "", 
                                                "entity_type": "Type", 
                                                "type_id": null, 
                                                "target_entity_type": "Task", 
                                                "type_id_local": 41, 
                                                "type": null, 
                                                "name": "Model"
                                            }, 
                                            "schedule_model": "effort"
                                        }, 
                                        {
                                            "tasks": [], 
                                            "description": "", 
                                            "entity_type": "Task", 
                                            "type_id": 42, 
                                            "schedule_constraint": 0, 
                                            "schedule_unit": "h", 
                                            "name": "LookDev", 
                                            "versions": [], 
                                            "schedule_timing": 1.0, 
                                            "path": "$REPO/TP/Assets/Environments/Env1/Props/Yapi1/LookDev", 
                                            "type": {
                                                "code": "LookDev", 
                                                "description": "", 
                                                "entity_type": "Type", 
                                                "type_id": null, 
                                                "target_entity_type": "Task", 
                                                "type_id_local": 42, 
                                                "type": null, 
                                                "name": "Look Development"
                                            }, 
                                            "schedule_model": "effort"
                                        }
                                    ], 
                                    "schedule_timing": 1.0, 
                                    "path": "$REPO/TP/Assets/Environments/Env1/Props/Yapi1", 
                                    "schedule_model": "effort", 
                                    "type": {
                                        "code": "Prop", 
                                        "description": "", 
                                        "entity_type": "Type", 
                                        "type_id": null, 
                                        "target_entity_type": "Asset", 
                                        "type_id_local": 38, 
                                        "type": null, 
                                        "name": "Prop"
                                    }, 
                                    "name": "Yapi1"
                                }
                            ], 
                            "description": "", 
                            "entity_type": "Task", 
                            "type_id": null, 
                            "schedule_constraint": 0, 
                            "schedule_unit": "h", 
                            "name": "Props", 
                            "versions": [], 
                            "schedule_timing": 1.0, 
                            "path": "$REPO/TP/Assets/Environments/Env1/Props", 
                            "type": null, 
                            "schedule_model": "effort"
                        }
                    ], 
                    "schedule_timing": 1.0, 
                    "path": "$REPO/TP/Assets/Environments/Env1", 
                    "schedule_model": "effort", 
                    "type": {
                        "code": "Exterior", 
                        "description": "", 
                        "entity_type": "Type", 
                        "type_id": null, 
                        "target_entity_type": "Asset", 
                        "type_id_local": 39, 
                        "type": null, 
                        "name": "Exterior"
                    }, 
                    "name": "Env1"
                }, 
                {
                    "asset_id": 76, 
                    "versions": [], 
                    "code": "Env2", 
                    "description": "", 
                    "entity_type": "Asset", 
                    "type_id": 39, 
                    "schedule_constraint": 0, 
                    "schedule_unit": "h", 
                    "tasks": [
                        {
                            "tasks": [], 
                            "description": "", 
                            "entity_type": "Task", 
                            "type_id": 44, 
                            "schedule_constraint": 0, 
                            "schedule_unit": "h", 
                            "name": "Layout", 
                            "versions": [], 
                            "schedule_timing": 1.0, 
                            "path": "$REPO/TP/Assets/Environments/Env2/Layout", 
                            "type": {
                                "code": "Layout", 
                                "description": "", 
                                "entity_type": "Type", 
                                "type_id": null, 
                                "target_entity_type": "Task", 
                                "type_id_local": 44, 
                                "type": null, 
                                "name": "Layout"
                            }, 
                            "schedule_model": "effort"
                        }, 
                        {
                            "tasks": [
                                {
                                    "asset_id": 79, 
                                    "versions": [], 
                                    "code": "Yapi2", 
                                    "description": "", 
                                    "entity_type": "Asset", 
                                    "type_id": 38, 
                                    "schedule_constraint": 0, 
                                    "schedule_unit": "h", 
                                    "tasks": [
                                        {
                                            "tasks": [], 
                                            "description": "", 
                                            "entity_type": "Task", 
                                            "type_id": 41, 
                                            "schedule_constraint": 0, 
                                            "schedule_unit": "h", 
                                            "name": "Model", 
                                            "versions": [], 
                                            "schedule_timing": 1.0, 
                                            "path": "$REPO/TP/Assets/Environments/Env2/Props/Yapi2/Model", 
                                            "type": {
                                                "code": "Model", 
                                                "description": "", 
                                                "entity_type": "Type", 
                                                "type_id": null, 
                                                "target_entity_type": "Task", 
                                                "type_id_local": 41, 
                                                "type": null, 
                                                "name": "Model"
                                            }, 
                                            "schedule_model": "effort"
                                        }, 
                                        {
                                            "tasks": [], 
                                            "description": "", 
                                            "entity_type": "Task", 
                                            "type_id": 42, 
                                            "schedule_constraint": 0, 
                                            "schedule_unit": "h", 
                                            "name": "LookDev", 
                                            "versions": [], 
                                            "schedule_timing": 1.0, 
                                            "path": "$REPO/TP/Assets/Environments/Env2/Props/Yapi2/LookDev", 
                                            "type": {
                                                "code": "LookDev", 
                                                "description": "", 
                                                "entity_type": "Type", 
                                                "type_id": null, 
                                                "target_entity_type": "Task", 
                                                "type_id_local": 42, 
                                                "type": null, 
                                                "name": "Look Development"
                                            }, 
                                            "schedule_model": "effort"
                                        }
                                    ], 
                                    "schedule_timing": 1.0, 
                                    "path": "$REPO/TP/Assets/Environments/Env2/Props/Yapi2", 
                                    "schedule_model": "effort", 
                                    "type": {
                                        "code": "Prop", 
                                        "description": "", 
                                        "entity_type": "Type", 
                                        "type_id": null, 
                                        "target_entity_type": "Asset", 
                                        "type_id_local": 38, 
                                        "type": null, 
                                        "name": "Prop"
                                    }, 
                                    "name": "Yapi2"
                                }
                            ], 
                            "description": "", 
                            "entity_type": "Task", 
                            "type_id": null, 
                            "schedule_constraint": 0, 
                            "schedule_unit": "h", 
                            "name": "Props", 
                            "versions": [], 
                            "schedule_timing": 1.0, 
                            "path": "$REPO/TP/Assets/Environments/Env2/Props", 
                            "type": null, 
                            "schedule_model": "effort"
                        }
                    ], 
                    "schedule_timing": 1.0, 
                    "path": "$REPO/TP/Assets/Environments/Env2", 
                    "schedule_model": "effort", 
                    "type": {
                        "code": "Exterior", 
                        "description": "", 
                        "entity_type": "Type", 
                        "type_id": null, 
                        "target_entity_type": "Asset", 
                        "type_id_local": 39, 
                        "type": null, 
                        "name": "Exterior"
                    }, 
                    "name": "Env2"
                }
            ], 
            "description": "", 
            "entity_type": "Task", 
            "type_id": null, 
            "schedule_constraint": 0, 
            "schedule_unit": "h", 
            "name": "Environments", 
            "versions": [], 
            "schedule_timing": 1.0, 
            "path": "$REPO/TP/Assets/Environments", 
            "type": null, 
            "schedule_model": "effort"
        }
    ], 
    "description": "", 
    "entity_type": "Task", 
    "type_id": null, 
    "schedule_constraint": 0, 
    "schedule_unit": "h", 
    "name": "Assets", 
    "versions": [], 
    "schedule_timing": 1.0, 
    "path": "$REPO/TP/Assets", 
    "type": null, 
    "schedule_model": "effort"
}"""

    assert data == expected_data
