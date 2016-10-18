#!/usr/bin/env python
# # coding: utf-8
from setuptools import find_packages, setup


setup(
    name='component_builder',
    description='Build runner of components for testing/releasing purposes.',
    version='0.1',
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
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
