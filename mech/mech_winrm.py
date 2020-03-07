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
import logging
import sys


import click
from pypsrp.client import Client


from . import utils
from .mech_instance import MechInstance

LOGGER = logging.getLogger('mech')


@click.group(context_settings=utils.context_settings())
@click.pass_context
def winrm(ctx):
    '''Winrm operations.'''
    pass


@winrm.command()
@click.argument('instance', required=False)
@click.pass_context
def config(ctx, instance):
    """
    Show winrm configuration.
    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s instance:%s', cloud_name, instance)

    if instance:
        # single instance
        instances = [instance]
    else:
        # multiple instances
        instances = utils.instances()

    for an_instance in instances:
        inst = MechInstance(an_instance)
        if inst.created:
            click.echo(inst.winrm_config())
        else:
            click.secho("VM ({}) is not created.".format(an_instance), fg="red")


@winrm.command()
@click.argument('instance', required=True)
@click.option('--command', '-c', required=False, metavar='COMMAND',
              help='Command to run on instance (using command prompt).')
@click.option('--powershell', '-p', required=False, metavar='POWERSHELL',
              help='Powershell to run on instance.')
@click.pass_context
def run(ctx, instance, command, powershell):
    """
    Run command or powershell using winrm

    Notes:
        Example command: 'date /T'
        Example powershell: 'Write-Host hello'

    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s instance:%s command:%s powershell:%s',
                 cloud_name, instance, command, powershell)

    if (command is None or command == '') and (powershell is None or powershell == ''):
        sys.exit(click.style("Command or Powershell is required", fg="red"))

    inst = MechInstance(instance)

    if inst.created:
        LOGGER.debug("connecting to pypsrp using: server:%s username:%s"
                     " password:%s", inst.get_ip(), inst.user, inst.password)
        utils.suppress_urllib3_errors()
        client = Client(inst.get_ip(), username=inst.user, password=inst.password, ssl=False)
        if command:
            stdout, stderr, rc = client.execute_cmd(command)
            LOGGER.debug('command:%s rc:%d stdout:%s stderr:%s', command, rc, stdout, stderr)
            if stdout:
                click.echo(stdout)
            if stderr:
                click.echo(stderr)
        else:
            output, streams, had_errors = client.execute_ps(powershell)
            LOGGER.debug('powershell:%s output:%s streams:%s '
                         'had_errors:%s', powershell, output, streams, had_errors)
            if output:
                click.echo(output)

    else:
        click.echo("VM not created.")


@winrm.command()
@click.argument('local', required=True)
@click.argument('remote', required=True)
@click.argument('instance', required=True)
@click.pass_context
def copy(ctx, local, remote, instance):
    """
    Copy local file to remote file on instance.
    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s local:%s remote:%s instance:%s',
                 cloud_name, local, remote, instance)

    inst = MechInstance(instance)

    if inst.created:
        utils.suppress_urllib3_errors()
        client = Client(inst.get_ip(), username=inst.user, password=inst.password, ssl=False)
        client.copy(local, remote)
        click.echo("Copied")


@winrm.command()
@click.argument('remote', required=True)
@click.argument('local', required=True)
@click.argument('instance', required=True)
@click.pass_context
def fetch(ctx, remote, local, instance):
    """
    Fetch remote file from instance.
    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s remote:%s local:%s instance:%s',
                 cloud_name, remote, local, instance)

    inst = MechInstance(instance)

    if inst.created:
        utils.suppress_urllib3_errors()
        client = Client(inst.get_ip(), username=inst.user, password=inst.password, ssl=False)
        client.fetch(remote, local)
        click.echo("Fetched")
