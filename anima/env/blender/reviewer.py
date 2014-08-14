# -*- coding: utf-8 -*-

import bpy
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel = logging.DEBUG

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


class StripGenerator(object):
    """Generates strips
    """

    def __init__(self):
        pass

    def storyboard(self):
        """When a task with Scene type is given it will return the storyboard
        """
        pass

    def previs(self):
        """when a Shot task
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
    from stalker import Project, Sequence
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
    from stalker import Sequence

    seq = Sequence.query.get(self.stalker_entity_id)

    # add all the child tasks under it
    for scene in sorted(seq.children, key=lambda x: x.name):
        op = layout.operator(StalkerSceneMenu.bl_idname, text=scene.name)
        op.scene_id = scene.id
        op.scene_name = scene.name


class StalkerAddFromProjectMenu(bpy.types.Menu):
    """The Add From Project menu for Blender
    """
    bl_label = "From Project..."
    bl_idname = "stalker.add_from_project_menu"

    def draw(self, context):
        layout = self.layout
        from stalker import Project
        for project in Project.query.order_by(Project.name).all():
            idname = 'stalker.%s_%s_menu' % (project.entity_type, project.id)
            layout.menu(idname)


class StalkerSceneMenu(bpy.types.Operator):
    """The Scene menu for Blender
    """

    bl_label = 'Scene'
    bl_idname = 'stalker.scene_menu'

    scene_id = bpy.props.IntProperty(name='scene_id')
    scene_name = bpy.props.StringProperty(name='scene_name')

    def execute(self, context):
        logger.debug('inside StalkerSceneMenu.execute()')

        # get the scene and all the shots under it
        from stalker import Task, Shot
        scene = Task.query.get(self.scene_id)

        # find the "Shots" task
        shots_task = Task.query\
            .filter_by(parent=scene)\
            .filter_by(name='Shots')\
            .first()

        if not shots_task:
            return set(['FINISHED'])

        # get all the shots under it
        for shot in shots_task.children:
            logger.debug('shot.name: %s' % shot.name)

            # get the

        return set(['FINISHED'])


class StalkerSceneAddAllShots(bpy.types.Operator):
    """Adds all the Shots of this Sequence to the sequencer"""

    bl_idname = 'sequencer.stalker_sequence_add_all_shots'
    bl_label = 'Add All Shots'
    bl_options = set(['REGISTER', 'UNDO'])

    def execute(self, context):

        logger.debug(self.bl_label)
        # get all the shots under this sequence

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


def generate_op_class(entity, draw=draw_stalker_entity_menu_item):
    """generates clunky opclass for given entity

    :param entity: The Stalker entity
    :param draw: The draw function, defaults to draw_stalker_entity_menu_item
    """
    idname = idname_template % (entity.entity_type, entity.id)
    return type(
        idname,
        (bpy.types.Menu, ),
        {
            'bl_idname': idname,
            'bl_label': entity.name,
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
    from stalker import Project, Sequence
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

    bpy.utils.register_class(StalkerMenu)
    bpy.utils.register_class(StalkerAddFromProjectMenu)
    bpy.utils.register_class(StalkerSceneMenu)
    bpy.utils.register_class(StalkerSceneAddAllShots)

    bpy.types.SEQUENCER_MT_add.append(draw_stalker_menu)


def unregister():
    """unregister the addon
    """
    bpy.utils.unregister_class(StalkerMenu)
    bpy.utils.unregister_class(StalkerAddFromProjectMenu)
    bpy.utils.unregister_class(StalkerSceneMenu)
    bpy.utils.unregister_class(StalkerSceneAddAllShots)

    # unregister dynamically created menu items
    for opclass in registered_menus:
        bpy.utils.unregister_class(opclass)

    bpy.types.SEQUENCER_MT_add.remove(draw_stalker_menu)


if __name__ == '__main__':
    register()
