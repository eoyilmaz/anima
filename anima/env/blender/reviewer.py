# -*- coding: utf-8 -*-

import bpy
from stalker import db, Task, Shot


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


class Reviewer(bpy.types.Panel):
    """Stalker version outputs Reviewer
    """
    bl_idname = "object.stalker_reviewer"  # unique identifier for buttons and
                                           # menu items to reference.
    bl_label = "Stalker Reviewer Panel"    # display name in the interface.
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        selected_sequences = context.selected_sequences
        selected_sequence_names = []
        for seq in selected_sequences:
            selected_sequence_names.append(seq.name)
        selected_sequence_names = ','.join(selected_sequence_names)

        row = layout.row()
        row.label(text="Hello world!", icon='WORLD_DATA')

        row = layout.row()
        row.label(text="Active sequence is: %s" % selected_sequence_names)

        row = layout.row()
        row.prop(selected_sequences, "name")

        # row = layout.row()
        # row.operator("mesh.primitive_cube_add")


def register():
    """register the addon
    """
    bpy.utils.register_class(Reviewer)


def unregister():
    """unregister the addon
    """
    bpy.utils.unregister_class(Reviewer)


if __name__ == '__main__':
    register()
