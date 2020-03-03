# mech

![Python package](https://github.com/mkinney/mech/workflows/Python%20package/badge.svg)
[![codecov](https://codecov.io/gh/mkinney/mech/branch/master/graph/badge.svg)](https://codecov.io/gh/mkinney/mech)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mikemech)

Please test and provide any feedback/issues.

*Newly added virtualbox functionality.* By default, the provider will be `vmware`.

Did you know you can now *provision* using `pyinfra`? See `mech provision --help` for more info.

*Newly added `mech cloud` capability.* See `mech cloud --help` for more info.

There is `--help` on every operation.

# mech --help
```
    Usage: mech [options] <command> [<args>...]

    Notes:
        "mech" provides an easy way to control virtual machines.
        An "instance" is a virtual machine.

    Options:
        -v, --version                    Print the version and exit.
        -h, --help                       Print this help.
        --debug                          Show debug messages.

    Common commands:
        box               manages boxes: add, list remove, etc.
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
        support           Print info helpful with support
        suspend           suspends the instance(s)
        (up|start)        starts instance(s)
        upgrade           upgrade the instance(s) - vmware only
        winrm             winrm options: config, copy, fetch, run

    For help on any individual command run `mech <command> -h`

    All "state" will be saved in .mech directory. (boxes and instances)

    Examples:

    Initializing and using a box from HashiCorp's Vagrant Cloud:

        mech init bento/ubuntu-18.04
        mech up
        mech ssh

    Having a problem with a command, add the "--debug" option like this:

        mech --debug up
```

# mech up --help
```
% mech up --help
        Starts and provisions the mech environment.

        Usage: mech up [options] [<instance>]

        Notes:
           - If no instance is specified, all instances will be started.
           - The options (memsize, numvcpus, and no-nat) will only be applied
             upon first run of the 'up' command.
           - The 'no-nat' option will only be applied if there is no network
             interface supplied in the box file for 'vmware'. For 'virtualbox',
             if you need internet access from the vm, then you will want to
             use 'no-nat'.
           - Will try these interfaces for the bridge when using 'no-nat':
                'en0', 'eno1', 'eth0', 'enp5s0'
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
```

# Example using mech

Initializing and using a machine from HashiCorp's Vagrant Cloud:

```
    mech init bento/ubuntu-18.04
    mech up
    mech ssh
```

`mech init` can be used to pull a box file which will be installed and
generate a Mechfile in the current directory. You can also pull boxes
from Vagrant Cloud with `mech init freebsd/FreeBSD-11.1-RELEASE`.
See the `mech up -h` page for more information.

Can have multiple instances of the same box. The default instance name is 'first'.

Here is the help info for adding a new instance:

# mech add --help
```
% mech add -h

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
```

# mech list
Here is what it would look like having multiple instance with different providers:
```
% mech list
                NAME	        ADDRESS	                                BOX	     VERSION	    PROVIDER	       STATE
               first	  192.168.3.134	                 bento/ubuntu-18.04	 201912.04.0	      vmware	     started
              second	 192.168.56.194	                 bento/ubuntu-18.04	 202002.04.0	  virtualbox	     running
               third	     notcreated	              mrlesmithjr/alpine311	  1578437753	  virtualbox	  notcreated
```

# Installation

To install:

`pip install -U mikemech`

or for the latest:

`pip install -U git+https://github.com/mkinney/mech.git`

# Shared Folders

If the box you init was created properly, you will be able to access
the host's current working directory in `/mnt/hgfs/mech`. If you are
having trouble with an Ubuntu guest, try running:

```bash
sudo apt-get update
sudo apt-get install linux-headers-$(uname -r) open-vm-tools
```

followed by

```bash
sudo vmware-config-tools.pl
```

or

```bash
vmhgfs-fuse .host:/mech /mnt/hgfs
```

# Want zsh completion for commands/options (aka "tab completion")?
1. add these lines to ~/.zshrc

```bash
# folder of all of your autocomplete functions
fpath=($HOME/.zsh-completions $fpath)
# enable autocomplete function
autoload -U compinit
compinit
```

2. Copy script to something in fpath (Note: Run `echo $fpath` to show value.)

```bash
cp _mech ~/.zsh-completions/
```

3. Reload zsh

```bash
exec zsh
```

4. Try it out by typing `mech <tab>`. It should show the options available.

# Want bash completion for commands/options (aka "tab completion")?
1. add these lines to ~/.bash_profile

```bash
[ -f /usr/local/etc/bash_completion ] && . /usr/local/etc/bash_completion
```

2. Copy script to path above

```bash
cp mech_completion.sh /usr/local/etc/bash_completion/
```

3. Reload .bash_profile

```bash
source ~/.bash_profile
```

4. Try it out by typing `mech <tab>`. It should show the options available.

# Background

One of the authors made this because they don't like VirtualBox and wanted to use vagrant
with VMmare Fusion but was too cheap to buy the Vagrant plugin.

https://blog.kchung.co/mech-vagrant-with-vmware-integration-for-free/

