# Copyright (c) 2020 Mike Kinney

"""Tests for VBoxManage class."""

import mech.vbm


def test_vbm_importvm():
    """Test importvm method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'import', '/tmp/first_tmp/some.ovf',
                '--vsys', '0', '--vmname', 'first', '--basefolder', '/tmp/first']
    got = vbm.importvm(path_to_ovf='/tmp/first_tmp/some.ovf',
                       name='first', base_folder='/tmp/first')
    assert got == expected


def test_vbm_start_headless():
    """Test start method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'startvm', 'first', '--type', 'headless']
    got = vbm.start(vmname='first')
    assert got == expected


def test_vbm_start_gui():
    """Test start method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'startvm', 'first', '--type', 'gui']
    got = vbm.start(vmname='first', gui=True)
    assert got == expected
