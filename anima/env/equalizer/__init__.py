# -*- coding: utf-8 -*-

from anima.env.base import EnvironmentBase


class Equalizer(EnvironmentBase):

    name = '3DEqualizer4'

    def save_as(self, version, run_pre_publishers=True):
        """runs when saving a document

        :param version:
        :param run_pre_publishers:
        :return:
        """

        import tde4

        tde4.setProjectPath(version.absolute_full_path)
        tde4.saveProject(version.absolute_full_path)

    def open(self, version, force=False, representation=None,
             reference_depth=0, skip_update_check=False):
        """

        :param version:
        :param force:
        :param representation:
        :param reference_depth:
        :param skip_update_check:
        :return:
        """
        import tde4

        from stalker import Version
        assert isinstance(version, Version)
        td4.loadProject(version.absolute_full_path)


class TDE4Lens(object):
    """Holds information about the 3DE4 lens
    """

    def __init__(self):
        self.lens_name = None
        self.horizontal_aperture = None
        self.vertical_aperture = None
        self.focal_length = None
        self.film_aspect = None
        self.lens_center_offset_x = None
        self.lens_center_offset_y = None
        self.pixel_aspect = None
        self.dynamic_lens_distortion = None
        self.distortion_model = None
        self.distortion_degree_2 = None
        self.u_degree_2 = None
        self.v_degree_2 = None
        self.distortion_degree_4 = None  # Quartic distortion
        self.u_degree_4 = None
        self.v_degree_4 = None
        self.phi = None
        self.beta = None

    def load(self, lens_file_path):
        """Loads the lens info and returns a dictionary

        :param str lens_file_path: Path to the saved lens txt file.
        :return:
        """
        output_data = {}
        with open(lens_file_path) as f:
            data = f.read().split('\n')

        self.lens_name = data[0]

        sensor_info = data[1].split(' ')
        self.horizontal_aperture = float(sensor_info[0]) * 10
        self.vertical_aperture = float(sensor_info[1]) * 10
        self.focal_length = float(sensor_info[2]) * 10
        self.film_aspect = float(sensor_info[3])
        self.lens_center_offset_x = float(sensor_info[4])
        self.lens_center_offset_y = float(sensor_info[5])
        self.pixel_aspect = float(sensor_info[6])

        self.dynamic_lens_distortion = data[2]
        self.distortion_model = data[3]

        def get_data(label):
            max_search_length = 60
            start_i = 0
            while data[start_i] != label and start_i < max_search_length:
                start_i += 1
            start_i += 1
            return data[start_i]

        # Distortion - Degree 2
        self.distortion_degree_2 = float(get_data('Distortion - Degree 2'))
        self.u_degree_2 = float(get_data('U - Degree 2'))
        self.v_degree_2 = float(get_data('V - Degree 2'))
        self.distortion_degree_4 = float(get_data('Quartic Distortion - Degree 4'))
        self.u_degree_4 = float(get_data('U - Degree 4'))
        self.v_degree_4 = float(get_data('V - Degree 4'))
        self.phi = float(get_data('Phi - Cylindric Direction'))
        self.beta = float(get_data('B - Cylindric Bending'))
