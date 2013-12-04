# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
# 
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import shutil

import os
import gzip
import struct
import time
import re

from anima.render.arnold import base85
reload(base85)

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


def curves2ass(ass_path, hair_name, min_pixel_width=0.5, mode='ribbon'):
    """exports the node content to ass file
    """
    print '*******************************************************************' 
    start_time = time.time()

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
"""

    curve_data = """
 name %(name)s
 num_points %(curve_count)i 1 UINT
  %(number_of_points_per_curve)s
 points %(point_count)s 1 b85POINT
 %(point_positions)s

 radius %(radius_count)s 1 b85FLOAT
 %(radius)s
 basis "catmull-rom"
 mode "%(mode)s"
 min_pixel_width %(min_pixel_width)s
 visibility 65523
 receive_shadows on
 self_shadows on
 matrix
  1 0 0 0
  0 1 0 0
  0 0 1 0
  0 0 0 1
 opaque on
 sss_sample_spacing 0.100000001
 sss_sample_distribution "blue_noise"
 declare uparamcoord uniform FLOAT
 uparamcoord %(curve_count)i 1 b85FLOAT
 %(uparamcoord)s
 declare vparamcoord uniform FLOAT
 vparamcoord %(curve_count)i 1 b85FLOAT
 %(vparamcoord)s
 declare curve_id uniform UINT
 curve_id %(curve_count)i 1 UINT
  %(curve_ids)s"""

    number_of_curves = geo.intrinsicValue('primitivecount')
    real_point_count = geo.intrinsicValue('pointcount')

    # The root and tip points are going to be used twice for the start and end tangents
    # so there will be 2 extra points per curve
    point_count = real_point_count + number_of_curves * 2

    # write down the radius for the tip twice
    radius_count = real_point_count

    real_number_of_points_in_one_curve = real_point_count / number_of_curves
    number_of_points_in_one_curve = real_number_of_points_in_one_curve + 2
    number_of_points_per_curve = [`number_of_points_in_one_curve`] * number_of_curves

    curve_ids = ' '.join(`id` for id in xrange(number_of_curves))

    radius = None

    pack = struct.pack
    
    # try to find the width as a point attribute to speed things up
    getting_radius_start = time.time()
    radius_attribute = geo.findPointAttrib('width')
    if radius_attribute:
        # this one works 100 times faster then iterating over each vertex
        radius = geo.pointFloatAttribValuesAsString('width')
    else:
        # no radius in points, so iterate over each vertex
        radius_i = 0
        radius_str_buffer = []
        radius_file_str = StringIO()
        radius_file_str_write = radius_file_str.write
        radius_str_buffer_append = radius_str_buffer.append
        for prim in geo.prims():
            prim_vertices = prim.vertices()

            # radius
            radius_i += real_number_of_points_in_one_curve
            if radius_i >= 1000:
                radius_file_str_write(''.join(radius_str_buffer))
                radius_str_buffer = []
                radius_str_buffer_append = radius_str_buffer.append
                radius_i = 0
    
            for vertex in prim_vertices:
                # TODO: copy vertex attributes to point attributes and get it directly
                radius_str_buffer_append(pack('f', vertex.attribValue('width')))

        # do flushes again before getting the values
        radius_file_str_write(''.join(radius_str_buffer))
        radius = radius_file_str.getvalue()
    getting_radius_end = time.time()
    print 'Getting Radius Info        : %3.3f' % (getting_radius_end - getting_radius_start)

    # point positions
    encode_start = time.time()
    point_positions = geo.pointFloatAttribValuesAsString('P')
    # repeat every first and last point coordinates
    # (3 value each 3 * 4 = 12 characters) of every curve
    zip_start = time.time()
    point_positions = ''.join(
        map(lambda x: '%s%s%s' % (x[:12], x, x[-12:]),
            map(''.join,
                zip(*[iter(point_positions)]*(real_number_of_points_in_one_curve*4*3))
            )
        )
    )
    zip_end = time.time()
    print 'Zipping Point Position     : %3.3f' % (zip_end - zip_start)

    encoded_point_positions = base85.arnold_b85_encode(point_positions)
    encode_end = time.time()
    print 'Encoding Point Position    : %3.3f' % (encode_end - encode_start)

    split_start = time.time()
    splitted_point_positions = re.sub("(.{500})", "\\1\n", encoded_point_positions, 0)
    split_end = time.time()
    print 'Splitting Point Poisitions : %3.3f' % (split_end - split_start)

    # radius
    encode_start = time.time()
    encoded_radius = base85.arnold_b85_encode(radius)
    encode_end = time.time()
    print 'Radius encode              : %3.3f' % (encode_end - encode_start)

    split_start = time.time()
    splitted_radius = re.sub("(.{500})", "\\1\n", encoded_radius, 0)
    split_end = time.time()
    print 'Splitting Radius           : %3.3f' % (split_end - split_start)

    # uv
    uv = geo.primFloatAttribValuesAsString('uv')
    # TODO: find a better way of doing the following two lines
    u = ''.join(map(''.join, zip(*[iter(uv)] * 4))[::3])
    v = ''.join(map(''.join, zip(*[iter(uv)] * 4))[1::3])

    encode_start = time.time()
    encoded_u = base85.arnold_b85_encode(u)
    encode_end = time.time()
    print 'Encoding UParamcoord       : %3.3f' % (encode_end - encode_start)

    split_start = time.time()
    splitted_u = re.sub("(.{500})", "\\1\n", encoded_u, 0)
    split_end = time.time()
    print 'Splitting UParamCoord      : %3.3f' % (split_end - split_start)

    encode_start = time.time()
    encoded_v = base85.arnold_b85_encode(v)
    encode_end = time.time()
    print 'Encoding VParamcoord       : %3.3f' % (encode_end - encode_start)

    split_start = time.time()
    splitted_v = re.sub("(.{500})", "\\1\n", encoded_v, 0)
    split_end = time.time()
    print 'Splitting VParamCoord      : %3.3f' % (split_end - split_start)

    print 'len(encoded_point_positions) : %s' % len(encoded_point_positions)
    print '(p + 2 * c) * 5 * 3          : %s' % (point_count * 5 * 3)
    print 'len(encoded_radius)          : %s' % len(encoded_radius)
    print 'len(uv)                      : %s' % len(uv)
    print 'len(encoded_u)               : %s' % len(encoded_u)
    print 'len(encoded_v)               : %s' % len(encoded_v)

    rendered_curve_data = curve_data % {
        'name': node.path().replace('/', '_'),
        'curve_count': number_of_curves,
        'number_of_points_per_curve': ' '.join(number_of_points_per_curve),
        'point_count': point_count,
        'point_positions': splitted_point_positions,
        'radius': splitted_radius,
        'radius_count': radius_count,
        'curve_ids': curve_ids,
        'uparamcoord': splitted_u,
        'vparamcoord': splitted_v,
        'min_pixel_width': min_pixel_width,
        'mode': mode
    }

    rendered_base_template = base_template % {
        'curve_data': rendered_curve_data
    }

    write_start = time.time()
    filehandler = open
    if use_gzip:
        filehandler = gzip.open

    try:
        os.makedirs(os.path.dirname(ass_path))
    except OSError:  # path exists
        pass

    ass_file = filehandler(ass_path, 'w')
    ass_file.write(rendered_base_template)
    ass_file.close()
    write_end = time.time()

    print 'Writing to file            : %3.3f' % (write_end - write_start)

    bounding_box = geo.intrinsicValue('bounds')
    bounding_box_info = 'bounds %s %s %s %s %s %s' % (
        bounding_box[0], bounding_box[2], bounding_box[4],
        bounding_box[1], bounding_box[3], bounding_box[5]
    )

    with open(asstoc_path, 'w') as asstoc_file:
        asstoc_file.write(bounding_box_info)

    end_time = time.time()
    print 'All Conversion took       : %3.3f sec' % (end_time - start_time)
    print '*******************************************************************' 
