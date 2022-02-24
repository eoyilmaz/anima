# This example assumes we have a mesh object in edit-mode

import bpy
import bmesh

# get selection
selection = bpy.context.selected_objects

curve_obj = selection[0]
mesh_obj = selection[1]

# store curve coordinates
curve_coordinates = [v.co for v in curve_obj.data.vertices]

print(curve_obj)
print(mesh_obj)
# Get the active mesh
particle_system = mesh_obj.particle_systems[0]

# get the segment count
segment_count = particle_system.settings.hair_step


particles = particle_system.particles

reverse = False

if reverse:
    index_function = lambda x, y: x * (segment_count + 1) + segment_count -  y
else:
    index_function = lambda x, y: x * (segment_count + 1) + y


for i,h in enumerate(particles):
    index = i * (segment_count + 1)
    h.location.x = curve_coordinates[index].x
    h.location.y = curve_coordinates[index].y
    h.location.z = curve_coordinates[index].z
    h.prev_location.x = curve_coordinates[index].x
    h.prev_location.y = curve_coordinates[index].y
    h.prev_location.z = curve_coordinates[index].z
    for j, pv in enumerate(h.hair_keys):
        index = index_function(i, j)
        pv.co.x = curve_coordinates[index].x
        pv.co.y = curve_coordinates[index].y
        pv.co.z = curve_coordinates[index].z


#bpy.context.object.modifiers["ParticleSystem 1"].show_viewport = False
#bpy.ops.particle.particle_edit_toggle()
#bpy.context.scene.tool_settings.particle_edit.tool = 'ADD'
#bpy.context.scene.tool_settings.particle_edit.use_default_interpolate = True
#bpy.ops.particle.brush_edit(stroke=[{"name":"", "location":(4.271749973297119, -11.9777193069458, 56.15434646606445), "mouse":(), "pressure":0, "size":0, "pen_flip":False, "time":0, "is_start":False}])

#bpy.ops.particle.brush_edit(stroke=[{"name":"", "location":(0, 0, 0), "mouse":(354, 384), "pressure":0, "size":0, "pen_flip":False, "time":0, "is_start":False}])
