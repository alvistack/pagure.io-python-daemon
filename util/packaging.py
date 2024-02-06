# util/packaging.py
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Custom packaging functionality for this project.

    This module provides functionality for Setuptools to dynamically derive
    project metadata at build time.

    Requires:

    * Docutils <https://docutils.sourceforge.io/>
    * JSON <https://docs.python.org/3/reference/json.html>
    """

import os.path

import setuptools
import setuptools.command.build
import setuptools.command.build_py
import setuptools.command.egg_info
import setuptools.dist

from .metadata import (
    docstring_from_object,
    parse_person_field,
    synopsis_and_description_from_docstring,
)
from .version import generate_version_info_from_changelog


def main_module_by_name(
        module_name,
        *,
        fromlist=None,
):
    """ Get the main module of this project, named `module_name`.

        :param module_name: The name of the module to import.
        :param fromlist: The list (of `str`) of names of objects to import in
            the module namespace.
        :return: The Python `module` object representing the main module.
        """
    module = __import__(module_name, level=0, fromlist=fromlist)
    return module


changelog_filename = "ChangeLog"


def get_changelog_path(distribution, filename=changelog_filename):
    """ Get the changelog file path for the distribution.

        :param distribution: The setuptools.dist.Distribution instance.
        :param filename: The base filename of the changelog document.
        :return: Filesystem path of the changelog document, or ``None``
            if not discoverable.
        """
    build_py_command = setuptools.command.build_py.build_py(distribution)
    build_py_command.finalize_options()
    setup_dirname = build_py_command.get_package_dir("")
    filepath = os.path.join(setup_dirname, filename)

    return filepath


def derive_dist_description(
        distribution,
        *,
        content_type="text/x-rst",
):
    """ Derive description fields for `distribution`, from the main module.

        :param distribution: The `setuptools.dist.Distribution` to inspect and
            modify.
        :param content_type: The MIME Content-Type value to describe the
            content of the long description.
        :return: ``None``.

        Read the main module's docstring, and derive values for metadata
        attributes of `distribution`:

        * `description`: The synopsis (one-line) description from the
          docstring.
        * `long_description: The remainder (separated by a blank line after the
          synopsis) of the docstring content.
        * `long_description_content_type`: Set to `content_type` value.
        """
    main_module = main_module_by_name('daemon')
    main_module_docstring = docstring_from_object(main_module)
    (synopsis, long_description) = synopsis_and_description_from_docstring(
        main_module_docstring)
    distribution.metadata.description = synopsis
    distribution.metadata.long_description = long_description
    distribution.metadata.long_description_content_type = content_type


def derive_version(distribution):
    """ Derive a `version` value for `distribution`, from change log document.

        :param distribution: The `setuptools.dist.Distribution` to inspect and
            modify.
        :return: ``None``.
        """
    changelog_path = get_changelog_path(distribution)
    version_info = generate_version_info_from_changelog(changelog_path)
    distribution.metadata.version = version_info['version']


def derive_maintainer(distribution):
    """ Derive maintainer values for `distribution`, from change log document.

        :param distribution: The `setuptools.dist.Distribution` to inspect and
            modify.
        :return: ``None``.
        """
    changelog_path = get_changelog_path(distribution)
    version_info = generate_version_info_from_changelog(changelog_path)
    person = parse_person_field(version_info['maintainer'])
    distribution.metadata.maintainer = person.name
    distribution.metadata.maintainer_email = person.email


# Copyright © 2008–2023 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-3’ for details.


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
