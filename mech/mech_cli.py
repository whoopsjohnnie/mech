import logging
import sys


import click


from .mech_instance import MechInstance
from . import utils

# for short and long help options
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# TODO: change back to __name__
# LOGGER = logging.getLogger(__name__)
LOGGER = logging.getLogger('mech')


class CustomMultiCommand(click.Group):

    def command(self, *args, **kwargs):
        """Behaves the same as `click.Group.command()` except if passed
        a list of names, all after the first will be aliases for the first.
        """
        def decorator(f):
            if isinstance(args[0], list):
                _args = [args[0][0]] + list(args[1:])
                for alias in args[0][1:]:
                    cmd = super(CustomMultiCommand, self).command(
                        alias, *args[1:], **kwargs)(f)
                    cmd.short_help = "Alias for '{}'".format(_args[0])
            else:
                _args = args
            cmd = super(CustomMultiCommand, self).command(
                *_args, **kwargs)(f)
            return cmd

        return decorator


@click.group(context_settings=CONTEXT_SETTINGS, cls=CustomMultiCommand)
@click.option('--debug', is_flag=True, default=False)
def cli(debug):
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(filename)s:%(lineno)s %(funcName)s() '
                                  '%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if debug:
        click.echo('Debug is on')
        LOGGER.setLevel(logging.DEBUG)


@cli.command(['list', 'ls'])
@click.option('--detail', '-d', is_flag=True, help='Print detailed info')
@click.argument('instance', required=False)
def list(detail, instance):
    '''Lists all available instances (using Mechfile)'''

    LOGGER.debug("detail:%s", detail)

    if detail:
        click.echo('Instance Details')
        click.echo()
    else:
        click.echo("{}\t{}\t{}\t{}\t{}\t{}".format(
            'NAME'.rjust(20),
            'ADDRESS'.rjust(15),
            'BOX'.rjust(35),
            'VERSION'.rjust(12),
            'PROVIDER'.rjust(12),
            'STATE'.rjust(12),
        ))

    instances = utils.instances()
    LOGGER.debug("instances:%s", instances)
    mechfiles = utils.load_mechfile()
    LOGGER.debug("mechfiles:%s", mechfiles)
    for name in instances:
        LOGGER.debug('name:%s', name)
        inst = MechInstance(name, mechfiles)
        vm_state = "unknown"
        if inst.created:
            ip_address = inst.get_ip()
            vm_state = inst.get_vm_state()
            if vm_state is None:
                vm_state = "unknown"
            if ip_address is None:
                ip_address = "poweroff"
            elif not ip_address:
                ip_address = "running"
        else:
            ip_address = "notcreated"
            vm_state = "notcreated"

        if detail:
            click.echo('==================================')
            click.echo('From Mechfile:')
            click.echo(inst)
            click.echo()
            if inst.provider == 'virtualbox':
                if inst.created:
                    click.echo('From virtualbox:')
                    click.echo(inst.get_vm_info())
        else:
            # deal with box_version being none
            box_version = inst.box_version
            if inst.box_version is None:
                box_version = ''
            click.echo("{}\t{}\t{}\t{}\t{}\t{}".format(
                name.rjust(20),
                ip_address.rjust(15),
                inst.box.rjust(35),
                box_version.rjust(12),
                inst.provider.rjust(12),
                vm_state.rjust(12),
            ))
