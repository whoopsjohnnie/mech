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
import re
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
        self.username = None
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
        self.username = clouds[name].get('username')

    def set_hostname(self, hostname):
        if hostname is None or hostname == '':
            sys.exit(colored.red("A non-blank hostname is required."))
        self.hostname = hostname

    def set_directory(self, directory):
        if directory is None or directory == '':
            sys.exit(colored.red("A non-blank directory is required."))
            if re.search(' ', directory) is not None:
                sys.exit(colored.red("A directory cannot contain spaces."))
        self.directory = directory

    def set_username(self, username):
        if username is None or username == '':
            sys.exit(colored.red("A non-blank username is required."))
        self.username = username

    def __repr__(self):
        """Return a representation of a Mech Cloud instance."""
        sep = '\n'
        return ('name:{name}{sep}hostname:{hostname}{sep}directory:{directory}'
                '{sep}username:{username}'.
                format(name=self.name, hostname=self.hostname, directory=self.directory,
                       username=self.username, sep=sep))

    def config(self):
        """Return the configuration for this mech clould instance."""
        entry = {}
        entry['name'] = self.name
        entry['hostname'] = self.hostname
        entry['directory'] = self.directory
        entry['username'] = self.username
        return entry

    def init(self):
        """Initialize the cloud instance.
            - add entry to Mechcloudfile
        """
        print(colored.blue("Writing entry to Mechcloudfile..."))
        clouds = utils.load_mechcloudfile(False)
        clouds[self.name] = self.config()
        utils.save_mechcloudfile(clouds)
        # create remote directory, if it does not exist
        # Note: If using ~/mike for the directory, then ~ will not be expanded
        # when surrounded by quotes. For this reason, directory should not have
        # any spaces in it.
        print(colored.blue("Creating directory (if necessary)..."))
        self.ssh('if ! [ -d {directory} ]; then mkdir {directory} ; fi'
                 .format(directory=self.directory))
        # create virtualenv, if not already created
        print(colored.blue("Creating python virtual environment (if necessary)..."))
        self.ssh('if ! [ -d {directory}/venv ]; then '
                 ' cd {directory}; virtualenv -p python3 venv ; fi'
                 .format(directory=self.directory))
        # install mikemech into that python virtual environment using pip
        print(colored.blue("Installing mikemech into that python virtual environment..."))
        self.ssh('source {}/venv/bin/activate && pip install mikemech'.format(self.directory))
        vmrun_found, _, _ = self.ssh('which vmrun', False)
        if vmrun_found == 0:
            print(colored.green("VMware vmrun was found."))
        else:
            print(colored.yellow("VMware vmrun was not found."))
        vbm_found, _, _ = self.ssh('which VBoxManage', False)
        if vbm_found == 0:
            print(colored.green("Oracle VBoxManage was found."))
        else:
            print(colored.yellow("Oracle VBoxManage was not found."))
        if vmrun_found != 0 and vbm_found != 0:
            print(colored.red("Neither VMware vmrun nor Oracle VBoxManage was found."))
            print(colored.red("The 'mech' command will not be very useful."))
        print("Done.")

    def upgrade(self):
        """Upgrade the cloud instance.
        """
        print(colored.blue("Updating pip on cloud instance:({})...".format(self.name)))
        self.ssh('if ! [ -d {directory}/venv ]; then '
                 ' cd {directory}; pip install -U pip ; fi'
                 .format(directory=self.directory))
        print(colored.blue("Updating mikemech..."))
        self.ssh('if ! [ -d {directory}/venv ]; then '
                 ' cd {directory}; pip install -U mikemech ; fi'
                 .format(directory=self.directory))
        print("Done.")

    def ssh(self, command, print_output_on_error=True):
        """Run ssh command using internal variables (like username and hostname) and print output.

           Parameters:
              command(str): command to execute (ex: 'chmod +x /tmp/file')

        """
        return_code, stdout, stderr = utils.ssh_with_username(hostname=self.hostname,
                                                              username=self.username,
                                                              command="'" + command + "'")
        if print_output_on_error:
            if return_code != 0:
                print(colored.red('Warning: Command did not complete successfully.'
                                  '(return_code:{})'.format(return_code)))
                if stdout:
                    print(stdout)
                if stderr:
                    print(stderr)
        return return_code, stdout, stderr
