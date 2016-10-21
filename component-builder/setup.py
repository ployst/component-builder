#!/usr/bin/env python
# # coding: utf-8
import os.path
import sys
from setuptools import find_packages, setup
USAGE = """
Component Builder setup.py:
  Relies on a VERSION.txt being present in the root of the library.

  Upload
  ------

  Easiest way to run this is via make:

    VERSION=1.0 make build release

  It will create the VERSION.txt file and then run `sdist upload`.

  Local Building
  --------------

  Create a VERSION.txt file in the root.

"""

if not os.path.exists('VERSION.txt'):
    print(USAGE)
    print(sys.argv)
    sys.exit(1)

version = open('VERSION.txt', 'r').read().strip()

setup(
    name='component_builder',
    description='Build runner of components for testing/releasing purposes.',
    version=version,
    install_requires=[
        'bash>=0.5',
        'docopt',
        'github3.py>=1.0.0a3',
        'pytz>=2015.4'
    ],
    scripts=[
        'scripts/tag-push'
    ],
    entry_points=dict(
        console_scripts=[
            'compbuild = component_builder.__main__:cli'
        ],
    ),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        ('License :: OSI Approved :: GNU Library or Lesser '
         'General Public License (LGPL)'),
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
