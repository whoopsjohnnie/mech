from .mech import cli
from .mech_box import box
from .mech_cloud import cloud
from .mech_snapshot import snapshot
from .mech_winrm import winrm


cli.add_command(box)
cli.add_command(cloud)
cli.add_command(snapshot)
cli.add_command(winrm)


if __name__ == '__main__':
    cli()
