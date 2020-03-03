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
"""MechWinrm class"""

from __future__ import print_function, absolute_import


import logging
import sys


import click
from pypsrp.client import Client

from .mech_command import MechCommand
from .mech_instance import MechInstance

LOGGER = logging.getLogger(__name__)


class SuppressFilter(logging.Filter):
    def filter(self, record):
        return 'unparsed data' not in record.getMessage()


class MechWinrm(MechCommand):
    """
    Usage: mech winrm <subcommand> [<args>...]

    Note: Cloud operations are not yet operational/supported.

    Available subcommands:
        config            Get configuration
        run               Run winrm command

    For help on any individual subcommand run `mech winrm <subcommand> -h`
    """

    def config(self, arguments):  # pylint: disable=no-self-use
        """
        Show winrm configuration.

        Usage: mech winrm config [options] <instance>

        Options:
            -h, --help                       Print this help
        """

        instance_name = arguments['<instance>']

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)
            if inst.created:
                click.echo(inst.winrm_config())
            else:
                click.secho("VM ({}) is not created.".format(instance), fg="red")

    def run(self, arguments):  # pylint: disable=no-self-use,unused-argument
        """
        Run command or powershell using winrm

        Usage: mech winrm run [options] <instance>

        Notes:
            Example command: 'date /T'
            Example powershell: 'write-host hello'

        Options:
            -h, --help                       Print this help
            -c, --command COMMAND            Command to run
            -p, --powershell POWERSHELL      Powershell to run
        """
        command = arguments['--command']
        powershell = arguments['--powershell']
        instance = arguments['<instance>']

        if (command is None or command == '') and (powershell is None or powershell == ''):
            sys.exit(click.style("Command or Powershell is required", fg="red"))

        inst = MechInstance(instance)

        if inst.created:
            LOGGER.debug("connecting to pypsrp using: server:%s username:%s"
                         " password:%s", inst.get_ip(), inst.user, inst.password)
            client = Client(inst.get_ip(), username=inst.user, password=inst.password, ssl=False)

            # Note: Not really sure why we need to do this, but it seems to suppress the output
            try:
                from urllib3.connectionpool import log
                log.addFilter(SuppressFilter())
            except:  # noqa: E722
                pass

            if command:
                stdout, stderr, rc = client.execute_cmd(command)
                LOGGER.debug('command:%s rc:%d stdout:%s stderr:%s', command, rc, stdout, stderr)
                if stdout:
                    click.echo(stdout)
                if stderr:
                    click.echo(stderr)
                sys.exit(rc)
            else:
                output, streams, had_errors = client.execute_ps(powershell)
                LOGGER.debug('powershell:%s output:%s streams:%s '
                             'had_errors:%s', powershell, output, streams, had_errors)
                if output:
                    click.echo(output)

        else:
            click.echo("VM not created.")
