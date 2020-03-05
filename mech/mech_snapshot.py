import logging
import sys


import click


from . import utils
from .mech_instance import MechInstance
from .vmrun import VMrun

LOGGER = logging.getLogger(__name__)


class MechSnapshotAliasedGroup(click.Group):
    '''Enable click command aliases.'''

    def get_command(self, ctx, cmd_name):
        '''get the alias command'''
        try:
            cmd_name = MECH_SNAPSHOT_ALIASES[cmd_name].name
        except KeyError:
            pass
        return super().get_command(ctx, cmd_name)


@click.group(context_settings=utils.context_settings(), cls=MechSnapshotAliasedGroup)
@click.pass_context
def snapshot(ctx):
    '''Snapshot operations.'''
    pass


@snapshot.command()
@click.argument('name', required=True)
@click.argument('instance', required=True)
@click.pass_context
def delete(ctx, name, instance):
    """
    Delete a snapshot taken previously with snapshot save.
    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s name:%s instance:%s',
                 cloud_name, name, instance)

    inst = MechInstance(instance)

    if inst.provider == 'vmware':
        vmrun = VMrun(inst.vmx)
        if vmrun.delete_snapshot(name) is None:
            click.secho("Cannot delete name", fg="red")
        else:
            click.secho("Snapshot {} deleted".format(name), fg="green")
    else:
        click.secho("Not yet implemented on this platform.", fg="red")


@snapshot.command()
@click.argument('instance', required=True)
@click.pass_context
def list(ctx, instance):
    """
    List all snapshots taken for an instance.
    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s instance:%s',
                 cloud_name, instance)

    if instance:
        # single instance
        instances = [instance]
    else:
        # multiple instances
        instances = utils.instances()

    for an_instance in instances:
        inst = MechInstance(an_instance)
        click.echo('Snapshots for instance:{}'.format(an_instance))
        if inst.created:
            if inst.provider == 'vmware':
                vmrun = VMrun(inst.vmx)
                click.echo(vmrun.list_snapshots())
            else:
                click.secho("Not yet implemented on this platform.", fg="red")
        else:
            click.secho('Instance ({}) is not created.'.format(an_instance), fg="red")


@snapshot.command()
@click.argument('name', required=True)
@click.argument('instance', required=True)
@click.pass_context
def save(ctx, name, instance):
    """
    Take a snapshot of the current state of the instance.

    Notes:
        Snapshots are useful for experimenting in a machine for being able
        to rollback quickly.
    """
    cloud_name = ctx.obj['cloud_name']
    LOGGER.debug('cloud_name:%s name:%s instance:%s',
                 cloud_name, name, instance)

    inst = MechInstance(instance)
    if inst.created:
        if inst.provider == 'vmware':
            vmrun = VMrun(inst.vmx)
            if vmrun.snapshot(name) is None:
                sys.exit(click.style("Warning: Could not take snapshot.", fg="red"))
            else:
                click.secho("Snapshot ({}) on VM ({}) taken".format(name, instance), fg="green")
        else:
            click.secho("Not yet implemented on this platform.", fg="red")
    else:
        click.secho('Instance ({}) is not created.'.format(instance), fg="red")


MECH_SNAPSHOT_ALIASES = {
    'ls': list,
    'remove': delete,
    'rm': delete,
}
