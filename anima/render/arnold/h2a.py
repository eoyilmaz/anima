# This code is called when instances of this SOP cook.
import gzip

import hou
import os
from sqlalchemy.sql.expression import false


def curves2ass(ass_path):
    """exports the node content to ass file
    """

    # MyFur.ass
    # MyFur.ass.gz
    # MyFur.asstoc
    parts = os.path.splitext(ass_path)
    extension = parts[1]
    use_gzip = False
    if extension == '.gz':
        use_gzip = True
        basename = os.path.splitext(parts[0])[0]
    else:
        basename = parts[0]

    asstoc_path = basename + '.asstoc'

    node = hou.pwd()
    geo = node.geometry()

    base_template = """
options
{
 name options
 xres 1920
 yres 1080
 aspect_ratio 1.0
 preserve_scene_data on
 procedural_force_expand on
 binary_ass off
}

curves
{
 %(curve_data)s
}

hair
{
 name aiHair1
 rootcolor 0.1 0.1 0.1
 tipcolor 0.5 0.5 0.5
 opacity 1 1 1
 ambdiff 0.6
 spec 1
 spec_color 1 1 1
 spec_shift 0
 gloss 10
 spec2 0
 spec2_color 1 0.4 0.1
 spec2_shift 0
 gloss2 7
 kd_ind 0
 uparam "uparamcoord"
 vparam "vparamcoord"
 diffuse_cache off
 aov_direct_diffuse "direct_diffuse"
 aov_direct_specular "direct_specular"
 aov_indirect_diffuse "indirect_diffuse"
}

MayaShadingEngine
{
 name curveShape1@SG
 beauty aiHair1
}
    """

    curve_data = """
 name %(name)s
 num_points %(curve_count)i 1 UINT
  %(number_of_points_per_curve)s
 points %(point_count)s 1 POINT
  %(point_positions)s
 radius %(radius_count)s 1 FLOAT
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
 shader "curveShape1@SG"
 opaque on
 sss_sample_spacing 0.100000001
 sss_sample_distribution "blue_noise"
 declare uparamcoord uniform FLOAT
 uparamcoord %(curve_count)i 1 FLOAT
  %(uparamcoord)s
 declare vparamcoord uniform FLOAT
 vparamcoord %(curve_count)i 1 FLOAT
  %(vparamcoord)s
 declare curve_id uniform UINT
 curve_id %(curve_count)i 1 UINT
  %(curve_ids)s"""

    curve_count = geo.intrinsicValue('primitivecount')
    real_point_count = geo.intrinsicValue('pointcount')

    # Export the root point three times
    # And the tip point twice
    # so we will have 3 extra points per curve
    point_count = real_point_count + curve_count * 2

    # write down the radius for the tip twice
    radius_count = real_point_count

    number_of_points_per_curve = []
    point_positions = []
    curve_ids = range(curve_count)
    radius = []
    uparamcoord = []
    vparamcoord = []
    for prim in geo.prims():
        curve = prim
        numVertices = curve.numVertices() + 2
        number_of_points_per_curve.append(numVertices)

        uv = prim.attribValue('uv')
        uparamcoord.append(uv[0])
        vparamcoord.append(uv[1])

        temp_point_positions = []
        for vertex in prim.vertices():
            point = vertex.point()
            temp_point_positions.extend(point.position())
            radius.append(vertex.attribValue('width'))

        # insert the root two more times
        first_point_position = temp_point_positions[0:3]
        temp_point_positions.insert(0, first_point_position[2])
        temp_point_positions.insert(0, first_point_position[1])
        temp_point_positions.insert(0, first_point_position[0])

        # insert the tip one more time
        temp_point_positions.extend(temp_point_positions[-3:])

        # finally write it down
        point_positions.extend(temp_point_positions)

        # extend the radius with the last radius again
        #radius.append(radius[-1])

    rendered_curve_data = curve_data % {
        'name': 'sero_fur',
        'curve_count': curve_count,
        'number_of_points_per_curve': ' '.join(map(str, number_of_points_per_curve)),
        'point_count': point_count,
        'point_positions': ' '.join(map(str, point_positions)),
        'radius': ' '.join(map(str, radius)),
        'radius_count': radius_count,
        'curve_ids': ' '.join(map(str, curve_ids)),
        'uparamcoord': ' '.join(map(str, uparamcoord)),
        'vparamcoord': ' '.join(map(str, vparamcoord))
    }

    rendered_base_template = base_template % {'curve_data': rendered_curve_data}

    filehandler = open
    if use_gzip:
        filehandler = gzip.open

    ass_file = filehandler(ass_path, 'w')
    ass_file.write(rendered_base_template)
    ass_file.close()

    bounding_box = geo.intrinsicValue('bounds')
    bounding_box_info = 'bounds %s %s %s %s %s %s' % (
        bounding_box[0], bounding_box[2], bounding_box[4],
        bounding_box[1], bounding_box[3], bounding_box[5]
    )

    with open(asstoc_path, 'w') as asstoc_file:
        asstoc_file.write(bounding_box_info)

