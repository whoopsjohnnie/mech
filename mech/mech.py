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
"""Mech class"""

from __future__ import print_function, absolute_import

import os
import platform
import sys
import logging
import textwrap
import shutil
import subprocess

from clint.textui import colored

from . import utils
from .vmrun import VMrun
from .vbm import VBoxManage
from .mech_instance import MechInstance
from .mech_command import MechCommand
from .mech_box import MechBox
from .mech_cloud import MechCloud
from .mech_cloud_instance import MechCloudInstance
from .mech_snapshot import MechSnapshot

LOGGER = logging.getLogger(__name__)


class Mech(MechCommand):
    """
    Usage: mech [options] <command> [<args>...]

    Notes:
        "mech" provides an easy way to control virtual machines.
        An "instance" is a virtual machine.

    Options:
        --cloud CLOUD                    Cloud to run the mech command on.
        --debug                          Show debug messages.
        -h, --help                       Print this help.
        -v, --version                    Print the version and exit.

    Common commands:
        box               manages boxes: add, list remove, etc.
        cloud             manages mech cloud
        destroy           stops and deletes all traces of the instance(s)
        (down|stop|halt)  stops the instance(s)
        global-status     outputs status of all virutal machines on this host
        init              initializes a new Mech environment (creates Mechfile)
        ip                outputs ip of an instance
        (list|ls)         lists instances
        pause             pauses the instance(s)
        port              displays guest port mappings (not fully implemented)
        provision         provisions the instance(s)
        ps                list running processes in guest
        (resume|unpause)  resume paused/suspended instance(s)
        scp               copies files to/from an instance via SCP
        snapshot          manages snapshots: save, list, remove, etc.
        ssh               connects to an instance via SSH (or run a command)
        ssh-config        outputs OpenSSH valid configuration to connect to instance
        suspend           suspends the instance(s)
        (up|start)        starts instance(s)
        upgrade           upgrade the instance(s) - vmware only

    For help on any individual command run `mech <command> -h`

    All "state" will be saved in .mech directory. (boxes and instances)

    Examples:

    Initializing and using a box from HashiCorp's Vagrant Cloud:

        mech init bento/ubuntu-18.04
        mech up
        mech ssh

    Having a problem with a command, add the "--debug" option like this:

        mech --debug up

    """

    subcommand_name = '<command>'

    def __init__(self, arguments):
        super(Mech, self).__init__(arguments)
        self.cloud_name = None

        logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter('%(filename)s:%(lineno)s %(funcName)s() '
                                      '%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        if arguments['--debug']:
            logger.setLevel(logging.DEBUG)
        cloud = arguments['--cloud']
        if cloud:
            self.cloud_name = cloud

    box = MechBox
    cloud = MechCloud
    snapshot = MechSnapshot

    def cloud_run(self, operations):
        """Run the command on the cloud instance.
        """
        if self.cloud_name and self.cloud_name != '':
            mci = MechCloudInstance(self.cloud_name)
            mci.read_config(self.cloud_name)

            # find out what args were used on the command line
            # any command after the operation will be appended to
            # the command to run on the remote
            args_list = []
            found_operation = False
            LOGGER.debug('sys.argv:%s', sys.argv)
            for arg in sys.argv:
                if arg in operations:
                    found_operation = True
                if found_operation:
                    args_list.append(arg)
            args_string = ' '.join(args_list)
            LOGGER.debug('cloud_name:%s operations:%s args_list:%s args_string:%s',
                         self.cloud_name, operations, args_list, args_string)
            command = ('''ssh {username}@{hostname} -- "cd {directory}; '''
                       '''source {directory}/venv/bin/activate && '''
                       '''mech {args_string}"''').format(hostname=mci.hostname,
                                                         directory=mci.directory,
                                                         username=mci.username,
                                                         args_string=args_string)
            LOGGER.debug('command:%s', command)
            result = subprocess.run(command, shell=True, capture_output=True)
            stdout = result.stdout.decode('utf-8')
            stderr = result.stderr.decode('utf-8')
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            return result.returncode, stdout, stderr

    def init(self, arguments):  # pylint: disable=no-self-use
        """
        Initializes a new mech environment by creating a Mechfile.

        Usage: mech init [options] <location>

        Notes:
          - The location can be a:
              + URL (ex: 'http://example.com/foo.box'),
              + box file (ex: 'file:/mnt/boxen/foo.box'),
              + json file (ex: 'file:/tmp/foo.json'), or
              + HashiCorp account/box (ex: 'bento/ubuntu-18.04').
          - A default shared folder name 'mech' will be available
            in the guest for the current directory.
          - The 'add-me' option will add the currently logged in user to the guest,
            add the same user to sudoers, and add the id_rsa.pub key to the
            authorized_hosts file for that user.
          - The 'use-me' option will use the currently logged in user for
            future interactions with the guest instead of the vagrant user.

        Options:
            -a, --add-me                     Add the current host user/pubkey to guest
                --box BOXNAME                Name of the box (ex: bento/ubuntu-18.04)
                --box-version VERSION        Constrain version of the added box
            -f, --force                      Overwrite existing Mechfile
            -h, --help                       Print this help
                --name INSTANCE              Name of the instance (myinst1)
            -p, --provider PROVIDER          Provider ('vmware' or 'virtualbox')
            -u, --use-me                     Use the current user for mech interactions
        """
        add_me = arguments['--add-me']
        use_me = arguments['--use-me']
        name = arguments['--name']
        box_version = arguments['--box-version']
        box = arguments['--box']
        location = arguments['<location>']
        provider = arguments['--provider']

        if provider is None:
            provider = 'vmware'
        if not utils.valid_provider(provider):
            sys.exit(colored.red("Need to provide valid provider."))

        if not name or name == "":
            name = "first"

        force = arguments['--force']

        LOGGER.debug('name:%s box:%s box_version:%s location:%s provider:%s',
                     name, box, box_version, location, provider)

        if self.cloud_name:
            self.cloud_run(['init'])
            return

        if os.path.exists('Mechfile') and not force:
            sys.exit(colored.red(textwrap.fill(
                "`Mechfile` already exists in this directory. Remove it "
                "before running `mech init`.")))

        print(colored.green("Initializing mech"))
        utils.init_mechfile(
            location=location,
            box=box,
            name=name,
            box_version=box_version,
            add_me=add_me,
            use_me=use_me,
            provider=provider)
        print(colored.green(textwrap.fill(
            "A `Mechfile` has been initialized and placed in this directory. "
            "You are now ready to `mech up` your first virtual environment!")))

    def add(self, arguments):  # pylint: disable=no-self-use
        """
        Add instance to the Mechfile.

        Usage: mech add [options] <name> <location>

        Example box: bento/ubuntu-18.04

        Notes:
        - The 'add-me' option will add the currently logged in user to the guest,
          add the same user to sudoers, and add the id_rsa.pub key to the authorized_hosts file
          for that user.

        Options:
            -a, --add-me                     Add the current host user/pubkey to guest
                --box BOXNAME                Name of the box (ex: bento/ubuntu-18.04)
                --box-version VERSION        Constrain version of the added box
            -h, --help                       Print this help
            -p, --provider PROVIDER          Provider ('vmware' or 'virtualbox')
            -u, --use-me                     Use the current user for mech interactions
        """
        name = arguments['<name>']
        box_version = arguments['--box-version']
        box = arguments['--box']
        add_me = arguments['--add-me']
        use_me = arguments['--use-me']
        provider = arguments['--provider']
        location = arguments['<location>']

        print('before provider:{}'.format(provider))
        if provider is None:
            provider = 'vmware'
        if not utils.valid_provider(provider):
            sys.exit(colored.red("Need to provide valid provider."))
        print('after provider:{}'.format(provider))

        if not name or name == "":
            sys.exit(colored.red("Need to provide a name for the instance to add to the Mechfile."))

        if self.cloud_name:
            self.cloud_run(['add'])
            return

        LOGGER.debug('name:%s box:%s box_version:%s location:%s provider:%s',
                     name, box, box_version, location, provider)

        print(colored.green("Adding ({}) to the Mechfile.".format(name)))

        utils.add_to_mechfile(
            location=location,
            box=box,
            name=name,
            box_version=box_version,
            add_me=add_me,
            use_me=use_me,
            provider=provider)
        print(colored.green("Added to the Mechfile."))

    def remove(self, arguments):
        """
        Remove instance from the Mechfile.

        Usage: mech remove [options] <name>

        Options:
            -h, --help                       Print this help
        """
        name = arguments['<name>']

        if not name or name == "":
            sys.exit(colored.red("Need to provide a name to be removed from the Mechfile."))

        if self.cloud_name:
            self.cloud_run(['remove', 'delete', 'rm'])
            return

        LOGGER.debug('name:%s', name)

        self.activate_mechfile()
        inst = self.mechfile.get(name, None)
        if inst:
            print(colored.green("Removing ({}) from the Mechfile.".format(name)))
            utils.remove_mechfile_entry(name=name)
            print(colored.green("Removed from the Mechfile."))
        else:
            sys.exit(colored.red("There is no instance called ({}) in the Mechfile.".format(name)))

    # add aliases for 'mech delete'
    delete = remove
    rm = remove

    def up(self, arguments):  # pylint: disable=invalid-name
        """
        Starts and provisions the mech environment.

        Usage: mech up [options] [<instance>]

        Notes:
           - If no instance is specified, all instances will be started.
           - The options (memsize, numvcpus, and no-nat) will only be applied
             upon first run of the 'up' command.
           - The 'no-nat' option will only be applied if there is no network
             interface supplied in the box file for 'vmware'. For 'virtualbox',
             if you need internet access from the vm, then you will want to
             use 'no-nat'. Interface 'en0' will be used for bridge.
           - Unless 'disable-shared-folders' is used, a default read/write
             share called "mech" will be mounted from the current directory.
             '/mnt/hgfs/mech' on 'vmware' and '/mnt/mech' on 'virtualbox'
             To add/change shared folders, modify the Mechfile directly, then
             stop/start the VM.
           - The 'remove-vagrant' option will remove the vagrant account from the
             guest VM which is what 'mech' uses to communicate with the VM.
             Be sure you can connect/admin the instance before using this option.
             Be sure to check that root cannot ssh, or change the root password.

        Options:
                --disable-provisioning       Do not provision
                --disable-shared-folders     Do not share folders with VM
                --gui                        Start GUI
                --memsize 1024               Specify memory size in MB
                --no-cache                   Do not save the downloaded box
                --no-nat                     Do not use NAT network (i.e., bridged)
                --numvcpus 1                 Specify number of vcpus
            -h, --help                       Print this help
            -r, --remove-vagrant             Remove vagrant user
        """
        gui = arguments['--gui']
        disable_shared_folders = arguments['--disable-shared-folders']
        disable_provisioning = arguments['--disable-provisioning']
        save = not arguments['--no-cache']
        remove_vagrant = arguments['--remove-vagrant']

        memsize = arguments['--memsize']
        numvcpus = arguments['--numvcpus']
        no_nat = arguments['--no-nat']

        instance_name = arguments['<instance>']

        if self.cloud_name:
            self.cloud_run(['up', 'start'])
            return

        LOGGER.debug('gui:%s disable_shared_folders:%s disable_provisioning:%s '
                     'save:%s numvcpus:%s memsize:%s no_nat:%s', gui,
                     disable_shared_folders, disable_provisioning, save,
                     numvcpus, memsize, no_nat)

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)

            inst.gui = gui
            inst.disable_shared_folders = disable_shared_folders
            inst.disable_provisioning = disable_provisioning
            inst.remove_vagrant = remove_vagrant
            inst.no_nat = no_nat

            location = inst.url
            if not location:
                location = inst.box_file

            # only run init_box on first "up"
            # extracts the VM files from the singular .box archive
            if not inst.created:
                path_to_vmx_or_vbox = utils.init_box(
                    instance,
                    box=inst.box,
                    box_version=inst.box_version,
                    location=location,
                    instance_path=inst.path,
                    save=save,
                    numvcpus=numvcpus,
                    memsize=memsize,
                    no_nat=no_nat,
                    provider=inst.provider)
                if inst.provider == 'vmware':
                    inst.vmx = path_to_vmx_or_vbox
                else:
                    inst.vbox = path_to_vmx_or_vbox
                    vbm = VBoxManage()
                    if memsize:
                        vbm.memory(inst.name, memsize)
                    if numvcpus:
                        vbm.cpus(inst.name, numvcpus)
                    # virtualbox wants to add shared folder before starting VM
                    utils.share_folders(inst)

                inst.created = True

            utils.start_vm(inst)

    # allows "mech start" to alias to "mech up"
    start = up

    def global_status(self, arguments):  # pylint: disable=no-self-use,unused-argument
        """
        Outputs info about all VMs running on this computer.

        Usage: mech global-status [options]

        Options:
            -h, --help                       Print this help
        """

        if self.cloud_name:
            self.cloud_run(['global-status'])
            return

        vmrun = VMrun()
        if vmrun.installed():
            print("===VMware VMs===")
            print(vmrun.list())

        vbm = VBoxManage()
        if vbm.installed():
            print("===VirtualBox VMs===")
            print(vbm.list())

    def ps(self, arguments):  # pylint: disable=invalid-name,no-self-use
        """
        List running processes in Guest OS.

        Usage: mech ps [options] <instance>

        Options:
            -h, --help                       Print this help
        """
        instance_name = arguments['<instance>']

        if self.cloud_name:
            self.cloud_run(['ps', 'process-status'])
            return

        inst = MechInstance(instance_name)

        if inst.created:
            _, stdout, _ = utils.ssh(inst, "ps -ef")
            print(stdout)
        else:
            print("VM {} not created.".format(instance_name))

    # alias "mech process-status" to "mech ps"
    process_status = ps

    def destroy(self, arguments):
        """
        Stops and deletes all traces of the instances.

        Usage: mech destroy [options] [<instance>]

        Options:
            -f, --force                      Destroy without confirmation.
            -h, --help                       Print this help
        """
        force = arguments['--force']

        instance_name = arguments['<instance>']

        if self.cloud_name:
            self.cloud_run(['destroy'])
            return

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)

            if os.path.exists(inst.path):
                if force or utils.confirm("Are you sure you want to delete {} "
                                          "at {}".format(inst.name, inst.path), default='n'):
                    print(colored.green("Deleting ({})...".format(instance)))

                    if inst.provider == 'vmware':
                        vmrun = VMrun(inst.vmx)
                        vmrun.stop(mode='hard', quiet=True)
                        vmrun.delete_vm()
                    else:
                        vbm = VBoxManage()

                        vbm.stop(vmname=inst.name, quiet=True)
                        vbm.unregister(vmname=inst.name, quiet=True)

                    if os.path.exists(inst.path):
                        shutil.rmtree(inst.path)
                    print("Deleted")
                else:
                    print(colored.red("Delete aborted."))
            else:
                print(colored.red("VM ({}) not created.".format(instance)))

    def down(self, arguments):
        """
        Stops the instances.

        Usage: mech down [options] [<instance>]

        Options:
            -f, --force                      Force a hard stop
            -h, --help                       Print this help
        """
        force = arguments['--force']

        instance_name = arguments['<instance>']

        if self.cloud_name:
            self.cloud_run(['down', 'halt', 'stop'])
            return

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)

            if inst.created:
                if inst.provider == 'vmware':
                    vmrun = VMrun(inst.vmx)
                    if not force and vmrun.installed_tools():
                        stopped = vmrun.stop()
                    else:
                        stopped = vmrun.stop(mode='hard')
                    if stopped is None:
                        print(colored.red("Not stopped", vmrun))
                    else:
                        print(colored.green("Stopped", vmrun))
                else:
                    vbm = VBoxManage()
                    stopped = vbm.stop(vmname=inst.name, quiet=True)
                    if stopped is None:
                        print(colored.red("Not stopped", vbm))
                    else:
                        print(colored.green("Stopped", vbm))
            else:
                print(colored.red("VM ({}) not created.".format(instance)))

    # alias 'mech stop' and 'mech halt' to 'mech down'
    stop = down
    halt = down

    def pause(self, arguments):
        """
        Pauses the instances.

        Usage: mech pause [options] [<instance>]

        Options:
            -h, --help                       Print this help
        """
        instance_name = arguments['<instance>']

        if self.cloud_name:
            self.cloud_run(['pause'])
            return

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)

            if inst.created:
                if inst.provider == 'vmware':
                    vmrun = VMrun(inst.vmx)
                    pause_results = vmrun.pause()
                    if pause_results is None:
                        print(colored.red("Not paused", vmrun))
                    else:
                        print(colored.yellow("Paused", vmrun))
                else:
                    vbm = VBoxManage()
                    pause_results = vbm.pause(inst.name)
                    if pause_results is None:
                        print(colored.red("Not paused", vbm))
                    else:
                        print(colored.yellow("Paused", vbm))
            else:
                print(colored.red("VM ({}) not created.".format(instance)))

    def upgrade(self, arguments):
        """
        Upgrade the vm file format and virtual hardware for the instance(s).

        Usage: mech upgrade [options] [<instance>]

        Note: The VMs must be created and stopped.

        Options:
            -h, --help                       Print this help
        """
        instance_name = arguments['<instance>']

        if self.cloud_name:
            self.cloud_run(['upgrade'])
            return

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)

            if inst.created:
                if inst.provider == 'vmware':
                    vmrun = VMrun(inst.vmx)
                    state = vmrun.check_tools_state(quiet=True)
                    if state == "running":
                        print("VM must be stopped before doing upgrade.")
                    else:
                        if vmrun.upgradevm(quiet=False) is None:
                            print(colored.red("Not upgraded", vmrun))
                        else:
                            print(colored.yellow("Upgraded", vmrun))
                else:
                    print(colored.red("Functionality not available on this platform."))
            else:
                print(colored.red("VM ({}) not created.".format(instance)))

    def resume(self, arguments):
        """
        Resume a paused/suspended instances.

        Usage: mech resume [options] [<instance>]

        Options:
            --disable-shared-folders         Do not share folders with VM
            -h, --help                       Print this help
        """
        instance_name = arguments['<instance>']
        disable_shared_folders = arguments['--disable-shared-folders']

        LOGGER.debug('instance_name:%s '
                     'disable_shared_folders:%s', instance_name, disable_shared_folders)

        if self.cloud_name:
            self.cloud_run(['resume', 'unpause'])
            return

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)
            inst.disable_shared_folders = disable_shared_folders
            LOGGER.debug('instance:%s', instance)

            # if we have started this instance before, try to unpause
            if inst.created:
                utils.unpause_vm(inst)
            else:
                print(colored.red("VM not created"))
    # allow 'mech unpause' as alias to 'mech resume'
    unpause = resume

    def suspend(self, arguments):
        """
        Suspends instances.

        Usage: mech suspend [options] [<instance>]

        Options:
            -h, --help                       Print this help
        """
        instance_name = arguments['<instance>']

        if self.cloud_name:
            self.cloud_run(['suspend'])
            return

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)

            if inst.created:
                if inst.provider == 'vmware':
                    vmrun = VMrun(inst.vmx)
                    if vmrun.suspend() is None:
                        print(colored.red("Not suspended", vmrun))
                    else:
                        print(colored.green("Suspended", vmrun))
                else:
                    print(colored.red("Not sure equivalent command on this platform."))
                    print(colored.red("If you know, please open issue on github."))
            else:
                print("VM has not been created.")

    def ssh_config(self, arguments):
        """
        Output OpenSSH valid configuration to connect to the machine.

        Usage: mech ssh-config [options] [<instance>]

        Options:
            -h, --help                       Print this help
        """
        instance_name = arguments['<instance>']

        if self.cloud_name:
            self.cloud_run(['ssh-config'])
            return

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)
            if inst.created:
                print(utils.config_ssh_string(inst.config_ssh()))
            else:
                print(colored.red("VM ({}) is not created.".format(instance)))

    def ssh(self, arguments):  # pylint: disable=no-self-use
        """
        Connects to machine via SSH.

        Usage: mech ssh [options] <instance> [-- <extra-ssh-args>...]

        Options:
            -c, --command COMMAND            Execute an SSH command directly
            -p, --plain                      Plain mode, leaves authentication up to user
            -h, --help                       Print this help
        """
        plain = arguments['--plain']
        extra = arguments['<extra-ssh-args>']
        command = arguments['--command']

        instance = arguments['<instance>']

        if self.cloud_name:
            print(colored.red("Using 'ssh' on cloud instance is not supported."))
            return

        inst = MechInstance(instance)

        if inst.created:
            rc, stdout, stderr = utils.ssh(inst, command, plain, extra)
            LOGGER.debug('command:%s rc:%d stdout:%s stderr:%s', command, rc, stdout, stderr)
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            sys.exit(rc)
        else:
            print("VM not created.")

    def scp(self, arguments):  # pylint: disable=no-self-use
        """
        Copies files to and from the machine via SCP.

        Usage: mech scp [options] <src> <dst> [-- <extra-ssh-args>...]

        Options:
            -h, --help                       Print this help
        """
        extra = arguments['<extra-ssh-args>']
        src = arguments['<src>']
        dst = arguments['<dst>']

        if self.cloud_name:
            self.cloud_run(['scp'])
            return

        dst_instance, dst_is_host, dst = dst.partition(':')
        src_instance, src_is_host, src = src.partition(':')

        instance_name = None
        if dst_is_host and src_is_host:
            sys.exit(colored.red("Both src and dst are host destinations"))
        if dst_is_host:
            instance_name = dst_instance
        else:
            dst = dst_instance
        if src_is_host:
            instance_name = src_instance
        else:
            src = src_instance

        if instance_name is None:
            sys.exit(colored.red("Could not determine instance name."))

        inst = MechInstance(instance_name)

        if inst.created:
            _, _, stderr = utils.scp(inst, src, dst, dst_is_host, extra)
            if stderr != '':
                print(stderr)
        else:
            print(colored.red('VM not created.'))

    def ip(self, arguments):  # pylint: disable=invalid-name,no-self-use
        """
        Outputs ip of the Mech machine.

        Usage: mech ip [options] <instance>

        Options:
            -h, --help                       Print this help
        """
        instance = arguments['<instance>']

        if self.cloud_name:
            self.cloud_run(['ip', 'ip_address'])
            return

        inst = MechInstance(instance)

        if inst.created:
            ip_address = inst.get_ip()
            if ip_address:
                print(colored.green(ip_address))
            else:
                print(colored.red("Unknown IP address"))
        else:
            print(colored.yellow("VM not created"))

    # alias 'mech ip_address' to 'mech ip'
    ip_address = ip

    def provision(self, arguments):
        """
        Provisions the Mech machine.

        Usage: mech provision [options] [<instance>]

        Notes:
          - There are a few provision types: 'file', 'shell', and 'pyinfra'.
          - 'shell' can be inline.
          - 'shell' and 'pyinfra' can have a remote endpoint ('http', 'https',
            'ftp') for the script.
            (ex: 'http://example.com/somefile.sh' or ex: 'ftp://foo.com/install.sh')
          - 'pyinfra' scripts must end with '.py' and 'pyinfra' must be installed.
            See https://pyinfra.readthedocs.io/en/latest/ for more info.
          - Provisioning is run when the instance is started. This option
            is if you want to re-run the provisioning.
          - An example of provisioning could be installing puppet (or your config tool
            of choice).

        Options:
            -h, --help                       Print this help
            -s, --show-only                  Show the provisioning info (do not run)
        """
        show = arguments['--show-only']
        instance_name = arguments['<instance>']

        if self.cloud_name:
            self.cloud_run(['provision'])
            return

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)

            if inst.created:
                utils.provision(inst, show)
            else:
                print("VM not created.")

    def port(self, arguments):
        """
        Displays information about guest port mappings.

        Usage: mech port [options] [<instance>]

        Options:
                --guest PORT                 Output the host port that maps to the given guest port
            -h, --help                       Print this help
        """
        instance_name = arguments['<instance>']

        if self.cloud_name:
            self.cloud_run(['port'])
            return

        if platform.system() == 'Linux':
            sys.exit('This command is not supported on this OS.')

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        # FUTURE: implement port forwarding?
        for instance in instances:
            inst = MechInstance(instance)

            if inst.provider == 'vmware':
                print('Instance ({}):'. format(instance))
                nat_found = False
                vmrun = VMrun(inst.vmx)
                for line in vmrun.list_host_networks().split('\n'):
                    network = line.split()
                    if len(network) > 2 and network[2] == 'nat':
                        print(vmrun.list_port_forwardings(network[1]))
                        nat_found = True
                if not nat_found:
                    print(colored.red("Cannot find a nat network"), file=sys.stderr)
            else:
                print(colored.red("Not yet implemented on this platform."))

    def list(self, arguments):
        """
        Lists all available boxes from Mechfile.

        Usage: mech list [options]

        Options:
            -d, --detail                     Print detailed info
            -h, --help                       Print this help
        """

        detail = arguments['--detail']

        if self.cloud_name:
            self.cloud_run(['list', 'ls'])
            return

        self.activate_mechfile()

        if detail:
            print('Instance Details')
            print()
        else:
            print("{}\t{}\t{}\t{}\t{}\t{}".format(
                'NAME'.rjust(20),
                'ADDRESS'.rjust(15),
                'BOX'.rjust(35),
                'VERSION'.rjust(12),
                'PROVIDER'.rjust(12),
                'STATE'.rjust(12),
            ))

        for name in self.mechfile:
            inst = MechInstance(name, self.mechfile)
            vm_state = "unknown"
            if inst.created:
                ip_address = inst.get_ip()
                vm_state = inst.get_vm_state()
                if vm_state is None:
                    vm_state = "unknown"
                if ip_address is None:
                    ip_address = colored.yellow("poweroff")
                elif not ip_address:
                    ip_address = colored.green("running")
                else:
                    ip_address = colored.green(ip_address)
            else:
                ip_address = "notcreated"
                vm_state = "notcreated"

            if detail:
                print('==================================')
                print('From Mechfile:')
                print(inst)
                print()
                if inst.provider == 'virtualbox':
                    if inst.created:
                        print('From virtualbox:')
                        print(inst.get_vm_info())
            else:
                # deal with box_version being none
                box_version = inst.box_version
                if inst.box_version is None:
                    box_version = ''
                print("{}\t{}\t{}\t{}\t{}\t{}".format(
                    colored.green(name.rjust(20)),
                    ip_address.rjust(15),
                    inst.box.rjust(35),
                    box_version.rjust(12),
                    inst.provider.rjust(12),
                    vm_state.rjust(12),
                ))

    # allow 'mech ls' as alias to 'mech list'
    ls = list
