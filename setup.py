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
import pydoc
import sys

from setuptools import (setup, find_packages)

sys.path.insert(0, os.path.dirname(__file__))
import version  # noqa: E402


main_module_name = 'daemon'
main_module_fromlist = ['_metadata']
main_module = __import__(
        main_module_name,
        level=0, fromlist=main_module_fromlist)
metadata = main_module._metadata

(synopsis, long_description) = pydoc.splitdoc(pydoc.getdoc(main_module))


test_requirements = [
        "testtools",
        "testscenarios >=0.4",
        "coverage",
        "docutils",
        ]

devel_requirements = [
        "twine",
        ] + test_requirements


setup_kwargs = dict(
        distclass=version.ChangelogAwareDistribution,
        name=metadata.distribution_name,
        packages=find_packages(exclude=["test"]),
        cmdclass={
            "write_version_info": version.WriteVersionInfoCommand,
            "egg_info": version.EggInfoCommand,
            "build": version.BuildCommand,
            },

        # Setuptools metadata.
        zip_safe=False,
        setup_requires=[
            "docutils",
            ],
        install_requires=[
            "setuptools",
            "lockfile >=0.10",
            ],
        python_requires=">=3.7",
        extras_require={
            'test': test_requirements,
            'devel': devel_requirements,
            },

        # PyPI metadata.
        author=metadata.author_name,
        author_email=metadata.author_email,
        description=synopsis,
        license=metadata.license,
        keywords="daemon fork unix".split(),
        url=metadata.url,
        long_description=long_description,
        long_description_content_type="text/x-rst",
        classifiers=[
            # Reference: <URL:https://pypi.org/classifiers/>
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 3",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries :: Python Modules",
            ],
        )

# Docutils is only required for building, but Setuptools can't distinguish
# dependencies properly.
# See <URL:https://github.com/pypa/setuptools/issues/457>.
setup_kwargs['install_requires'].append("docutils")


if __name__ == '__main__':
    setup(**setup_kwargs)


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
