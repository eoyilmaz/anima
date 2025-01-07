# -*- coding: utf-8 -*-


try:
    from functools import cache
except ImportError:
    # has the limitation of maxsize=128
    from functools import lru_cache as cache

import os

from stalker import SimpleEntity, Project


def extends(cls):
    """A decorator for extending classes with other class methods or functions.

    Args:
        cls (Type): The class object that will be extended.
    """

    def wrapper(f):
        if isinstance(f, property):
            name = f.fget.__name__
        else:
            name = f.__name__
        if isinstance(cls, type):
            setattr(cls, name, f)
        elif isinstance(cls, list):
            for c in cls:
                setattr(c, name, f)

        def wrapped_f(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapped_f

    return wrapper


def get_generic_text_attr(self, attr):
    """Return the value of the attribute from the generic text.

    Args:
        attr (str): The name of the attribute.

    Returns:
        Any: The corresponding value for the given attr.
    """
    import json

    attr_value = None
    if self.generic_text:
        data = json.loads(self.generic_text)
        attr_value = data.get(attr)
    return attr_value


def set_generic_text_attr(self, attr, value):
    """Set the value of the attribute in the generic text.

    Args:
        attr (str): The name of the attribute.
        value (Any): The value to set to.
    """
    import json

    data = {}
    if self.generic_text:
        data = json.loads(self.generic_text)
    data[attr] = value
    self.generic_text = json.dumps(data)


SimpleEntity.get_generic_text_attr = get_generic_text_attr
SimpleEntity.set_generic_text_attr = set_generic_text_attr



# Patch Stalker.Project
@property
@cache
def is_managed(self) -> bool:
    """Return True if this is a managed project.

    Returns:
        bool: True if this is a managed project, False otherwise.
    """
    project_repo = self.repository
    return not os.path.exists(
        os.path.join(project_repo.path, self.code, "unmanaged_project")
    )


@property
@cache
def cache_format(self) -> str:
    """Return the project cache format.

    By default it is Alembic.

    Returns:
        str: The cache format name.
    """
    from anima import ALEMBIC, USD

    project_repo = self.repository

    if os.path.exists(os.path.join(project_repo.path, self.code, "use_usd")):
        return USD
    else:
        return ALEMBIC


Project.is_managed = is_managed
Project.cache_format = cache_format
