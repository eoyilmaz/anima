# -*- coding: utf-8 -*-


class RepresentationManager(object):
    """Manages Task/Version :class:`.Representation`\ s.

    RepresentationManager manages all these different representations as one
    and supplies easy switching or on load switching for different
    representations.
    """

    pass


class Representation(object):
    """A single representation of a Version.

    A representation is basically a Version instance, what does matter is the
    content of this version instance, it can be a hires polygonal model, a
    delayed load archive or arnold scene source file or a geometry with only
    one bounding box.

    In Anima Pipeline, different representations are managed through the
    Version.variant_name attribute. So if the base take name for a given Version
    is **Main** then **Main_BBox** or **Main_ASS** or **Main_GPU** is
    considered as the other representations.

    This is done in that way to allow easy creations of different
    representations, that is without using any special script or attribute and
    it is flexible enough.
    """

    base_repr_name = "Base"
    repr_separator = "@"

    def __init__(self, version=None):
        self._version = None
        self.version = version

    def _validate_version(self, version):
        """Validates the given version value

        :param version: :class:`.Version`
        :return: :class:`.Version`
        """
        if version is not None:
            from stalker import Version

            if not isinstance(version, Version):
                raise TypeError(
                    "%(class)s.version should be a "
                    "stalker.models.version.Version instance, not "
                    "%(version_class)s"
                    % {
                        "class": self.__class__.__name__,
                        "version_class": version.__class__.__name__,
                    }
                )
        return version

    @property
    def version(self):
        """getter for the _version attribute

        :return:
        """
        return self._version

    @version.setter
    def version(self, version):
        """getter for the _version attribute

        :return:
        """
        self._version = self._validate_version(version)

    def has_any_repr(self):
        """Returns true or false depending if the version has any
        representation or not

        :returns: bool
        """
        return len(self.list_all()) > 1

    def has_repr(self, repr_name):
        """Returns True or False depending on that this reference has a
        Representation with the given name

        :param str repr_name: The desired representation name
        :return:
        """
        return self.find(repr_name) is not None

    def is_repr(self, repr_name=""):
        """Returns a bool value depending if the version is the requested
        representation in its representation series.

        :param str repr_name: Representation name
        :return:
        """
        base_variant_name = self.get_base_variant_name(self.version)

        if repr_name != self.base_repr_name and repr_name != base_variant_name:
            resolved_repr_name = "{}{}{}".format(
                base_variant_name,
                self.repr_separator,
                repr_name,
            )
        else:
            resolved_repr_name = base_variant_name

        return self.version.variant_name == resolved_repr_name

    def is_base(self):
        """Returns a bool value depending if the version is the base of its
        representations series.

        :return: bool
        """
        base_variant_name = self.get_base_variant_name(self.version)
        return self.version.variant_name == base_variant_name

    @classmethod
    def get_base_variant_name(cls, version):
        """Returns the base variant_name for the related version
        :return: str
        """
        # find the base repr name from the current version
        variant_name = ""
        from stalker import Version

        if isinstance(version, Version):
            variant_name = version.variant_name
        elif isinstance(version, str):
            variant_name = version

        if cls.repr_separator in variant_name:
            # it is a repr
            base_repr_variant_name = variant_name.split(cls.repr_separator)[0]
        else:
            # it is the base repr
            base_repr_variant_name = variant_name

        return base_repr_variant_name

    def list_all(self):
        """lists other representations"""
        base_variant_name = self.get_base_variant_name(self.version)

        # find any version that starts with the base_repr_name
        # under the same task
        from anima.utils import get_unique_variant_names

        variant_names = get_unique_variant_names(self.version.task.id, include_reprs=True)
        variant_names.sort()

        repr_names = []
        for variant_name in variant_names:
            if variant_name.startswith(base_variant_name):
                if variant_name != base_variant_name:
                    repr_names.append(
                        variant_name[len(base_variant_name) + len(self.repr_separator) :]
                    )
                else:
                    repr_names.append(self.base_repr_name)
        return repr_names

    def find(self, repr_name=""):
        """returns the Version instance with the given representation name.

        :param repr_name: The take name of the desires representation.
        :return: :class:`.Version`
        """
        base_variant_name = self.get_base_variant_name(self.version)
        if repr_name == self.base_repr_name:
            variant_name = base_variant_name
        else:
            variant_name = "{}{}{}".format(base_variant_name, self.repr_separator, repr_name)

        from stalker import Version

        return (
            Version.query.filter_by(task=self.version.task)
            .filter_by(variant_name=variant_name)
            .filter_by(is_published=True)
            .order_by(Version.version_number.desc())
            .first()
        )

    @property
    def repr(self):
        """returns the current representation name"""
        if not self.version:
            return None

        variant_name = self.version.variant_name
        if self.repr_separator in variant_name:
            # it is a repr
            repr_name = variant_name.split(self.repr_separator)[1]
        else:
            # it is the base repr
            repr_name = self.base_repr_name

        return repr_name
