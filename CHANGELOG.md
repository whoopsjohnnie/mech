# TBD

+ Breaking change: boxes will now include the provider ('vmware' or 'virtualbox'). This may
  cause boxes to be re-downloaded.

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
