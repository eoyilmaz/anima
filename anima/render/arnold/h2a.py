# This code is called when instances of this SOP cook.
import os
import gzip
import hou
from cStringIO import StringIO


class Buffer(object):
    """Buffer class for efficient string concatenation.
    
    This class uses cStringIO for the general store and a string buffer as an
    intermediate storage, then concatenates every 1000 element in to the
    cStringIO file handler.
    """

    def __init__(self, str_buffer_size=1000):
        self.file_str = StringIO()
        self.str_buffer = []
        self.str_buffer_size = str_buffer_size
        self.i = 0
        self.file_str_write = self.file_str.write
        self.str_buffer_append = self.str_buffer.append

    def append(self, data):
        """appends the data to the str_buffer if the limit is reached then the
        data in the buffer is flushed to the cStringIO
        """
        if self.i == self.str_buffer_size:
            # do a flush
            self.flush()
        self.str_buffer.append(`data`)
        self.i += 1

    def flush(self):
        self.file_str_write(' '.join(self.str_buffer))
        self.str_buffer = []
        self.i = 0

    def getvalue(self):
        """returns the string data
        """
        # do a last flush
        self.flush()
        return self.file_str.getvalue()


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

    #number_of_points_per_curve = []
    number_of_points_per_curve = Buffer()
    number_of_points_per_curve_append = number_of_points_per_curve.append
    
    #point_positions = []
    point_positions = Buffer()
    point_positions_append = point_positions.append
    curve_ids = ' '.join(`id` for id in xrange(curve_count))
    #radius = []
    radius = Buffer()
    radius_append = radius.append

    #uparamcoord = []
    #vparamcoord = []
    uparamcoord = Buffer()
    uparamcoord_append = uparamcoord.append
    vparamcoord = Buffer()
    vparamcoord_append = vparamcoord.append

    for prim in geo.prims():
        curve = prim
        numVertices = curve.numVertices() + 2
        number_of_points_per_curve_append(numVertices)

        uv = curve.attribValue('uv')
        uparamcoord_append(uv[0])
        vparamcoord_append(uv[1])

        curve_vertices = curve.vertices()
        vertex = curve_vertices[0]
        point_position = vertex.point().position()
        point_positions_append(point_position[0])
        point_positions_append(point_position[1])
        point_positions_append(point_position[2])
        for vertex in curve.vertices():
            point_position = vertex.point().position()
            point_positions_append(point_position[0])
            point_positions_append(point_position[1])
            point_positions_append(point_position[2])
            radius_append(vertex.attribValue('width'))
        vertex = curve_vertices[-1]
        point_position = vertex.point().position()
        point_positions_append(point_position[0])
        point_positions_append(point_position[1])
        point_positions_append(point_position[2])

    rendered_curve_data = curve_data % {
        'name': 'sero_fur',
        'curve_count': curve_count,
        'number_of_points_per_curve': number_of_points_per_curve.getvalue(),
        'point_count': point_count,
        'point_positions': point_positions.getvalue(),
        'radius': ' '.radius.getvalue(),
        'radius_count': radius_count,
        'curve_ids': curve_ids,
        'uparamcoord': uparamcoord.getvalue(),
        'vparamcoord': vparamcoord.getvalue()
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

