#!/usr/bin/env python

"""Setup file for testing, not for packaging/distribution."""

import setuptools

setuptools.setup(
    name='blender-id',
    version='1.0',
    packages=setuptools.find_packages('application'),
    package_dir={'': 'blender-id'},  # tell setuptools packages are under 'blender-id'
    tests_require=['pytest'],
    zip_safe=False,
)
