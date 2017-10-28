#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#  Copyright (c) Huoty - All rights reserved
#
#      Author: Huoty <sudohuoty@gmail.com>
#  CreateTime: 2016-11-04 15:07:03
# *************************************************************

from os import path
from codecs import open  # To use a consistent encoding

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils import setup, find_packages


package_name = 'phankom'

here = path.abspath(path.dirname(__file__))


def get_version():
    import ast

    with open(package_name + '/__init__.py', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('__version__'):
                return ast.parse(line).body[0].value.s


def get_long_description():
    try:
        with open(path.join(here, 'README.md'), encoding='utf-8') as f:
            return f.read()
    except IOError:
        return ''

setup(
    name=package_name,
    version=get_version(),
    description='Phankom is a proxy tool',
    long_description=get_long_description(),

    # The project's main homepage.
    url='',

    # Author details
    author='Huoty',
    author_email='sudohuoty@gamil.com',

    # Choose license
    license='GPL v2',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick license as wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        # Specify the Python versions support here. In particular, ensure
        # that project indicate whether project support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does project relate to
    keywords='tool',

    # Can just specify the packages manually here if project is
    # simple. Or can use find_packages().
    packages=find_packages(exclude=['docs', 'tests']),

    # List run-time dependencies here. requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=get_requires(),

    # List additional groups of dependencies here (e.g. development
    # dependencies). Can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['pytest', 'coverage'],
    },

    # If there are data files included in packages that need to be
    # installed, specify them here.
    # package_data = {
    #     # 任何包中含有.txt文件，都包含它
    #     '': ['*.txt'],
    #     # 包含demo包data文件夹中的 *.dat文件
    #     'demo': ['data/*.dat'],
    # }

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)
