# v0.8.4

+ This release provides most functionality for virtualbox and vmware
+ Added virtualbox "no-nat" capability (so vm can access internet)
+ Added virtualbox provisioning
+ Added virtualbox integration test
+ Changed "mech ps" to use utils.ssh()
+ Improved "mech list"
+ Removed "mech status" command (see "mech list")
+ Removed "mech reload" command (not really sure what it did)
+ Removed "mech reset" command (did not see need)

# v0.8.3

+ Added initial virtualbox provider; basic functionality ("up", "down",
  "add", "init", "list", "destroy", "ssh", "scp", "ip", "global-status")
  limited to "host only" networking (a "vboxnet0" and a dhcp server is created),
  no provisioning, no shared folders, cannot override cpu/memory;
  added "not implemented yet" messages so it is clear what is implemented;
  changed the output for operations like "start" and "list"
+ Breaking change: boxes will now include the provider ('vmware' or 'virtualbox').
  This will cause boxes to be re-downloaded.

# v0.8.2

+ Add pyinfra provisioning
+ Created new project board: Mech Cloud https://github.com/mkinney/mech/projects/2
+ Created new project board: Mech and VirtualBox https://github.com/mkinney/mech/projects/3
+ Created this CHANGELOG.md file

# v0.8.1

+ First release under mikemech
+ Added unit tests ("pytest")
+ Added static code analysis tools ("flake8" and started fixing "pylint" warnings)
+ Added integration tests
+ Added github workflow
+ Added code coverage visibility (see https://codecov.io/gh/mkinney/mech)
+ Ensure unit and integration tests work from ubunutu and mac
+ Created project board: Mech https://github.com/mkinney/mech/projects/1
+ Added option to remove vagrant user "remove-vagrant"
+ Added option to add current user "add-me"
+ Added option to use current user for mech interactions "use-me"
+ Added option to upgrade vm (bios and virtual hardware)
+ Added option to have multiple shared folders
+ Added option to be able to disable shared folders "disable-shared-folders"
+ Added bash and zsh command completion
+ Added bridged networking ("no-nat")
+ Added ability to change cpus ("numvcpus")
+ Added ability to change memory ("memsize")
+ Added option to have multiple instances of same box
+ Removed delays in code ("sleep()")
+ Refactored code to different classes (ex: MechInstance)
+ Got provisioning working; ensure runs during an instance start
+ Added unit test and code coverage badges in README.md
+ Added the ability to not run provising code during instance start ("no-provision")