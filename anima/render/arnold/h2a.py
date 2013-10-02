# This code is called when instances of this SOP cook.
import os
import gzip
try:
    import hou
except ImportError:
    hou = None
from cStringIO import StringIO


class Buffer(object):
    """Buffer class for efficient string concatenation.
    
    This class uses cStringIO for the general store and a string buffer as an
    intermediate storage, then concatenates every 1000 element in to the
    cStringIO file handler.
    """

    def __init__(self, str_buffer_size=1000):
        self.i = 0
        self.str_buffer = []
        self.file_str = StringIO()
        self.file_str_write = self.file_str.write
        self.str_buffer_append = self.str_buffer.append
        self.str_buffer_size = str_buffer_size

    def flush(self):
        """flushes the data to the StringIO buffer and resets the counter
        """
        self.file_str_write(' '.join(self.str_buffer))
        self.str_buffer = []
        self.i = 0

    def append(self, data):
        """appends the data to the str_buffer if the limit is reached then the
        data in the buffer is flushed to the cStringIO
        """
        self_i = self.i
        self_i += 1
        if self_i == self.str_buffer_size:
            self.flush()
        self.str_buffer_append(`data`)

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

    # The root and tip points are going to be used twice for the start and end tangents
    # so there will be 2 extra points per curve
    point_count = real_point_count + curve_count * 2

    # write down the radius for the tip twice
    radius_count = real_point_count

    #number_of_points_per_curve = Buffer()
    #number_of_points_per_curve = []
    number_of_points_per_curve_i = 0
    number_of_points_per_curve_str_buffer = []
    number_of_points_per_curve_file_str = StringIO()
    number_of_points_per_curve_file_str_write = number_of_points_per_curve_file_str.write
    number_of_points_per_curve_str_buffer_append = number_of_points_per_curve_str_buffer.append

    #point_positions = Buffer()
    #point_positions = []
    point_positions_i = 0
    point_positions_str_buffer = []
    point_positions_file_str = StringIO()
    point_positions_file_str_write = point_positions_file_str.write
    point_positions_str_buffer_append = point_positions_str_buffer.append

    curve_ids = ' '.join(`id` for id in xrange(curve_count))

    #radius = Buffer()
    #radius = []
    radius_i = 0
    radius_str_buffer = []
    radius_file_str = StringIO()
    radius_file_str_write = radius_file_str.write
    radius_str_buffer_append = radius_str_buffer.append

    #uparamcoord = Buffer()
    #uparamcoord = []
    uparamcoord_i = 0
    uparamcoord_str_buffer = []
    uparamcoord_file_str = StringIO()
    uparamcoord_file_str_write = uparamcoord_file_str.write
    uparamcoord_str_buffer_append = uparamcoord_str_buffer.append

    #vparamcoord = Buffer()
    #vparamcoord = []
    vparamcoord_i = 0
    vparamcoord_str_buffer = []
    vparamcoord_file_str = StringIO()
    vparamcoord_file_str_write = vparamcoord_file_str.write
    vparamcoord_str_buffer_append = vparamcoord_str_buffer.append

    for prim in geo.prims():
        curve = prim
        real_numVertices = curve.numVertices()
        numVertices = real_numVertices + 2

        # number_of_points_per_curve
        number_of_points_per_curve_i += 1
        if number_of_points_per_curve_i >= 1000:
            number_of_points_per_curve_file_str_write(' '.join(number_of_points_per_curve_str_buffer))
            number_of_points_per_curve_file_str_write(' ')
            number_of_points_per_curve_str_buffer = []
            number_of_points_per_curve_str_buffer_append = number_of_points_per_curve_str_buffer.append
            number_of_points_per_curve_i = 0
        number_of_points_per_curve_str_buffer_append(`numVertices`)

        uv = curve.attribValue('uv')

        # uparamcoord
        uparamcoord_i += 1
        if uparamcoord_i >= 1000:
            uparamcoord_file_str_write(' '.join(uparamcoord_str_buffer))
            uparamcoord_file_str_write(' ')
            uparamcoord_str_buffer = []
            uparamcoord_str_buffer_append = uparamcoord_str_buffer.append
            uparamcoord_i = 0
        uparamcoord_str_buffer_append(`uv[0]`)

        vparamcoord_i += 1
        if vparamcoord_i >= 1000:
            vparamcoord_file_str_write(' '.join(vparamcoord_str_buffer))
            vparamcoord_file_str_write(' ')
            vparamcoord_str_buffer = []
            vparamcoord_str_buffer_append = vparamcoord_str_buffer.append
            vparamcoord_i = 0
        vparamcoord_str_buffer_append(`uv[1]`)

        curve_vertices = curve.vertices()
        vertex = curve_vertices[0]
        point_position = vertex.point().position()
        
        # point_positions
        point_positions_i += numVertices
        if point_positions_i >= 1000:
            point_positions_file_str_write(' '.join(point_positions_str_buffer))
            point_positions_file_str_write(' ')
            point_positions_str_buffer = []
            point_positions_str_buffer_append = point_positions_str_buffer.append
            point_positions_i = 0
        point_positions_str_buffer_append(`point_position[0]`)
        point_positions_str_buffer_append(`point_position[1]`)
        point_positions_str_buffer_append(`point_position[2]`)

        # radius
        radius_i += real_numVertices
        if radius_i >= 1000:
            radius_file_str_write(' '.join(radius_str_buffer))
            radius_file_str_write(' ')
            radius_str_buffer = []
            radius_str_buffer_append = radius_str_buffer.append
            radius_i = 0

        for vertex in curve_vertices:
            point_position = vertex.point().position()
            point_positions_str_buffer_append(`point_position[0]`)
            point_positions_str_buffer_append(`point_position[1]`)
            point_positions_str_buffer_append(`point_position[2]`)

            radius_str_buffer_append(`vertex.attribValue('width')`)


        vertex = curve_vertices[-1]
        point_position = vertex.point().position()
        point_positions_str_buffer_append(`point_position[0]`)
        point_positions_str_buffer_append(`point_position[1]`)
        point_positions_str_buffer_append(`point_position[2]`)

    # do flushes again before getting the values
    number_of_points_per_curve_file_str_write(' '.join(number_of_points_per_curve_str_buffer))
    uparamcoord_file_str_write(' '.join(uparamcoord_str_buffer))
    vparamcoord_file_str_write(' '.join(vparamcoord_str_buffer))
    point_positions_file_str_write(' '.join(point_positions_str_buffer))
    radius_file_str_write(' '.join(radius_str_buffer))

    rendered_curve_data = curve_data % {
        'name': 'sero_fur',
        'curve_count': curve_count,
        'number_of_points_per_curve': number_of_points_per_curve_file_str.getvalue(),
        'point_count': point_count,
        'point_positions': point_positions_file_str.getvalue(),
        'radius': radius_file_str.getvalue(),
        'radius_count': radius_count,
        'curve_ids': curve_ids,
        'uparamcoord': uparamcoord_file_str.getvalue(),
        'vparamcoord': vparamcoord_file_str.getvalue()
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

