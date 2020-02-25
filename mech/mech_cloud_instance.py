# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017 Kevin Chung
# Copyright (c) 2018 German Mendez Bravo (Kronuz)
# Copyright (c) 2020 Mike Kinney
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
"""MechCloudInstance class"""

from __future__ import print_function, absolute_import

import sys
import logging

from clint.textui import colored

from . import utils

LOGGER = logging.getLogger(__name__)


class MechCloudInstance():
    """Class to hold Mech Cloud instances."""

    def __init__(self, name, clouds=None):
        """Constructor for the mech cloud instance."""
        if not name or name == "":
            raise AttributeError("Must provide a name for the cloud instance.")
        self.name = name
        self.hostname = None
        self.directory = None

    def read_config(self, name):
        clouds = utils.load_mechcloudfile(False)
        LOGGER.debug("clouds:%s", clouds)

        if clouds.get(name, None):
            self.name = name
        else:
            sys.exit(colored.red("Instance ({}) was not found in the "
                                 "Mechcloudfile".format(name)))

        self.hostname = clouds[name].get('hostname')
        self.directory = clouds[name].get('directory')

    def set_hostname(self, hostname):
        if hostname is None or hostname == '':
            sys.exit(colored.red("A non-blank hostname is required."))
        self.hostname = hostname

    def set_directory(self, directory):
        if directory is None or directory == '':
            sys.exit(colored.red("A non-blank directory is required."))
        self.directory = directory

    def __repr__(self):
        """Return a representation of a Mech Cloud instance."""
        sep = '\n'
        return ('name:{name}{sep}host:{hostname}{sep}directory:{directory}'.
                format(name=self.name, hostname=self.hostname, directory=self.directory,
                       sep=sep))

    def config(self):
        """Return the configuration for this mech clould instance."""
        entry = {}
        entry['name'] = self.name
        entry['hostname'] = self.hostname
        entry['directory'] = self.directory
        return {self.name: entry}

    def init(self):
        """Initialize the cloud instance.
            - add entry to Mechcloudfile
        """
        utils.save_mechcloudfile(self.config())
