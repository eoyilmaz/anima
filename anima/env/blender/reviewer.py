# -*- coding: utf-8 -*-
import os
import bpy

from stalker import Project, Task, Version, Sequence, Shot
from anima import logger

bl_info = {
    "name": "Stalker Reviewer",
    "description": "Review Stalker task version outputs in Blender.",
    "author": "Erkan Ozgur Yilmaz",
    "version": (0, 1),
    "blender": (2, 71, 0),
    "location": "View3D > Add > Mesh",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"
                "Scripts/My_Script",
    "category": "Object"
}


idname_template = 'stalker.%s_%s_menu'
registered_menus = []


output_types = {
    'image': ['.jpg', '.jpeg', '.png', '.tiff', '.tga'],
    'movie': ['.mov', '.avi', '.webm', '.mpeg', '.mpg']
}


class StripGenerator(object):
    """Generates strips out of tasks given to it.
    """

    def __init__(self):
        pass

    def add_from_task(self, task):
        """adds the latest output of the given task
        """
        if not task:
            # inform the user
            return

        # get the repo
        repo = task.project.repository

        # do it in dirty way
        versions = Version.query\
            .filter(Version.task == task)\
            .order_by(Version.version_number.desc())\
            .all()

        found_output = False
        for v in versions:
            if len(v.outputs):
                # get all outputs of this version
                for output in v.outputs:
                    output_absolute_full_path = os.path.expandvars(
                        output.full_path
                    )
                    self.add_output(output_absolute_full_path)
                    found_output = True
                    break

            if found_output:
                break

    def add_output(self, full_path, name=None, channel=1):
        """adds the media in the given path to the time line

        :param str full_path: The path of the file
        """
        logger.debug('adding output from: %s' % full_path)
        extension = os.path.splitext(full_path)[-1].lower()

        logger.debug('extension: %s' % extension)

        output_type = None
        for key in output_types.keys():
            if extension in output_types[key]:
                output_type = key
                break

        if output_type == 'image':
            logger.debug('output is image')
            bpy.ops.sequencer.image_strip_add(
                directory=os.path.dirname(full_path),
                files=[
                    {
                        "name": os.path.basename(full_path),
                        # "name": os.path.basename(full_path)
                    }
                ],
                relative_path=True,
                frame_start=1,
                frame_end=26,
                channel=channel
            )
        elif output_type == 'movie':
            logger.debug('output is movie')
            logger.debug('full_path: %s' % full_path)
            bpy.ops.sequencer.movie_strip_add(
                filepath=full_path,
                files=[
                    {
                        "name": os.path.basename(full_path),
                        # "name": os.path.basename(full_path)
                    }
                ],
                relative_path=True,
                frame_start=1,
                channel=channel
            )
        else:
            logger.debug('output_type is unknown: %s' % output_type)

    def storyboard(self, task):
        """When a Scene task is given it will create a strip from the output of
        the Storyboard task under it.

        :param task: A :class:`stalker.models.task.Task` class instance.
        """
        # get the storyboard task
        storyboard = Task.query\
            .filter(Task.parent == task)\
            .filter(Task.name == 'Storyboard')\
            .first()

        self.add_from_task(storyboard)

    def previs(self, task):
        """when a Shot task is given it will create a strip from the output of
        the Previs task under it.

        :param task: A :class:`stalker.models.task.Task` class instance.
        """
        # get the previs task
        previs = Task.query\
            .filter(Task.parent == task)\
            .filter(Task.name == 'Previs')\
            .first()

        self.add_from_task(previs)

    def animation(self, task):
        """when a Shot task is given it will create a strip from the output of
        the Animation task under it.

        :param task: A :class:`stalker.models.task.Task` class instance.
        """
        # get the storyboard task
        animation = Task.query\
            .filter(Task.parent == task)\
            .filter(Task.name == 'Animation')\
            .first()

        self.add_from_task(animation)

    def lighting(self, task):
        """when a Shot task is given it will create a strip from the output of
        the Lighting task under it.

        :param task: A :class:`stalker.models.task.Task` class instance.
        """
        # get the storyboard task
        animation = Task.query\
            .filter(Task.parent == task)\
            .filter(Task.name == 'Animation')\
            .first()

        self.add_from_task(animation)

    def comp(self, task):
        """when a Shot task is given it will create a strip from the output of
        the Compositing task under it.

        :param task: A :class:`stalker.models.task.Task` class instance.
        """
        pass


class StalkerMenu(bpy.types.Menu):
    """The Stalker menu for Blender
    """
    bl_label = "Stalker..."
    bl_idname = 'stalker.main_menu'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.menu(StalkerAddFromProjectMenu.bl_idname,
                    text="Add From Project")


def draw_stalker_entity_menu_item(self, context):
    """draws one menu item
    """
    logger.debug('entity_id   : %s' % self.stalker_entity_id)
    logger.debug('entity_name : %s' % self.stalker_entity_name)


def draw_stalker_project_menu_item(self, context):
    """draws one menu item
    """
    logger.debug('entity_id   : %s' % self.stalker_entity_id)
    logger.debug('entity_name : %s' % self.stalker_entity_name)

    layout = self.layout

    # get the project
    project = Project.query.get(self.stalker_entity_id)
    all_seqs = Sequence.query\
        .filter(Sequence.project == project)\
        .order_by(Sequence.name)\
        .all()
    for seq in all_seqs:
        idname = idname_template % (seq.entity_type, seq.id)
        layout.menu(idname, text=seq.name)


def draw_stalker_sequence_menu_item(self, context):
    """draws one menu item
    """
    logger.debug('entity_id   : %s' % self.stalker_entity_id)
    logger.debug('entity_name : %s' % self.stalker_entity_name)

    layout = self.layout

    # get the sequence
    seq = Sequence.query.get(self.stalker_entity_id)

    # add all the child tasks under it
    for scene in sorted(seq.children, key=lambda x: x.name):
        # op = layout.operator(StalkerSceneMenu.bl_idname, text=scene.name)
        # op.stalker_entity_id = scene.id
        # op.stalker_entity_name = scene.name
        idname = idname_template % (scene.entity_type, scene.id)
        layout.menu(idname, text=scene.name)


def draw_stalker_scene_menu_item(self, context):
    """draws one scene menu item
    """
    logger.debug('entity_id   : %s' % self.stalker_entity_id)
    logger.debug('entity_name : %s' % self.stalker_entity_name)

    layout = self.layout

    scene = Task.query.get(self.stalker_entity_id)

    # Add Everything
    op = layout.operator(
        StalkerSceneAddEverythingOperator.bl_idname,
        text='Add Everything'
    )
    op.stalker_entity_id = scene.id
    op.stalker_entity_name = scene.name

    layout.separator()

    # Add Storyboard Only
    op = layout.operator(
        StalkerSceneAddStoryboardOperator.bl_idname,
        text='Storyboard'
    )
    op.stalker_entity_id = scene.id
    op.stalker_entity_name = scene.name

    # Add Previs Only
    op = layout.operator(
        StalkerSceneAddPrevisOperator.bl_idname,
        text='Previs'
    )
    op.stalker_entity_id = scene.id
    op.stalker_entity_name = scene.name

    layout.separator()

    # Add From Shots Menu
    idname = '%s%s' % (
        idname_template % (scene.entity_type, scene.id),
        '_add_from_shots_menu'
    )
    layout.menu(idname)


def draw_stalker_scene_add_from_shots_menu_item(self, context):
    """draws one scene/add from shots scene menu item
    """

    logger.debug('entity_id   : %s' % self.stalker_entity_id)
    logger.debug('entity_name : %s' % self.stalker_entity_name)

    layout = self.layout

    scene = Task.query.get(self.stalker_entity_id)

    # Add All Shot Task Outputs
    op = layout.operator(
        StalkerSceneAddAllShotOutputsOperator.bl_idname,
        text='Add All Shot Outputs'
    )
    op.stalker_entity_id = scene.id
    op.stalker_entity_name = scene.name

    # separator
    layout.separator()

    # Previs
    op = layout.operator(
        StalkerSceneAddAllShotPrevisOutputsOperator.bl_idname,
        text='Previs'
    )
    op.stalker_entity_id = scene.id
    op.stalker_entity_name = scene.name

    # Animation
    op = layout.operator(
        StalkerSceneAddAllShotAnimationOutputsOperator.bl_idname,
        text='Animation'
    )
    op.stalker_entity_id = scene.id
    op.stalker_entity_name = scene.name

    # Lighting
    op = layout.operator(
        StalkerSceneAddAllShotLightingOutputsOperator.bl_idname,
        text='Lighting'
    )
    op.stalker_entity_id = scene.id
    op.stalker_entity_name = scene.name

    # Comp
    op = layout.operator(
        StalkerSceneAddAllShotCompOutputsOperator.bl_idname,
        text='Comp'
    )
    op.stalker_entity_id = scene.id
    op.stalker_entity_name = scene.name

    # separator
    layout.separator()

    # then add menu for each shot under its "Shots" tasks
    shots_task = Task.query\
        .filter(Task.parent == scene)\
        .filter(Task.name == 'Shots')\
        .first()

    if shots_task:
        for shot in shots_task.children:
            # add a shot menu
            idname = idname_template % (shot.entity_type, shot.id)
            layout.menu(idname)


def draw_stalker_shot_menu_item(self, context):
    """draws one menu item
    """
    logger.debug('entity_id   : %s' % self.stalker_entity_id)
    logger.debug('entity_name : %s' % self.stalker_entity_name)

    layout = self.layout

    # get the sequence

    shot = Shot.query.get(self.stalker_entity_id)

    # add all the child tasks under it
    # for scene in sorted(seq.children, key=lambda x: x.name):
    #     # op = layout.operator(StalkerSceneMenu.bl_idname, text=scene.name)
    #     # op.stalker_entity_id = scene.id
    #     # op.stalker_entity_name = scene.name
    #     idname = idname_template % (scene.entity_type, scene.id)
    #     layout.menu(idname, text=scene.name)

    # add a menu operator for
    # Add All Task Outputs
    op = layout.operator(
        StalkerShotAddAllTaskOutputsOperator.bl_idname,
        text='Add All Task Outputs'
    )
    op.stalker_entity_id = self.stalker_entity_id
    op.stalker_entity_name = self.stalker_entity_name

    # ------
    # Add a separator
    layout.separator()

    # Previs
    op = layout.operator(
        StalkerShotAddPrevisOutputOperator.bl_idname,
        text='Previs'
    )
    op.stalker_entity_id = self.stalker_entity_id
    op.stalker_entity_name = self.stalker_entity_name

    # Animation
    op = layout.operator(
        StalkerShotAddAnimationOutputOperator.bl_idname,
        text='Animation'
    )
    op.stalker_entity_id = self.stalker_entity_id
    op.stalker_entity_name = self.stalker_entity_name

    # Lighting
    op = layout.operator(
        StalkerShotAddLightingOutputOperator.bl_idname,
        text='Lighting'
    )
    op.stalker_entity_id = self.stalker_entity_id
    op.stalker_entity_name = self.stalker_entity_name

    # Comp
    op = layout.operator(
        StalkerShotAddCompOutputOperator.bl_idname,
        text='Comp'
    )
    op.stalker_entity_id = self.stalker_entity_id
    op.stalker_entity_name = self.stalker_entity_name


class StalkerAddFromProjectMenu(bpy.types.Menu):
    """The Add From Project menu for Blender"""
    bl_label = "From Project..."
    bl_idname = "stalker.add_from_project_menu"

    def draw(self, context):
        layout = self.layout
        for project in Project.query.order_by(Project.name).all():
            idname = 'stalker.%s_%s_menu' % (project.entity_type, project.id)
            layout.menu(idname)


class StalkerSceneAddEverythingOperator(bpy.types.Operator):
    """Adds all of the outputs of everything under this scene"""

    bl_label = 'Add Everything'
    bl_idname = 'stalker.scene_add_everything_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        scene = Task.query.get(self.stalker_entity_id)

        logger.debug('scene: %s' % scene)

        # generate storyboard
        strip_gen = StripGenerator()
        strip_gen.storyboard(scene)
        strip_gen.previs(scene)
        strip_gen.animation(scene)
        strip_gen.lighting(scene)
        strip_gen.comp(scene)

        # go to each Shot and add latest outputs of everything under it
        for task in scene.walk_hierarchy():
            if isinstance(task, Shot):
                # find the animation task under it
                animation_task = Task.query.filter(Task.parent_id==task.id).filter(Task.name=='Animation').first()

        return set(['FINISHED'])


class StalkerSceneAddStoryboardOperator(bpy.types.Operator):
    """Adds the storyboard output of this scene"""

    bl_label = 'Add Storyboard Only'
    bl_idname = 'stalker.scene_add_storyboard_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        scene = Task.query.get(self.stalker_entity_id)

        logger.debug('scene: %s' % scene)

        # generate storyboard
        strip_gen = StripGenerator()
        strip_gen.storyboard(scene)

        return set(['FINISHED'])


class StalkerSceneAddPrevisOperator(bpy.types.Operator):
    """Adds the previs output of this scene"""

    bl_label = 'Add Previs Only'
    bl_idname = 'stalker.scene_add_previs_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        scene = Task.query.get(self.stalker_entity_id)

        logger.debug('scene: %s' % scene)

        # generate storyboard
        strip_gen = StripGenerator()
        strip_gen.previs(scene)

        return set(['FINISHED'])


class StalkerSceneAddAllShotOutputsOperator(bpy.types.Operator):
    """Adds all of the shot task outputs under this scene"""

    bl_label = 'Add All Shot Outputs'
    bl_idname = 'stalker.scene_add_all_shot_outputs_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        scene = Task.query.get(self.stalker_entity_id)

        logger.debug('scene: %s' % scene)

        # find the "Shots" Task and get all the shots under it
        # for each shot add the animation, lighting and comp

        # for shot in scene.children
        # # generate storyboard
        # strip_gen = StripGenerator()
        # strip_gen.previs(scene)
        # strip_gen.animation(scene)
        # strip_gen.lighting(scene)
        # strip_gen.comp(scene)

        return set(['FINISHED'])


class StalkerSceneAddAllShotPrevisOutputsOperator(bpy.types.Operator):
    """Adds all the Previs task outputs from all of the shots"""

    bl_label = 'Add All Shot Previs Outputs'
    bl_idname = 'stalker.scene_add_all_shot_previs_outputs_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        scene = Task.query.get(self.stalker_entity_id)

        logger.debug('scene: %s' % scene)

        # find the "Shots" Task and get all the shots under it
        # for each shot add the animation, lighting and comp

        # for shot in scene.children
        # # generate storyboard
        # strip_gen = StripGenerator()
        # strip_gen.previs(scene)
        # strip_gen.animation(scene)
        # strip_gen.lighting(scene)
        # strip_gen.comp(scene)

        return set(['FINISHED'])


class StalkerSceneAddAllShotAnimationOutputsOperator(bpy.types.Operator):
    """Adds all the Animation task outputs from all of the shots"""

    bl_label = 'Add All Shot Animation Outputs'
    bl_idname = 'stalker.scene_add_all_shot_animation_outputs_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        scene = Task.query.get(self.stalker_entity_id)

        logger.debug('scene: %s' % scene)

        # find the "Shots" Task and get all the shots under it
        # for each shot add the animation, lighting and comp

        # for shot in scene.children
        # # generate storyboard
        # strip_gen = StripGenerator()
        # strip_gen.previs(scene)
        # strip_gen.animation(scene)
        # strip_gen.lighting(scene)
        # strip_gen.comp(scene)

        return set(['FINISHED'])


class StalkerSceneAddAllShotLightingOutputsOperator(bpy.types.Operator):
    """Adds all the Lighting task outputs from all of the shots"""

    bl_label = 'Add All Shot Lighting Outputs'
    bl_idname = 'stalker.scene_add_all_shot_lighting_outputs_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        scene = Task.query.get(self.stalker_entity_id)

        logger.debug('scene: %s' % scene)

        # find the "Shots" Task and get all the shots under it
        # for each shot add the animation, lighting and comp

        # for shot in scene.children
        # # generate storyboard
        # strip_gen = StripGenerator()
        # strip_gen.previs(scene)
        # strip_gen.animation(scene)
        # strip_gen.lighting(scene)
        # strip_gen.comp(scene)

        return set(['FINISHED'])


class StalkerSceneAddAllShotCompOutputsOperator(bpy.types.Operator):
    """Adds all the Comp task outputs from all of the shots"""

    bl_label = 'Add All Shot Comp Outputs'
    bl_idname = 'stalker.scene_add_all_shot_comp_outputs_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        scene = Task.query.get(self.stalker_entity_id)

        logger.debug('scene: %s' % scene)

        # find the "Shots" Task and get all the shots under it
        # for each shot add the animation, lighting and comp

        # for shot in scene.children
        # # generate storyboard
        # strip_gen = StripGenerator()
        # strip_gen.previs(scene)
        # strip_gen.animation(scene)
        # strip_gen.lighting(scene)
        # strip_gen.comp(scene)

        return set(['FINISHED'])


class StalkerShotAddAllTaskOutputsOperator(bpy.types.Operator):
    """Adds all task outputs of this shot"""

    bl_label = 'Add All Task Outputs'
    bl_idname = 'stalker.shot_add_all_task_outputs_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        shot = Shot.query.get(self.stalker_entity_id)

        logger.debug('shot: %s' % shot)

        # find Previs, Animation, Lighting and Comp tasks

        # # generate storyboard
        # strip_gen = StripGenerator()
        # strip_gen.previs(scene)
        # strip_gen.animation(scene)
        # strip_gen.lighting(scene)
        # strip_gen.comp(scene)

        return set(['FINISHED'])


class StalkerShotAddPrevisOutputOperator(bpy.types.Operator):
    """Adds just the Previs output of this shot"""

    bl_label = 'Add Previs Output'
    bl_idname = 'stalker.shot_add_previs_output_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        shot = Shot.query.get(self.stalker_entity_id)

        logger.debug('shot: %s' % shot)

        # find Previs, Animation, Lighting and Comp tasks

        # # generate storyboard
        # strip_gen = StripGenerator()
        # strip_gen.previs(shot)

        return set(['FINISHED'])


class StalkerShotAddAnimationOutputOperator(bpy.types.Operator):
    """Adds just the Animation output of this shot"""

    bl_label = 'Add Animation Output'
    bl_idname = 'stalker.shot_add_animation_output_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        shot = Shot.query.get(self.stalker_entity_id)

        logger.debug('shot: %s' % shot)

        # find Previs, Animation, Lighting and Comp tasks

        # # generate storyboard
        # strip_gen = StripGenerator()
        # strip_gen.animation(shot)

        return set(['FINISHED'])


class StalkerShotAddLightingOutputOperator(bpy.types.Operator):
    """Adds just the Lighting output of this shot"""

    bl_label = 'Add Lighting Output'
    bl_idname = 'stalker.shot_add_lighting_output_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        shot = Shot.query.get(self.stalker_entity_id)

        logger.debug('shot: %s' % shot)

        # find Previs, Animation, Lighting and Comp tasks

        # # generate storyboard
        # strip_gen = StripGenerator()
        # strip_gen.lighting(shot)

        return set(['FINISHED'])


class StalkerShotAddCompOutputOperator(bpy.types.Operator):
    """Adds just the Comp output of this shot"""

    bl_label = 'Add Comp Output'
    bl_idname = 'stalker.shot_add_comp_output_op'

    stalker_entity_id = bpy.props.IntProperty(name='stalker_entity_id')
    stalker_entity_name = bpy.props.StringProperty(name='stalker_entity_name')

    def execute(self, context):
        logger.debug('inside %s.execute()' % self.__class__.__name__)

        # get the scene and all the shots under it
        shot = Shot.query.get(self.stalker_entity_id)

        logger.debug('shot: %s' % shot)

        # find Previs, Animation, Lighting and Comp tasks

        # # generate storyboard
        # strip_gen = StripGenerator()
        # strip_gen.comp(shot)

        return set(['FINISHED'])


# class Reviewer(bpy.types.Panel):
#     """Stalker version outputs Reviewer
#     """
#     bl_idname = "stalker.reviewer"       # unique identifier for buttons and
#                                          # menu items to reference.
#     bl_label = "Stalker Reviewer Panel"  # display name in the interface.
#     bl_space_type = 'SEQUENCE_EDITOR'
#     bl_region_type = 'UI'
#
#     def draw(self, context):
#         layout = self.layout
#
#         selected_sequences = context.selected_sequences
#         selected_sequence_names = ''
#         if selected_sequences:
#             seq_names = []
#             for seq in selected_sequences:
#                 seq_names.append(seq.name)
#             seq_names = ','.join(selected_sequence_names)
#
#         row = layout.row()
#         row.label(text="Hello world!", icon='WORLD_DATA')
#
#         row = layout.row()
#         row.label(text="Active sequence is: %s" % selected_sequence_names)
#
#         #row = layout.row()
#         #row.prop(selected_sequences, "name")
#
#         # row = layout.row()
#         # row.operator("mesh.primitive_cube_add")


def draw_stalker_menu(self, context):
    layout = self.layout
    layout.menu(StalkerMenu.bl_idname)


def generate_op_class(entity,
                      draw=draw_stalker_entity_menu_item,
                      idpostfix='',
                      label=None):
    """generates clunky opclass for given entity

    :param entity: The Stalker entity
    :param draw: The draw function, defaults to draw_stalker_entity_menu_item
    :param label: Label of this menu
    """
    idname = '%s%s' % (
        idname_template % (entity.entity_type, entity.id),
        idpostfix
    )
    return type(
        idname,
        (bpy.types.Menu, ),
        {
            'bl_idname': idname,
            'bl_label': label if label else entity.name,
            'stalker_entity_id': entity.id,
            'stalker_entity_type': entity.entity_type,
            'stalker_entity_name': entity.name,
            'draw': draw
        }
    )


def register():
    """register the addon
    """
    # do database setup
    from anima.utils import do_db_setup
    do_db_setup()

    #
    # generate one class for each menu item
    #
    # This is a limitation of Blender, as of 2.71 the ``layout.menu()`` method
    # is not returning any item to set the property to, so clever guys around
    # the blender community are suggesting to dynamically generating new
    # classes which is a very very very very bad practice, which essentially
    # does nothing better than bloating the python name space.
    #
    for project in Project.query.order_by(Project.name).all():
        opclass = generate_op_class(
            project,
            draw=draw_stalker_project_menu_item
        )

        bpy.utils.register_class(opclass)

        # append them to the lookup table so we will be able to unregister
        # them later on
        registered_menus.append(opclass)

        # for each project register a sequence menu
        all_seqs = Sequence.query.\
            filter(Sequence.project == project)\
            .order_by(Sequence.name).all()
        for seq in all_seqs:
            opclass = generate_op_class(
                seq,
                draw=draw_stalker_sequence_menu_item
            )
            bpy.utils.register_class(opclass)
            registered_menus.append(opclass)

            # for each sequence register a scene menu
            for sce in seq.children:
                opclass = generate_op_class(
                    sce,
                    draw=draw_stalker_scene_menu_item
                )
                bpy.utils.register_class(opclass)
                registered_menus.append(opclass)

                # generate a "Add From Shots" menu for each of them
                opclass = generate_op_class(
                    sce,
                    draw=draw_stalker_scene_add_from_shots_menu_item,
                    idpostfix='_add_from_shots_menu',
                    label='Add From Shots'
                )
                bpy.utils.register_class(opclass)
                registered_menus.append(opclass)

        # for each Shot generate a menu item
        for shot in Shot.query.filter(Shot.project == project).all():
            opclass = generate_op_class(
                shot,
                draw=draw_stalker_shot_menu_item
            )
            bpy.utils.register_class(opclass)
            registered_menus.append(opclass)

    bpy.utils.register_class(StalkerMenu)
    bpy.utils.register_class(StalkerAddFromProjectMenu)

    bpy.utils.register_class(StalkerSceneAddEverythingOperator)
    bpy.utils.register_class(StalkerSceneAddStoryboardOperator)
    bpy.utils.register_class(StalkerSceneAddPrevisOperator)

    bpy.utils.register_class(StalkerSceneAddAllShotOutputsOperator)
    bpy.utils.register_class(StalkerSceneAddAllShotPrevisOutputsOperator)
    bpy.utils.register_class(StalkerSceneAddAllShotAnimationOutputsOperator)
    bpy.utils.register_class(StalkerSceneAddAllShotLightingOutputsOperator)
    bpy.utils.register_class(StalkerSceneAddAllShotCompOutputsOperator)

    bpy.utils.register_class(StalkerShotAddAllTaskOutputsOperator)
    bpy.utils.register_class(StalkerShotAddPrevisOutputOperator)
    bpy.utils.register_class(StalkerShotAddAnimationOutputOperator)
    bpy.utils.register_class(StalkerShotAddLightingOutputOperator)
    bpy.utils.register_class(StalkerShotAddCompOutputOperator)

    bpy.types.SEQUENCER_MT_add.append(draw_stalker_menu)


def unregister():
    """unregister the addon
    """
    bpy.utils.unregister_class(StalkerMenu)
    bpy.utils.unregister_class(StalkerAddFromProjectMenu)

    bpy.utils.unregister_class(StalkerSceneAddEverythingOperator)
    bpy.utils.unregister_class(StalkerSceneAddStoryboardOperator)
    bpy.utils.unregister_class(StalkerSceneAddPrevisOperator)

    bpy.utils.unregister_class(StalkerSceneAddAllShotOutputsOperator)
    bpy.utils.unregister_class(StalkerSceneAddAllShotPrevisOutputsOperator)
    bpy.utils.unregister_class(StalkerSceneAddAllShotAnimationOutputsOperator)
    bpy.utils.unregister_class(StalkerSceneAddAllShotLightingOutputsOperator)
    bpy.utils.unregister_class(StalkerSceneAddAllShotCompOutputsOperator)

    bpy.utils.unregister_class(StalkerShotAddPrevisOutputOperator)
    bpy.utils.unregister_class(StalkerShotAddAnimationOutputOperator)
    bpy.utils.unregister_class(StalkerShotAddLightingOutputOperator)
    bpy.utils.unregister_class(StalkerShotAddCompOutputOperator)

    # unregister dynamically created menu items
    for opclass in registered_menus:
        bpy.utils.unregister_class(opclass)

    bpy.types.SEQUENCER_MT_add.remove(draw_stalker_menu)


if __name__ == '__main__':
    register()
