# -*- coding: utf-8 -*-
"""Setup mech"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os

from mech import __version__


def read(fname):
    """Read in a file."""
    try:
        with open(os.path.join(os.path.dirname(__file__), fname), "r") as a_file:
            return a_file.read().strip()
    except IOError:
        return ''


setup(
    name="pymech",
    version=__version__,
    author="Kevin Chung, Germán Méndez Bravo, Mike Kinney",
    author_email="kchung@nyu.edu, german.mb@gmail.com, mike.kinney@gmail.com",
    # url="https://github.com/mkinney/mech",
    url="https://github.com/whoopsjohnnie/mech",
    # download_url="https://github.com/mkinney/mech/tarball/master",
    download_url="https://github.com/whoopsjohnnie/mech/tarball/master",
    license="MIT",
    description="Tool for command line virtual machines",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    keywords=['vagrant', 'vmware', 'vmrun', 'tool', 'virtualization'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Emulators",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=['requests', 'click', 'colorama', 'pyinfra', 'pypsrp'],
    python_requires='>=3.7',
    packages=['mech'],
    entry_points={
        'console_scripts': [
            'mech = mech.mech_cli:cli',
        ]
    },
)
