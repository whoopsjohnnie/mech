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
import fnmatch
import logging
import os
import shutil
import sys

import click

from . import utils

LOGGER = logging.getLogger('mech')


class MechBoxAliasedGroup(click.Group):
    '''Enable click command aliases.'''

    def get_command(self, ctx, cmd_name):
        '''get the alias command'''
        try:
            cmd_name = MECH_BOX_ALIASES[cmd_name].name
        except KeyError:
            pass
        return super().get_command(ctx, cmd_name)


@click.group(context_settings=utils.context_settings(), cls=MechBoxAliasedGroup)
@click.pass_context
def box(ctx):
    '''Box operations.

    A box is typically a compressed tar file that contains all files necessary for
    VMware or Virtualbox to import/use.
    '''
    pass


@box.command()
@click.argument('location', required=True)
@click.option('--box-version', metavar='VERSION', help='Constrain to specific box version.')
@click.option('-f', '--force', is_flag=True, default=False, help='Overwrite existing Mechfile.')
@click.option('--provider', metavar='PROVIDER', default='vmware',
              help='Provider (`vmware` or `virtualbox`)')
@click.pass_context
def add(ctx, location, box_version, force, provider):
    """
    Add a box to the catalog of available boxes.

    Notes:
        The location can be a:
            URL (ex: 'http://example.com/foo.box'),
            box file (ex: 'file:/mnt/boxen/foo.box'),
            json file (ex: 'file:/tmp/foo.json'), or
            HashiCorp account/box (ex: 'bento/ubuntu-18.04').
    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s location:%s box_version:%s '
                 'force:%s provider:%s', cloud_name,
                 location, box_version, force, provider)

    if not utils.valid_provider(provider):
        sys.exit(click.style('Need to provide valid provider.', fg='red'))

    utils.add_box(name=None, box=None, location=location, box_version=box_version,
                  force=force, provider=provider)


@box.command()
@click.pass_context
def list(ctx):
    """
    List all available boxes in the catalog.
    """

    print("{}\t{}\t{}".format(
        'BOX'.rjust(35),
        'VERSION'.rjust(12),
        'PROVIDER'.rjust(12),
    ))
    path = os.path.abspath(os.path.join(utils.mech_dir(), 'boxes'))
    for root, _, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*.box'):
            directory = os.path.dirname(os.path.join(root, filename))[len(path) + 1:]
            provider, account, box, version = directory.split('/', 3)
            print("{}\t{}\t{}".format(
                "{}/{}".format(account, box).rjust(35),
                version.rjust(12),
                provider.rjust(12),
            ))


@box.command()
@click.option('--name', metavar='BOXNAME', required=True,
              help='Box name (ex: `bento/ubuntu-18.04`).')
@click.option('--provider', metavar='PROVIDER', default='vmware',
              help='Provider (`vmware` or `virtualbox`)')
@click.option('--version', metavar='VERSION', required=True, help='Box version.')
@click.pass_context
def remove(ctx, name, provider, version):
    """
    Remove a box that matches the name, provider and version.
    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s name:%s provider:%s version:%s',
                 cloud_name, name, provider, version)

    if not utils.valid_provider(provider):
        sys.exit(click.style("Need to provide valid provider.", fg="red"))

    path = os.path.abspath(os.path.join(utils.mech_dir(), 'boxes', provider, name, version))
    if os.path.exists(path):
        shutil.rmtree(path)
        print("Removed {} {}".format(name, version))
    else:
        print("No boxes were removed.")


MECH_BOX_ALIASES = {
    'delete': remove,
    'ls': list,
    'rm': remove,
}
