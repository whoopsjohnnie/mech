# -*- coding: utf-8 -*-
#
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
"""VBM (virtual box manage) class"""

from __future__ import absolute_import

import os
import sys
import re
import logging
import subprocess
import time

from .compat import b2s
from . import utils


LOGGER = logging.getLogger(__name__)


class VBoxManage():
    """Interface class for the 'VBoxManage' command.
       The 'VBoxManage' command is used to interact with Oracle Virtual Box instances.
       To add/update functionality, run the 'VBoxManage' command with '--help'.
    """

    def __init__(self, executable=None, test_mode=False):
        """Constructor - set sane defaults."""

        self.executable = executable
        self.provider = 'virtualbox'

        if self.executable is None:
            if sys.platform == 'darwin':
                self.executable = utils.get_darwin_executable('VBoxManage')
            elif sys.platform == 'win32':
                # FUTURE: Find out the windows registry/path info
                self.executable = None
            else:
                self.executable = utils.get_fallback_executable('VBoxManage')

        if self.executable is not None:
            LOGGER.debug('self.executable:%s', self.executable)

        # If test_mode is True, then do not perform the action
        # just return the command info
        self.test_mode = test_mode

    def installed(self):
        """Returns True if VB is installed (based on whether
           we could find the VBoxManage command."""
        if self.executable is not None and os.path.exists(self.executable):
            return True
        else:
            return False

    def run(self, cmd, *args, **kwargs):
        """Execute a command."""
        quiet = kwargs.pop('quiet', False)
        arguments = kwargs.pop('arguments', ())

        cmds = [self.executable]
        cmds.append(cmd)
        cmds.extend(filter(None, args))
        cmds.extend(filter(None, arguments))

        LOGGER.debug(
            " ".join(
                "'{}'".format(
                    c.replace(
                        "'",
                        "\\'")) if ' ' in c else c for c in cmds))

        if self.test_mode:
            return cmds

        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(
            cmds,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo)
        stdoutdata, stderrdata = map(b2s, proc.communicate())

        if stderrdata and not quiet:
            LOGGER.error(stderrdata.strip())
        LOGGER.debug("(⏎ %s)", proc.returncode)

        if not proc.returncode:
            stdoutdata = stdoutdata.strip()
            LOGGER.debug(repr(stdoutdata))
            return stdoutdata

        if stdoutdata and not quiet:
            LOGGER.error(stdoutdata.strip())

    ############################################################################
    # startvm               <uuid|vmname>...
    #                       [--type gui|headless|separate]
    # registervm            <filename>
    # unregistervm          <uuid|vmname> [--delete]
    # import                <ovfname/ovaname>
    #                       [--dry-run|-n]
    #                       [--options keepallmacs|keepnatmacs|importtovdi]
    #                       [--vmname <name>]
    #                       [--cloud]
    #                       [--cloudprofile <cloud profile name>]
    #                       [--cloudinstanceid <instance id>]
    #                       [--cloudbucket <bucket name>]
    #                       [more options]
    #                       (run with -n to have options displayed
    #                        for a particular OVF. It doesn't work for the Cloud import.)

    def start(self, vmname, gui=False, quiet=False):
        '''Start a VM'''
        return self.run('startvm', vmname, '--type', 'gui' if gui else 'headless', quiet=quiet)

    def importvm(self, path_to_ovf, name, base_folder, quiet=False):
        '''Import a VM (import ovf/ova).
           Note: Did not want to use 'import' as that could clash with python's "import".
           Tip: Do not have spaces in the options, make them be a separate argument.
                (ex: For the argument "--vsys 0" option, use: '--vsys', '0')
        '''
        return self.run('import', path_to_ovf, '--vsys', '0', '--vmname', name,
                        '--basefolder', base_folder, quiet=quiet)

    def _ip(self, vmname, quiet=False):
        """Get ip address of VM."""
        line = self.run('guestproperty', 'get', vmname,
                        '/VirtualBox/GuestInfo/Net/0/V4/IP', quiet=False)
        if line and line != 'No value set!':
            parts = line.split()
            if len(parts) > 1:
                return parts[1]

    def ip(self, vmname, wait=False, quiet=False):
        """Get ip address of VM.
        """
        ip_address = self._ip(vmname, quiet=quiet)
        if wait:
            while True:
                ip_address = self._ip(vmname, quiet=quiet)
                if ip_address:
                    return ip_address
                time.sleep(1)
        else:
            return ip_address

    def register(self, filename, quiet=False):
        '''Register a VM.
           Note: Probably want to use importvm().
        '''
        return self.run('registervm', filename, quiet=quiet)

    def unregister(self, vmname, quiet=False):
        '''Unregister a VM (similar to destroy)'''
        return self.run('unregistervm', vmname, quiet=quiet)

    # controlvm                 <uuid|vmname>
    #                       pause|resume|reset|poweroff|savestate|
    #                          ...snip...

    def stop(self, vmname, quiet=False):
        '''Stop a VM'''
        return self.run('controlvm', vmname, 'poweroff', quiet=quiet)

    def resume(self, vmname, quiet=False):
        '''Resume a VM'''
        return self.run('controlvm', vmname, 'resume', quiet=quiet)

    def reset(self, vmname, quiet=False):
        '''Reset a VM'''
        return self.run('controlvm', vmname, 'reset', quiet=quiet)

    def pause(self, vmname, quiet=False):
        '''Pause a VM'''
        return self.run('controlvm', vmname, 'pause', quiet=quiet)

    def cpus(self, vmname, num_cpus, quiet=False):
        '''Changes VM to have num_cpus.
           Note: VM must be stopped.
        '''
        return self.run('modifyvm', vmname,
                        '--cpus', '{}'.format(num_cpus), quiet=quiet)

    def memory(self, vmname, memory_in_mb, quiet=False):
        '''Changes VM to have memory_in_mb.
           Note: VM must be stopped.
        '''
        return self.run('modifyvm', vmname,
                        '--memory', '{}'.format(memory_in_mb), quiet=quiet)

    def sharedfolder_add(self, vmname, share_name, host_path, quiet=False):
        '''Add a shared folder'''
        return self.run('sharedfolder', 'add', vmname,
                        '--name', share_name, '--hostpath', host_path, quiet=quiet)

    def sharedfolder_remove(self, vmname, share_name, quiet=False):
        '''Remove a shared folder'''
        return self.run('sharedfolder', 'remove', vmname,
                        '--name', share_name, quiet=quiet)

    def list_hostonly_ifs(self, quiet=False):
        '''List hostonly interfaces.'''
        return self.run('list', 'hostonlyifs', quiet=quiet)

    def create_hostonly(self, quiet=False):
        '''Create the stuff needed for hostonly networking to work.'''
        ifs = self.list_hostonly_ifs()
        if re.search(r'vboxnet', ifs, re.MULTILINE) is None:
            self.create_hostonly_if(quiet=quiet)
        ds = self.list_dhcpservers(quiet=quiet)
        if re.search(r'vboxnet', ds, re.MULTILINE) is None:
            self.add_hostonly_dhcp(quiet=quiet)

    def create_hostonly_if(self, quiet=False):
        '''Create hostonly interface (creates vboxnet0)'''
        return self.run('hostonlyif', 'create', quiet=quiet)

    def remove_hostonly_if(self, host_interface='vboxnet0', quiet=False):
        '''Remove hostonly interface (creates vboxnet0)'''
        return self.run('hostonlyif', 'remove', host_interface, quiet=quiet)

    def add_hostonly_dhcp(self, host_interface='vboxnet0', quiet=False):
        '''Create dhcp on host interface (ex: vboxnet0).'''
        return self.run('dhcpserver', 'add', '--ifname', host_interface,
                        '--enable', '--ip', '192.168.56.1', '--netmask', '255.255.255.0',
                        '--lower-ip', '192.168.56.100', '--upper-ip', '192.168.56.200',
                        quiet=quiet)

    def remove_hostonly_dhcp(self, network_name='HostInterfaceNetworking-vboxnet0', quiet=False):
        '''Remove dhcp network.'''
        return self.run('dhcpserver', 'remove', '--network', network_name, quiet=quiet)

    def list_dhcpservers(self, quiet=False):
        '''List dhcpservers.'''
        return self.run('list', 'dhcpservers', quiet=quiet)

    def hostonly(self, vmname, quiet=False):
        '''Make a VM use hostonly networking.
           Note: The VM will not be able to access the internet.
        '''
        return self.run('modifyvm', vmname, '--nic1', 'hostonly',
                        '--hostonlyadapter1', 'vboxnet0', quiet=quiet)

    def bridged(self, vmname, bridge_adapter='en0', quiet=False):
        '''Make a VM use bridged networking.
           Note: Will get an IP from network DHCP server.
                 Should be able to access internet.
        '''
        return self.run('modifyvm', vmname, '--nic1', 'bridged', '--bridgeadapter1',
                        bridge_adapter, quiet=quiet)

    ############################################################################
    # list [--long|-l] [--sorted|-s]          vms|runningvms|ostypes|hostdvds|hostfloppies|
    #                       intnets|bridgedifs|hostonlyifs|natnets|dhcpservers|
    #                       hostinfo|hostcpuids|hddbackends|hdds|dvds|floppies|
    #                       usbhost|usbfilters|systemproperties|extpacks|
    #                       groups|webcams|screenshotformats|cloudproviders|
    #                       cloudprofiles

    def list(self, quiet=False):
        '''List all VMs'''
        return self.run('list', 'vms', quiet=quiet)

    def get_vm_info(self, vmname, quiet=False):
        '''Return the show VM info'''
        return self.run('showvminfo', vmname, quiet=quiet)

    def vm_state(self, vmname, quiet=False):
        '''Return the first word from the showvminfo output line that starts with "State:".'''
        vm_info = self.get_vm_info(vmname, quiet=quiet)
        matches = re.search(r'State:(.*)\(', vm_info)
        if matches:
            return matches.group(1).strip()

    def list_running(self, quiet=False):
        '''List all running VMs'''
        running_vms = []
        output = self.run('list', 'runningvms', quiet=quiet)
        each_line = output.split('\n')
        LOGGER.debug('each_line:%s', each_line)
        for line in each_line:
            LOGGER.debug('line:%s', line)
            parts = line.split(' ')
            if len(parts) > 0:
                running_vms.append(parts[0].replace('"', ''))
        LOGGER.debug('running_vms:%s', running_vms)
        return running_vms
