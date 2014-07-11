# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


def empty_reference_resolution(root=None, leave=None, update=None, create=None):
    """Generates an empty reference_resolution dictionary.

    Generates a ``Reference Resolution`` dictionary, where there are keys like
    'root', 'leave', 'update', 'create' showing:

    root: the versions referenced directly to the root,
    leave: Versions those doesn't have any new versions,
    update: Versions does have an updated version,
    create: Versions that should be updated by creating a new published version
      because its references has updated versions.

    :return: dict
    """
    return {
        'root': [] if root is None else root,
        'leave': [] if leave is None else leave,
        'update': [] if update is None else update,
        'create': [] if create is None else create
    }


def create_repo_vars():
    """creates environment variables for all of the repositories in the current
    database
    """
    # get all the repositories
    import os
    from stalker import Repository
    from anima import repo_env_template
    all_repos = Repository.query.all()
    for repo in all_repos:
        os.environ[repo_env_template % {'id': repo.id}] = repo.path


def to_os_independent_path(path):
    """Replaces the part of the given path with repository environment
    variable which makes the given path OS independent.

    :param path: path to make OS independent
    :return:
    """
    # find the related repo
    from anima.env.base import EnvironmentBase
    from anima import repo_env_template

    repo = EnvironmentBase.find_repo(path)

    if repo:
        return '$%(repo_env_var)s/%(relative_path)s' % {
            'repo_env_var': repo_env_template % {'id': repo.id},
            'relative_path': repo.make_relative(path)
        }
    else:
        return path
