# -*- coding: utf-8 -*-

from typing import List, Union

from stalker import Link, Type, Version
from stalker.db.session import DBSession

from anima.extension import extends


REPR_TYPE_NAME = "Representation"
BASE_REPR_NAME = "Base"


def get_repr_type() -> Union[None, Type]:
    """Return the representation Type instance.

    Returns:
        Union[None, Type]: Retrieve and return the representation Type
            instance, None if it doesn't exist at all.
    """
    with DBSession.no_autoflush:
        repr_type = (
            Type.query.filter(Type.name == REPR_TYPE_NAME)
            .filter(Type.target_entity_type == "Link")
            .first()
        )
    return repr_type


class RepresentationManager(object):
    """Manages Task/Version :class:`.Representation` instances.

    RepresentationManager manages all these different representations as one
    and supplies easy switching or on load switching for different
    representations.
    """

    pass


class Representation(object):
    """A single representation related to a Version.

    A representation is basically a Link instance, created as an output to a
    Version. The content of the file that the Link is representing can be a
    Maya scene that contains a hires polygonal model (LOD500, LOD300, LOD100
    etc), a delayed load archive suitable for the render engine(i.e Arnold
    Scene Source (*.ass) or a Redshift Proxy (*.rs) file) or a geometry with
    only one bounding box.

    In Anima Pipeline, different representations are managed through Link
    instances stored in `Version.outputs` list. Each `Link` that is a
    representation has a `Type.name=="Representation"` and the `Link.name`
    attribute stores the name of the representation. So, by looking at the
    outputs of a `Version` instance through the `Version.outputs` list, the
    `Link` instances with
    `Link.type==(Type(name=="Representation", target_entity_type=="Link")` is
    considered as a representation of the related `Version` instance.

    Args:
        link: The related Link instance.
    """

    base_repr_name = "Base"
    repr_separator = "@"

    def __init__(self, version=None):
        self._version = None
        self.version = version

    def _validate_version(self, version) -> Version:
        """Validate the given version.

        Args:
            version (:class:`.Version`): The version instance to be validated.

        Returns:
            :class:`.Version`: The validated Version instance.
        """
        if version is None:
            return

        if not isinstance(version, Version):
            raise TypeError(
                f"{self.__class__.__name__}.version should be a "
                "stalker.models.version.Version instance, "
                f"not {version.__class__.__name__}: '{version}'"
            )

        return version

    @property
    def version(self) -> Version:
        """Return the _version attribute value.

        Returns:
            Version:
        """
        return self._version

    @version.setter
    def version(self, version):
        """Set the _version attribute value."""
        self._version = self._validate_version(version)

    def has_any_repr(self):
        """Return True if the version has any representation or not.

        Returns:
            bool: True if the Version has any representation other than the
                base repr.
        """
        return len(self.list_all()) > 1

    def has_repr(self, repr_name):
        """Return True if the related version has a repr with the given name.

        Args:
            repr_name (str): The desired representation name.

        Returns:
            bool: True if there is a repr with the given name.
        """
        return self.find(repr_name) is not None

    def is_repr(self, repr_name=""):
        """Return a True if the version is the requested repr in its repr series.

        Args:
            repr_name (str): Representation name.

        Returns:
            bool:
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
        """Return True if the version is the base of its representations series.

        Returns:
            bool: If the Version is the base representation.
        """
        base_variant_name = self.get_base_variant_name(self.version)
        return self.version.variant_name == base_variant_name

    @classmethod
    def get_base_variant_name(cls, version):
        """Return the base variant_name for the related version.

        Returns:
            str:
        """
        # find the base repr name from the current version
        variant_name = ""

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

    def list_all(self) -> List[str]:
        """Return all representation names.

        Returns:
            List[str]: All the representation names.
        """
        base_variant_name = self.get_base_variant_name(self.version)

        # find any version that starts with the base_repr_name
        # under the same task
        from anima.utils import get_unique_variant_names

        variant_names = get_unique_variant_names(
            self.version.task.id, include_reprs=True
        )
        variant_names.sort()

        repr_names = []
        for variant_name in variant_names:
            if variant_name.startswith(base_variant_name):
                if variant_name != base_variant_name:
                    repr_names.append(
                        variant_name[
                            len(base_variant_name) + len(self.repr_separator) :
                        ]
                    )
                else:
                    repr_names.append(self.base_repr_name)
        return repr_names

    def find(self, repr_name=""):
        """Return the Version instance with the given representation name.

        Args:
            repr_name (str) : The variant name of the desires representation.

        Returns:
            :class:`.Version`: The related version.
        """
        base_variant_name = self.get_base_variant_name(self.version)
        if repr_name == self.base_repr_name:
            variant_name = base_variant_name
        else:
            variant_name = "{}{}{}".format(
                base_variant_name, self.repr_separator, repr_name
            )

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


#
# Version extensions
#


@extends(Version)
def get_representation_names(self) -> List[str]:
    """Return the available representation names."""
    with DBSession.no_autoflush:
        repr_type = (
            Type.query.filter(Type.name == REPR_TYPE_NAME)
            .filter(Type.target_entity_type == "Link")
            .first()
        )
    repr_names = []
    if repr_type is None:
        return repr_names

    for link in self.outputs:
        if link.type == repr_type:
            repr_names.append(link.name)

    return list(set(repr_names))


@extends(Version)
def get_representation(self, repr_name: str) -> Union[None, Link]:
    """Return the representation with the given name.

    Args:
        repr_name (str): The representation name in query.

    Returns:
        Union[None, Link]: The representation if available, None otherwise.
    """
    # validate repr_name arg
    if not isinstance(repr_name, str):
        raise TypeError(
            "repr_name should be a str, "
            f"not {repr_name.__class__.__name__}: '{repr_name}'"
        )

    with DBSession.no_autoflush:
        repr_type = (
            Type.query.filter(Type.name == REPR_TYPE_NAME)
            .filter(Type.target_entity_type == "Link")
            .first()
        )
    if repr_type is None:
        return

    for link in self.outputs:
        if link.type == repr_type and link.name == repr_name:
            return link
    return


@extends(Version)
def get_base_representation(self) -> Union[None, Link]:
    """Return the base representation.

    Returns:
        Union[None, Link]:
    """
    return self.get_representation(BASE_REPR_NAME)


@extends(Version)
def has_representations(self) -> bool:
    """Return True if this Version has representations other than the base.

    Returns:
        bool: True if this Version has representations other than the base.
    """
    with DBSession.no_autoflush:
        repr_type = (
            Type.query.filter(Type.name == REPR_TYPE_NAME)
            .filter(Type.target_entity_type == "Link")
            .first()
        )
    if repr_type is None:
        return False

    print(f"self.outputs: {self.outputs}")

    for link in self.outputs:
        if link.type == repr_type and link.name != BASE_REPR_NAME:
            return True
    return False


@extends(Version)
def has_representation(self, repr_name: str) -> bool:
    """Return True if a representation with the given name exists.

    Args:
    """
    # validate repr_name arg
    if not isinstance(repr_name, str):
        raise TypeError(
            "repr_name should be a str, "
            f"not {repr_name.__class__.__name__}: '{repr_name}'"
        )
    return self.get_representation(repr_name) is not None


@extends(Version)
def create_representation(self, repr_name: str) -> Link:
    """Create and return a representation with the given name.

    Args:
        repr_name (str): The representation name.

    Returns:
        Link: The newly created representation.
    """
    # validate repr_name
    if not isinstance(repr_name, str):
        raise TypeError(
            "repr_name should be a str, "
            f"not {repr_name.__class__.__name__}: '{repr_name}'"
        )

    # check if representation already exists
    if self.has_representation(repr_name):
        raise ValueError(f"'{repr_name}' representation already exists in this Version")

    with DBSession.no_autoflush:
        repr_type = (
            Type.query.filter(Type.name == REPR_TYPE_NAME)
            .filter(Type.target_entity_type == "Link")
            .first()
        )
    if repr_type is None:
        return

    repr = Link(name=repr_name, type=repr_type)
    DBSession.save(repr)
    self.outputs.append(repr)
    DBSession.commit()

    return repr


#
# Link extensions
#


@extends(Link)
def is_representation(self) -> bool:
    """Return True if this is a representation.

    Returns:
        bool: True if this is a representation.
    """
    # check if we are a representation at all
    with DBSession.no_autoflush:
        repr_type = (
            Type.query.filter(Type.name == REPR_TYPE_NAME)
            .filter(Type.target_entity_type == "Link")
            .first()
        )
    if repr_type is None:
        return False
    return self.type is not None and self.type == repr_type


@extends(Link)
def is_base_representation(self) -> bool:
    """Return True if this is the base representation.

    Returns:
        bool: True if this is the base representation.
    """
    return self.name == BASE_REPR_NAME and self.is_representation()
