import logging
import platform
import sys


import click


from . import utils
from .__init__ import __version__
from .mech_instance import MechInstance
from .vmrun import VMrun
from .vbm import VBoxManage

# for short and long help options
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# TODO: change back to __name__
# LOGGER = logging.getLogger(__name__)
LOGGER = logging.getLogger('mech')

ALIASES = {
    'ls': list,
}


class AliasedGroup(click.Group):
    '''Enable click command aliases.'''
    def get_command(self, ctx, cmd_name):
        '''get the alias command'''
        try:
            cmd_name = ALIASES[cmd_name].name
        except KeyError:
            pass
        return super().get_command(ctx, cmd_name)


@click.group(context_settings=CONTEXT_SETTINGS, cls=AliasedGroup)
@click.option('--debug', is_flag=True, default=False)
@click.option('--cloud')
@click.version_option(version=__version__, message='%(prog)s v%(version)s')
def cli(debug, cloud):
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(filename)s:%(lineno)s %(funcName)s() '
                                  '%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if debug:
        click.echo('Debug is on')
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.debug('cloud:%s', cloud)


@cli.command()
@click.option('--detail', '-d', is_flag=True, help='Print detailed info')
@click.argument('instance', required=False)
def list(detail, instance):
    '''Lists all available instances (using Mechfile)'''

    LOGGER.debug("detail:%s", detail)
    click.echo('cloud:{}'.format(cloud))

# TODO: cloud
#    if self.cloud_name:
#        self.cloud_run(['list', 'ls'])
#        return
#
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
    LOGGER.debug('instances:%s', instances)
    mechfiles = utils.load_mechfile()
    LOGGER.debug('mechfiles:%s', mechfiles)
    for name in instances:
        LOGGER.debug('name:%s', name)
        inst = MechInstance(name, mechfiles)
        vm_state = 'unknown'
        if inst.created:
            ip_address = inst.get_ip()
            vm_state = inst.get_vm_state()
            if vm_state is None:
                vm_state = 'unknown'
            if ip_address is None:
                ip_address = 'poweroff'
            elif not ip_address:
                ip_address = 'running'
        else:
            ip_address = 'notcreated'
            vm_state = 'notcreated'

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
            click.echo('{}\t{}\t{}\t{}\t{}\t{}'.format(
                name.rjust(20),
                ip_address.rjust(15),
                inst.box.rjust(35),
                box_version.rjust(12),
                inst.provider.rjust(12),
                vm_state.rjust(12),
            ))


@cli.command()
@click.option('--detail', '-d', is_flag=True, help='Print detailed info')
@click.argument('instance', required=False)
def support(detail, instance):
    '''Show info that would be helpful for support.'''

# TODO: cloud

    click.echo('If you are having issues with mikemech or wish to make feature requests, ')
    click.echo('please check out the GitHub issues at https://github.com/mkinney/mech/issues .')
    click.echo('')
    click.echo('When adding an issue, be sure to include the following:')
    click.echo(' System: {0}'.format(platform.system()))
    click.echo('   Platform: {0}'.format(platform.platform()))
    click.echo('   Release: {0}'.format(platform.uname().release))
    click.echo('   Machine: {0}'.format(platform.uname().machine))
    click.echo(' mikemech: v{0}'.format(__version__))
    click.echo(' Executable: {0}'.format(sys.argv[0]))
    click.echo(' Python: {0} ({1}, {2})'.format(
        platform.python_version(),
        platform.python_implementation(),
        platform.python_compiler(),
    ))


@cli.command()
@click.argument('instance', required=False)
def port(instance):

#    if self.cloud_name:
#        self.cloud_run(['port'])
#        return

    if platform.system() == 'Linux':
        sys.exit(click.style('This command is not supported on this OS.', fg="red"))

    if instance:
        # single instance
        instances = [instance]
    else:
        # multiple instances
        instances = utils.instances()

    # FUTURE: implement port forwarding?
    for instance in instances:
        inst = MechInstance(instance)

        if inst.provider == 'vmware':
            click.echo('Instance ({}):'. format(instance))
            nat_found = False
            vmrun = VMrun(inst.vmx)
            for line in vmrun.list_host_networks().split('\n'):
                network = line.split()
                if len(network) > 2 and network[2] == 'nat':
                    click.echo(vmrun.list_port_forwardings(network[1]))
                    nat_found = True
            if not nat_found:
                click.secho("Cannot find a nat network", fg="red")
        else:
            click.secho("Not yet implemented on this platform.", fg="red")
