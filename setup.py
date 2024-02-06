# setup.py
# Python Setuptools configuration program for this distribution.
# Documentation: <URL:https://packaging.python.org/guides/distributing-packages-using-setuptools/#setup-py>.  # noqa: E501

# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Distribution setup for ‘python-daemon’ library. """

import os.path
import sys

from setuptools import (
    find_packages,
    setup,
)

# This module is not inside a package, so we can't use relative imports. We
# instead add its directory to the import path.
sys.path.insert(0, os.path.dirname(__file__))
import util.packaging  # noqa: E402


main_module = util.packaging.main_module_by_name(
        'daemon', fromlist=['_metadata'])
metadata = main_module._metadata


test_requirements = [
        "testtools",
        "testscenarios >=0.4",
        "coverage",
        "docutils",
        ]

build_requirements = [
        "wheel",
        "build",
        "sphinx",
        ] + test_requirements

dist_requirements = [
        "twine",
        ] + build_requirements

devel_requirements = [
        "isort",
        ] + dist_requirements


setup_kwargs = dict(
        name=metadata.distribution_name,
        version="3.0.2",
        packages=find_packages(exclude=["test", "util"]),
        entry_points={
            "setuptools.finalize_distribution_options": [
                "description_fields = util.packaging:derive_dist_description",
                "maintainer = util.packaging:derive_maintainer",
                ],
            },

        # Setuptools metadata.
        zip_safe=False,
        setup_requires=[
            "docutils",
            "packaging",
            "setuptools",
            ],
        install_requires=[
            "setuptools >=62.4.0",
            "packaging",
            "lockfile >=0.10",
            ],
        python_requires=">=3.7",
        extras_require={
            'test': test_requirements,
            'build': build_requirements,
            'dist': dist_requirements,
            'devel': devel_requirements,
            },

        # PyPI metadata.
        author=metadata.author_name,
        author_email=metadata.author_email,
        license=metadata.license,
        keywords="daemon fork unix".split(),
        classifiers=[
            # Reference: <URL:https://pypi.org/classifiers/>
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 3",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries :: Python Modules",
            ],
        url=metadata.url,
        project_urls={
            'Change Log':
                "https://pagure.io/python-daemon/blob/main/f/ChangeLog",
            'Source': "https://pagure.io/python-daemon/",
            'Issue Tracker': "https://pagure.io/python-daemon/issues",
            },
        )

# Docutils is only required for building, but Setuptools can't distinguish
# dependencies properly.
# See <URL:https://github.com/pypa/setuptools/issues/457>.
setup_kwargs['install_requires'].append("docutils")


if __name__ == '__main__':  # pragma: nocover
    setup(**setup_kwargs)


# Copyright © 2008–2024 Ben Finney <ben+python@benfinney.id.au>
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
