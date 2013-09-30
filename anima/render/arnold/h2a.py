# This code is called when instances of this SOP cook.

import hou
#import jinja2

node = hou.pwd()
geo = node.geometry()

# Add code to modify the contents of geo.

#output_file_path = node.param('output_file')

#['addVertex', 'attribType', 'attribValue', 'attribValueAt',
# 'closed', 'edges', 'floatAttribValue', 'floatListAttribValue', 'geometry', 'groups', 'intAttribValue',
# 'intListAttribValue', 'intrinsicNames', 'intrinsicValue', 'intrinsicValueDict', 'isClosed', 'nearestToPosition',
# 'normal', 'numEdges', 'numVertices', 'number', 'positionAt', 'setAttribValue', 'setIntrinsicValue', 'setIsClosed',
# 'stringAttribValue', 'stringListAttribValue', 'this', 'thisown', 'type', 'vertex', 'vertices']


baseTemplate = """
options
{
 name options
 xres 1920
 yres 540
 aspect_ratio 1.0
 preserve_scene_data on
 procedural_force_expand on
 binary_ass off
}

curves
{
{{curve_data}}
}
"""

curve_data = """
 name %(name)s
 num_points %(curve_count)i 1 UINT
  %(number_of_points_per_curve)s
 points $(point_count)i 1 POINT
  %(point_positions)s
 radius $(point_count)i 1 FLOAT
  %(radius)s
 basis "catmull-rom"
 mode "ribbon"
 min_pixel_width 0
 visibility 65523
 receive_shadows on
 self_shadows on
 matrix
  1 0 0 0
  0 1 0 0
  0 0 1 0
  0 0 0 1
 shader ""
 opaque on
 sss_sample_spacing 0.100000001
 sss_sample_distribution "blue_noise"
 declare curve_id uniform UINT
 curve_id %(curve_count)i 1 UINT
  %(curve_ids)s
"""

curve_count = geo.intrinsicValue('primitivecount')
point_count = geo.intrinsicValue('pointcount')

number_of_points_per_curve = []
point_positions = []
curve_ids = range(curve_count)
radius = []
for prim in geo.prims():
    curve = prim
    numVertices = curve.numVertices()
    number_of_points_per_curve.append(numVertices)
    for vertex in prim.vertices():
        point = vertex.point()
        point_positions.extend(point.position())
        radius.append(vertex.attribValue('width'))

rendered_curve_data = curve_data % {
    'name': 'sero_fur',
    'curve_count': curve_count,
    'number_of_points_per_curve': ' '.join(map(str, number_of_points_per_curve)),
    'point_count': point_count,
    'point_positions': ' '.join(map(str, point_positions)),
    'radius': ' '.join(map(str, radius)),
    'curve_ids': ' '.join(map(str, curve_ids))
}

print rendered_curve_data

