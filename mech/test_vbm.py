# Copyright (c) 2020 Mike Kinney
"""Tests for VBoxManage class."""
from unittest.mock import patch, MagicMock


import mech.vbm


@patch('subprocess.Popen')
def test_vbm_run(mock_popen):
    """Test run method."""
    process_mock = MagicMock()
    attrs = {'communicate.return_value': ('output', 'error')}
    process_mock.configure_mock(**attrs)
    mock_popen.return_value = process_mock
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=False)
    got = vbm.run('list')
    assert got is None
    mock_popen.assert_called()


@patch('os.path.exists', return_value=True)
def test_vbm_installed(mock_path_exists):
    """Test installed."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage')
    assert vbm.installed()
    mock_path_exists.assert_called()
    assert vbm.get_executable() == '/bin/VBoxManage'


@patch('os.path.exists', return_value=False)
def test_vbm_executable_not_found(mock_path_exists):
    """Test installed."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage')
    assert not vbm.installed()
    mock_path_exists.assert_called()


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


def test_vbm__ip_no_ip():
    """Test _ip method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = None
    with patch.object(mech.vbm.VBoxManage, 'run', return_value='No value set!'):
        got = vbm._ip(vmname='first')
        assert got == expected


def test_vbm__ip():
    """Test _ip method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = '192.168.56.195'
    with patch.object(mech.vbm.VBoxManage, 'run', return_value='Value: 192.168.56.195'):
        got = vbm._ip(vmname='first')
        assert got == expected


def test_vbm_ip_with_wait():
    """Test ip method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = '192.168.56.195'
    with patch.object(mech.vbm.VBoxManage, '_ip', return_value='192.168.56.195'):
        got = vbm.ip(vmname='first', wait=True)
        assert got == expected


def test_vbm_ip_with_no_wait():
    """Test ip method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = '192.168.56.195'
    with patch.object(mech.vbm.VBoxManage, '_ip', return_value='192.168.56.195'):
        got = vbm.ip(vmname='first', wait=False)
        assert got == expected


def test_vbm_start_gui():
    """Test start method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'startvm', 'first', '--type', 'gui']
    got = vbm.start(vmname='first', gui=True)
    assert got == expected


def test_vbm_register():
    """Test register method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'registervm', '/tmp/some.ovf']
    got = vbm.register('/tmp/some.ovf')
    assert got == expected


def test_vbm_unregister():
    """Test unregister method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'unregistervm', 'first']
    got = vbm.unregister('first')
    assert got == expected


def test_vbm_stop():
    """Test stop method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'controlvm', 'first', 'poweroff']
    got = vbm.stop('first')
    assert got == expected


def test_vbm_resume():
    """Test resume method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'controlvm', 'first', 'resume']
    got = vbm.resume('first')
    assert got == expected


def test_vbm_reset():
    """Test reset method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'controlvm', 'first', 'reset']
    got = vbm.reset('first')
    assert got == expected


def test_vbm_pause():
    """Test pause method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'controlvm', 'first', 'pause']
    got = vbm.pause('first')
    assert got == expected


def test_vbm_cpus_using_int():
    """Test cpus method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'modifyvm', 'first', '--cpus', '3']
    got = vbm.cpus('first', 3)
    assert got == expected


def test_vbm_cpus_using_string():
    """Test cpus method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'modifyvm', 'first', '--cpus', '3']
    got = vbm.cpus('first', "3")
    assert got == expected


def test_vbm_memory():
    """Test memory method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'modifyvm', 'first', '--memory', '2048']
    got = vbm.memory('first', 2048)
    assert got == expected


def test_vbm_sharedfolder_add():
    """Test sharedfolder_add method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'sharedfolder', 'add', 'first', '--name',
                'some_share', '--hostpath', '~/foo']
    got = vbm.sharedfolder_add('first', 'some_share', '~/foo')
    assert got == expected


def test_vbm_sharedfolder_remove():
    """Test sharedfolder_remove method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'sharedfolder', 'remove', 'first', '--name',
                'some_share']
    got = vbm.sharedfolder_remove('first', 'some_share')
    assert got == expected


def test_vbm_list_hostonly_ifs():
    """Test list_hostonly_if method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'list', 'hostonlyifs']
    got = vbm.list_hostonly_ifs()
    assert got == expected


def test_vbm_create_hostonly():
    """Test create_hostonly method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = None
    with patch.object(mech.vbm.VBoxManage, 'list_hostonly_ifs', return_value='some output'):
        with patch.object(mech.vbm.VBoxManage, 'list_dhcpservers', return_value='some output'):
            with patch.object(mech.vbm.VBoxManage, 'create_hostonly_if', return_value=None):
                with patch.object(mech.vbm.VBoxManage, 'add_hostonly_dhcp', return_value=None):
                    got = vbm.create_hostonly()
                    assert got == expected


def test_vbm_create_hostonly_if():
    """Test create_hostonly_if method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'hostonlyif', 'create']
    got = vbm.create_hostonly_if()
    assert got == expected


def test_vbm_remove_hostonly_if():
    """Test remove_hostonly_if method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'hostonlyif', 'remove', 'vboxnet0']
    got = vbm.remove_hostonly_if()
    assert got == expected


def test_vbm_add_hostonly_dhcp():
    """Test add_hostonly_dhcp method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'dhcpserver', 'add', '--ifname', 'vboxnet0',
                '--enable', '--ip', '192.168.56.1', '--netmask', '255.255.255.0',
                '--lower-ip', '192.168.56.100', '--upper-ip', '192.168.56.200']
    got = vbm.add_hostonly_dhcp()
    assert got == expected


def test_vbm_remove_hostonly_dhcp():
    """Test remove_hostonly_dhcp method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'dhcpserver', 'remove', '--network',
                'HostInterfaceNetworking-vboxnet0']
    got = vbm.remove_hostonly_dhcp()
    assert got == expected


def test_vbm_list_dhcpservers():
    """Test list_dhcpservers method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'list', 'dhcpservers']
    got = vbm.list_dhcpservers()
    assert got == expected


def test_vbm_hostonly():
    """Test hostonly method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'modifyvm', 'first', '--nic1', 'hostonly',
                '--hostonlyadapter1', 'vboxnet0']
    got = vbm.hostonly('first')
    assert got == expected


def test_vbm_bridged():
    """Test bridged method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'modifyvm', 'first', '--nic1', 'bridged',
                '--bridgeadapter1', 'en0']
    got = vbm.bridged('first')
    assert got == expected


def test_vbm_list():
    """Test list method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'list', 'vms']
    got = vbm.list()
    assert got == expected


def test_vbm_get_vm_info():
    """Test get_vm_info method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    expected = ['/bin/VBoxManage', 'showvminfo', 'first']
    got = vbm.get_vm_info('first')
    assert got == expected


def test_vbm_vm_state_running():
    """Test vm_state method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    output = """VT-x Unrestricted Exec.:     enabled
Paravirt. Provider:          Default
Effective Paravirt. Prov.:   KVM
State:                       running (since 2020-02-28T00:24:40.461000000)
Graphics Controller:         VBoxVGA

Monitor count:               1
"""
    expected = 'running'
    with patch.object(mech.vbm.VBoxManage, 'get_vm_info', return_value=output):
        got = vbm.vm_state('first')
        assert got == expected


def test_vbm_vm_state_unknown():
    """Test vm_state method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    output = None
    expected = None
    with patch.object(mech.vbm.VBoxManage, 'get_vm_info', return_value=output):
        got = vbm.vm_state('first')
        assert got == expected


def test_vbm_vm_state_powered_off():
    """Test vm_state method."""
    vbm = mech.vbm.VBoxManage(executable='/bin/VBoxManage', test_mode=True)
    output = """VT-x Unrestricted Exec.:     enabled
Paravirt. Provider:          Default
Effective Paravirt. Prov.:   KVM
State:                       powered off (since 2020-02-28T00:24:40.461000000)
Graphics Controller:         VBoxVGA

Monitor count:               1
"""
    expected = 'powered off'
    with patch.object(mech.vbm.VBoxManage, 'get_vm_info', return_value=output):
        got = vbm.vm_state('first')
        assert got == expected
