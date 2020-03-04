import click


from .mech_instance import MechInstance
from . import utils

# for short and long help options
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--debug', '-D', is_flag=True, help='Show debug')
@click.option('--detail', '-d', is_flag=True, help='Print detailed info')
@click.argument('instance', required=False)
def list(debug, detail, instance):
    '''Lists all available instances (using Mechfile).'''

    if debug:
        click.echo('Debug:')
        click.echo(' instance:{}'.format(instance))
        click.echo(' detail:{}'.format(detail))

    mechfiles = utils.load_mechfile()

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

    for name in list(mechfiles):
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
