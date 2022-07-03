# -*- coding: utf-8 -*-
import os

from anima.dcc.base import DCCBase


class TDE4(DCCBase):

    name = "3DE4"
    extensions = [".3de"]

    def save_as(self, version, run_pre_publishers=True):
        """runs when saving a document

        :param version:
        :param run_pre_publishers:
        :return:
        """
        import tde4

        version.update_paths()

        # set version extension to ma
        version.extension = self.extensions[0]
        version.created_with = self.name
        # create the folder if it doesn't exists
        try:
            os.makedirs(version.absolute_path)
        except OSError:
            # already exists
            pass

        tde4.setProjectPath(version.absolute_full_path)
        tde4.saveProject(version.absolute_full_path)

        from stalker.db.session import DBSession

        DBSession.add(version)
        # append it to the recent file list
        self.append_to_recent_files(version.absolute_full_path)

        DBSession.commit()

    def open(
        self,
        version,
        force=False,
        representation=None,
        reference_depth=0,
        skip_update_check=False,
    ):
        """

        :param version:
        :param force:
        :param representation:
        :param reference_depth:
        :param skip_update_check:
        :return:
        """
        import tde4

        tde4.loadProject(version.absolute_full_path)
        self.append_to_recent_files(version.absolute_full_path)
        from anima.dcc import empty_reference_resolution

        return empty_reference_resolution()

    def get_current_version(self):
        """Return the current version from environment

        :return:
        """
        import tde4

        project_path = tde4.getProjectPath()
        version = self.get_version_from_full_path(project_path)
        return version


class TDE4LensDistortionBase(object):
    """Base class for other Lens Distortion classes."""

    def __init__(self, distortion_model=None):
        self.distortion_model = distortion_model
        self.data = None

    def get_data(self, label):
        max_search_length = 60
        start_i = 0
        while self.data[start_i] != label and start_i < max_search_length:
            start_i += 1
        start_i += 1
        return self.data[start_i]

    @classmethod
    def get_distortion(cls, distortion_model):
        """Generate a proper distortion instance.

        :param str distortion_model: One of the following:

            3DE4 Radial - Standard, Degree 4
            3DE4 Anamorphic - Standard, Degree 4

            The rest of the distortion models will be implemented as they are required.

        :return TDE4LensDistortionBase:
        """
        distortion_class_lut = {
            "3DE4 Radial - Standard, Degree 4": TDE4RadialStandardDegree4,
            "3DE4 Anamorphic - Standard, Degree 4": TDE4AnamorphicStandardDegree4,
        }
        return distortion_class_lut[distortion_model](distortion_model=distortion_model)

    def load(self, data):
        """Load self from the given data.

        :param data: The raw data read from the lens file.
        """
        raise NotImplemented("Implement this on the child class.")


class TDE4RadialStandardDegree4(TDE4LensDistortionBase):
    """Radial - Standard Degree 4 lens distortion model."""

    def __init__(self, distortion_model=None):
        super(TDE4RadialStandardDegree4, self).__init__(
            distortion_model=distortion_model
        )
        self.u_degree_2 = None
        self.v_degree_2 = None
        self.distortion_degree_2 = None
        self.quartic_distortion_degree_4 = None
        self.u_degree_4 = None
        self.v_degree_4 = None
        self.phi = None
        self.beta = None

    def load(self, data):
        """Load self from the given data.

        :param data: The raw data read from the lens file.
        """
        self.data = data
        self.distortion_degree_2 = float(self.get_data("Distortion - Degree 2"))
        self.u_degree_2 = float(self.get_data("U - Degree 2"))
        self.v_degree_2 = float(self.get_data("V - Degree 2"))
        self.quartic_distortion_degree_4 = float(
            self.get_data("Quartic Distortion - Degree 4")
        )
        self.u_degree_4 = float(self.get_data("U - Degree 4"))
        self.v_degree_4 = float(self.get_data("V - Degree 4"))
        self.phi = float(self.get_data("Phi - Cylindric Direction"))
        self.beta = float(self.get_data("B - Cylindric Bending"))


class TDE4AnamorphicStandardDegree4(TDE4LensDistortionBase):
    """Anamorphic - Standard, Degree 4 lens distortion model."""

    def __init__(self, distortion_model=None):
        super(TDE4AnamorphicStandardDegree4, self).__init__(
            distortion_model=distortion_model
        )
        self.cx02_degree_2 = None
        self.cy02_degree_2 = None
        self.cx22_degree_2 = None
        self.cy22_degree_2 = None
        self.cx04_degree_4 = None
        self.cy04_degree_4 = None
        self.cx24_degree_4 = None
        self.cy24_degree_4 = None
        self.cx44_degree_4 = None
        self.cy44_degree_4 = None
        self.lens_rotation = None
        self.squeeze_x = None
        self.squeeze_y = None

    def load(self, data):
        """Load self from the given data.

        :param data: The raw data read from the lens file.
        """
        self.data = data
        self.cx02_degree_2 = float(self.get_data("Cx02 - Degree 2"))
        self.cy02_degree_2 = float(self.get_data("Cy02 - Degree 2"))
        self.cx22_degree_2 = float(self.get_data("Cx22 - Degree 2"))
        self.cy22_degree_2 = float(self.get_data("Cy22 - Degree 2"))
        self.cx04_degree_4 = float(self.get_data("Cx04 - Degree 4"))
        self.cy04_degree_4 = float(self.get_data("Cy04 - Degree 4"))
        self.cx24_degree_4 = float(self.get_data("Cx24 - Degree 4"))
        self.cy24_degree_4 = float(self.get_data("Cy24 - Degree 4"))
        self.cx44_degree_4 = float(self.get_data("Cx44 - Degree 4"))
        self.cy44_degree_4 = float(self.get_data("Cy44 - Degree 4"))
        self.lens_rotation = float(self.get_data("Lens Rotation"))
        self.squeeze_x = float(self.get_data("Squeeze-X"))
        self.squeeze_y = float(self.get_data("Squeeze-Y"))


class TDE4Lens(object):
    """Holds information about the 3DE4 lens"""

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
        self.distortion = None

    def load(self, lens_file_path):
        """Loads the lens info and returns a dictionary

        :param str lens_file_path: Path to the saved lens txt file.
        :return:
        """
        output_data = {}
        with open(lens_file_path) as f:
            data = f.read().split("\n")

        self.lens_name = data[0]

        sensor_info = data[1].split(" ")
        self.horizontal_aperture = float(sensor_info[0]) * 10
        self.vertical_aperture = float(sensor_info[1]) * 10
        self.focal_length = float(sensor_info[2]) * 10
        self.film_aspect = float(sensor_info[3])
        self.lens_center_offset_x = float(sensor_info[4])
        self.lens_center_offset_y = float(sensor_info[5])
        self.pixel_aspect = float(sensor_info[6])

        self.dynamic_lens_distortion = data[2]

        distortion_model = data[3]
        self.distortion = TDE4LensDistortionBase.get_distortion(distortion_model)
        # allow the distortion to load itself
        self.distortion.load(data)


class TDE4Point(object):
    """Represents a 3DEqualizer track point"""

    def __init__(self, name, data):
        self.data = {}
        self.parse_data(data)
        self.name = name

    def parse_data(self, data):
        """Loads data from the given text

        :param data: The data as text which is exported directly from
          3DEqualizer
        :return:
        """
        for i, pos in enumerate(data):
            pos = list(map(float, pos.split(" ")))
            self.data[int(pos[0])] = pos[1:]


class TDE4PointManager(object):
    """Manages 3DEqualizer points"""

    def __init__(self):
        self.points = []

    def read(self, file_path):
        """Read data from file

        :param file_path:
        :return:
        """
        with open(file_path, "r") as f:
            data = f.readlines()
        self.reads(data)

    def reads(self, data):
        """Reads the data from textual input

        :param data: lines of data
        """
        number_of_points = int(data[0])
        cursor = 1
        for i in range(number_of_points):
            # gather individual point data
            point_name = data[cursor]

            # get start
            cursor += 1
            start = int(data[cursor])

            # get end
            cursor += 1
            end = int(data[cursor])

            # find the length
            cursor += 1
            data_start = cursor
            length = 0
            while cursor < len(data) - 1 and " " in data[cursor]:
                cursor += 1
                length += 1

            # length = end - start + 1
            point_data = data[data_start : data_start + length]

            # generate point
            point = TDE4Point(point_name, point_data)

            self.points.append(point)
