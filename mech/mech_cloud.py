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
'''Mech cloud functionality.'''
import logging


import click


from . import utils
from .mech_cloud_instance import MechCloudInstance

LOGGER = logging.getLogger('mech')


class MechCloudAliasedGroup(click.Group):
    '''Enable click command aliases.'''

    def get_command(self, ctx, cmd_name):
        '''get the alias command'''
        try:
            cmd_name = MECH_CLOUD_ALIASES[cmd_name].name
        except KeyError:
            pass
        return super().get_command(ctx, cmd_name)


@click.group(context_settings=utils.context_settings(), cls=MechCloudAliasedGroup)
def cloud():
    '''Cloud operations.

    Notes:
        Mech Cloud is an easy way to expose resources for non-local use.

        If you have a spare desktop/laptop:

            1. Install VMware Workstation and/or Oracle VirtualBox, and

            2. Install pre-requisites ("python3.7+" and "virtualenv")

               For Ubuntu:
                 sudo apt-get install python3.7 python3-pip
                 sudo pip3 install virtualenv

               For Fedora:
                 sudo dnf install python37 python3-pip
                 sudo pip3 install virtualenv

        See https://github.com/Fizzadar/pyinfra/tree/master/examples/virtualbox
        to install virtualbox using `pyinfra`.

        Then add that host as a mech "cloud-instance" using the
        "mech cloud init" command.

        This would allow you to spin up/down virtual machines on that
        computer. For instance, if you have a could-instance called "top",
        you could init and start a VM on the remote computer using:
            mech -C top init bento/ubuntu-18.04
            mech -C top up

        The host's directory needs to have a virtual environment setup in
        "venv" and "mech" needs to be installed under that virtual
        environment, such as: "pip install mikemech". The 'mech cloud init'
        takes care of this for you.

        Virtualbox instances are "global". So, you can have only one
        instance named "first".
    '''


@cloud.command()
@click.argument('hostname', required=True, metavar='HOST')
@click.argument('directory', required=True, metavar='DIR')
@click.argument('username', required=True, metavar='USER')
@click.argument('name', required=True, metavar='NAME')
@click.pass_context
def init(ctx, hostname, directory, username, name):
    """
    Initialize Mechcloudfile and add entry.

    The directory will be created with a python virtual environment (venv)
    and "mikemech" will be installed into it.

    Notes:
       - The "mech cloud init" operation can be run again with same cloud-instance.
         (The values would be updated in the Mechcloudfile).

       - The directory should not contain spaces.

       - If you use '~' in the directory value, be sure it is surrounded by
         single quotes because without quotes or if double quotes (") are used,
         then the '~' will be expanded locally and will not use the remote value.
            Good Example: --directory '~/mikemech'
            Bad Example: --directory "~/mikemech"   (do not use)
    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s hostname:%s directory:%s username:%s name:%s',
                 cloud_name, hostname, directory, username, name)

    if cloud_name:
        # Note: All cloud ops are supported.
        utils.cloud_run(cloud_name, ['cloud'])
        return

    inst = MechCloudInstance(name)
    inst.set_hostname(hostname)
    inst.set_directory(directory)
    inst.set_username(username)
    inst.init()


@cloud.command()
@click.argument('name', required=True, metavar='NAME')
@click.pass_context
def remove(ctx, name):
    """
    Remove a Mech Cloud instance
    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s name:%s', cloud_name, name)

    if cloud_name:
        # Note: All cloud ops are supported.
        utils.cloud_run(cloud_name, ['cloud'])
        return

    if utils.cloud_exists(name):
        utils.remove_mechcloudfile_entry(name=name)
        print("Removed ({}) from mech cloud.".format(name))
        print("Be sure to remove any running virtual machines.")
    else:
        print("Cloud ({}) does not exist in the Mechcloudfile.", name)


@cloud.command()
@click.pass_context
def list(ctx):
    """
    List Mech Clouds
    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s', cloud_name)

    if cloud_name:
        # Note: All cloud ops are supported.
        utils.cloud_run(cloud_name, ['cloud'])
        return

    print('=== mech clouds: ===')
    clouds = utils.cloud_instances()
    for a_cloud in clouds:
        mci = MechCloudInstance(a_cloud)
        mci.read_config(a_cloud)
        print(mci)
        print()


@cloud.command()
@click.argument('name', required=False, metavar='NAME')
@click.pass_context
def upgrade(ctx, name):
    """
    Upgrade 'pip' and 'mikemech' on the cloud instances.
    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s name:%s', cloud_name, name)

    if name:
        instances = [name]
    else:
        instances = utils.cloud_instances()

    for a_name in instances:
        mci = MechCloudInstance(a_name)
        mci.read_config(a_name)
        mci.upgrade()


MECH_CLOUD_ALIASES = {
    'delete': remove,
    'ls': list,
    'rm': remove,
}
