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
"""MechCloud class"""

from __future__ import print_function, absolute_import


import logging


from . import utils
from .mech_command import MechCommand
from .mech_cloud_instance import MechCloudInstance

LOGGER = logging.getLogger(__name__)


class MechCloud(MechCommand):
    """
    Usage: mech cloud <subcommand> [<args>...]

    Notes:
        Mech Cloud is an easy way to expose resources for non-local use.
        For instance, if you have a spare desktop/laptop, install
        VMware Workstation and/or Oracle VirtualBox and add
        that host as a mech "cloud-instance".
        This would allow you to spin up/down virtual machines on that
        computer. For instance, if you have a could-instance called "top",
        from this computer, you could init and start a VM on the remote
        computer using these commands:
        The host's directory needs to have a virtual environment setup in
        "venv" and "mech" needs to be installed under that virtual
        environment, such as: "pip install mikemech".

            mech -C top init bento/ubuntu-18.04
            mech -C top up

    Available subcommands:
        init              initialize the mech cloud instance
        remove            remove a mech cloud instance
        list              list the mech clould instances

    For help on any individual subcommand run `mech cloud <subcommand> -h`
    """

    def init(self, arguments):  # pylint: disable=no-self-use,unused-argument
        """
        Initialize the Mech Cloud configuration.

        Usage: mech cloud init [options] --hostname HOST --directory DIR <cloud-instance>

        Notes:
           Can be run again with same cloud-instance. (The values would be
           updated in the Mechcloudfile).

        Options:
            --hostname HOST                  Hostname (resolvable hostname or ip)
            --directory DIR                  Directory on remote host where mech will be installed
            -h, --help                       Print this help
        """
        hostname = arguments['--hostname']
        directory = arguments['--directory']
        cloud_instance = arguments['<cloud-instance>']

        inst = MechCloudInstance(cloud_instance)
        inst.set_hostname(hostname)
        inst.set_directory(directory)
        inst.init()

    def remove(self, arguments):  # pylint: disable=no-self-use,unused-argument
        """
        Remove a Mech Cloud instance

        Usage: mech cloud remove [options] <cloud-instance>

        Options:
            -h, --help                       Print this help
        """
        cloud_instance = arguments['<cloud-instance>']
        utils.remove_mechcloudfile_entry(name=cloud_instance)

    def list(self, arguments):  # pylint: disable=no-self-use,unused-argument
        """
        List Mech Clouds

        Usage: mech cloud list [options]

        Options:
            -h, --help                       Print this help
        """
        clouds = utils.load_mechcloudfile(True)
        # TODO: impove the output
        print(clouds)
