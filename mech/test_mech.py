# Copyright (c) 2020 Mike Kinney

"""mech tests"""
import os
import re

from unittest.mock import patch, mock_open, MagicMock
from pytest import raises

import mech.command
import mech.mech
import mech.vmrun
import mech.mech_instance


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_list_with_one(mock_locate, mock_load_mechfile, capfd,
                            mechfile_one_entry):
    """Test 'mech list' with one entry."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    list_arguments = {'--detail': False}
    a_mech.list(list_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'first\s+notcreated', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_list_with_one_witout_box_version(mock_locate, mock_load_mechfile, capfd,
                                               mechfile_one_entry_without_box_version):
    """Test 'mech list' with one entry."""
    mock_load_mechfile.return_value = mechfile_one_entry_without_box_version
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    list_arguments = {'--detail': False}
    a_mech.list(list_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'first\s+notcreated', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_list_with_one_and_debug(mock_locate, mock_load_mechfile, capfd,
                                      mechfile_one_entry):
    """Test 'mech list' with one entry."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': True, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    list_arguments = {'--detail': True}
    a_mech.list(list_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'created:False', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_list_with_two_not_created(mock_locate, mock_load_mechfile, capfd,
                                        mechfile_two_entries):
    """Test 'mech list' with two entries."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    list_arguments = {'--detail': False}
    a_mech.list(list_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'first\s+notcreated', out, re.MULTILINE)
    assert re.search(r'second\s+notcreated', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_list_powered_on(mock_locate, mock_load_mechfile,
                              capfd,
                              mechfile_two_entries):
    """Test 'mech list' powered on."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {'<instance>': 'first', '--detail': None}
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        a_mech.list(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_get_ip.assert_called()
        assert re.search(r'192.168.', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_list_powered_on_cannot_get_ip(mock_locate, mock_load_mechfile,
                                            capfd, mechfile_two_entries):
    """Test 'mech list' powered on."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {'<instance>': 'first', '--detail': None}
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value=False) as mock_get_ip:
        a_mech.list(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_get_ip.assert_called()
        assert re.search(r'running', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_list_powered_off(mock_locate, mock_load_mechfile,
                               capfd, mechfile_two_entries):
    """Test 'mech list' powered off."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {'<instance>': 'first', '--detail': None}
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value=None) as mock_get_ip:
        a_mech.list(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_get_ip.assert_called()
        assert re.search(r'poweroff', out, re.MULTILINE)


@patch('mech.utils.get_provider', return_value=None)
@patch('os.path.exists', return_value=True)
@patch('shutil.rmtree')
@patch('mech.vmrun.VMrun.delete_vm')
@patch('mech.vmrun.VMrun.stop', return_value=True)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_destroy(mock_locate, mock_load_mechfile,
                      mock_vmrun_stop, mock_vmrun_delete_vm,
                      mock_rmtree, mock_path_exists, mock_get_provider,
                      capfd, mechfile_two_entries):
    """Test 'mech destroy' powered on."""
    mock_load_mechfile.return_value = mechfile_two_entries
    mock_rmtree.return_value = True
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--force': True,
    }
    a_mech.destroy(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_stop.assert_called()
    mock_get_provider.assert_called()
    mock_vmrun_delete_vm.assert_called()
    mock_rmtree.assert_called()
    mock_path_exists.assert_called()
    assert re.search(r'Deleting', out, re.MULTILINE)
    assert re.search(r'Deleted', out, re.MULTILINE)


@patch('os.path.exists', return_value=True)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_destroy_prompted_and_answered_no(mock_locate, mock_load_mechfile,
                                               mock_path_exists,
                                               capfd, mechfile_two_entries):
    """Test 'mech destroy' powered on."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--force': False,
    }
    a_mock = MagicMock()
    a_mock.return_value = 'N'
    with patch('mech.utils.raw_input', a_mock):
        a_mech.destroy(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_path_exists.assert_called()
        assert re.search(r'Delete aborted', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_destroy_not_created(mock_locate, mock_load_mechfile,
                                  capfd, mechfile_two_entries):
    """Test 'mech destroy' not created."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': None,
        '--force': True,
    }
    a_mech.destroy(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'not created', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.installed_tools', return_value='running')
@patch('mech.vmrun.VMrun.stop', return_value=True)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_down(mock_locate, mock_load_mechfile,
                   mock_vmrun_stop, mock_installed_tools,
                   capfd, mechfile_two_entries):
    """Test 'mech down' powered on."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--force': None,
    }
    a_mech.down(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_stop.assert_called()
    mock_installed_tools.assert_called()
    assert re.search(r'Stopped', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.installed_tools', return_value=False)
@patch('mech.vmrun.VMrun.stop', return_value=None)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_down_no_vmware_tools_and_stopped_fails(mock_locate, mock_load_mechfile,
                                                     mock_vmrun_stop, mock_installed_tools,
                                                     capfd, mechfile_two_entries):
    """Test 'mech down' powered on."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--force': None,
    }
    a_mech.down(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_stop.assert_called()
    mock_installed_tools.assert_called()
    assert re.search(r'Not stopped', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_down_not_created(mock_locate, mock_load_mechfile,
                               capfd, mechfile_two_entries):
    """Test 'mech down' not created."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': None,
        '--force': None,
    }
    a_mech.down(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r' not created', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_ip(mock_locate, mock_load_mechfile,
                 capfd, mechfile_two_entries):
    """Test 'mech ip' powered on."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
    }
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        a_mech.ip(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_get_ip.assert_called()
        mock_get_ip.assert_called()
        assert re.search(r'192.168', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_ip_unknown(mock_locate, mock_load_mechfile,
                         capfd, mechfile_two_entries):
    """Test 'mech ip' but cannot get ip address."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
    }
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value=None) as mock_get_ip:
        a_mech.ip(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_get_ip.assert_called()
        assert re.search(r'Unknown', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_ip_not_created(mock_locate, mock_load_mechfile,
                             capfd, mechfile_two_entries):
    """Test 'mech ip' not created."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
    }
    a_mech.ip(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'VM not created', out, re.MULTILINE)


MECHFILE_WITH_PROVISIONING = {
    "first": {
        "box": "mrlesmithjr/alpine311",
        "box_version": "1578437753",
        "name": "first",
        "url": "https://vagrantcloud.com/mrlesmithjr/boxes/alpine311/\
versions/1578437753/providers/vmware_desktop.box",
        "provision": [
            {
                "type": "file",
                "source": "file1.txt",
                "destination": "/tmp/file1.txt"
            },
            {
                "type": "file",
                "source": "file2.txt",
                "destination": "/tmp/file2.txt"
            }
        ]
    },
    "second": {
        "box": "mrlesmithjr/alpine311",
        "box_version": "1578437753",
        "name": "second",
        "url": "https://vagrantcloud.com/mrlesmithjr/boxes/alpine311/\
versions/1578437753/providers/vmware_desktop.box",
        "provision": [
            {
                "type": "shell",
                "path": "file1.sh",
                "args": [
                    "a=1",
                    "b=true"
                ]
            },
            {
                "type": "shell",
                "path": "file2.sh",
                "args": []
            },
            {
                "type": "shell",
                "inline": "echo hello from inline"
            }
        ]
    },
    "third": {
        "box": "mrlesmithjr/alpine311",
        "box_version": "1578437753",
        "name": "third",
        "url": "https://vagrantcloud.com/mrlesmithjr/boxes/alpine311/\
    versions/1578437753/providers/vmware_desktop.box",
        "provision": []
    },
    "fourth": {
        "box": "mrlesmithjr/alpine311",
        "box_version": "1578437753",
        "name": "second",
        "url": "https://vagrantcloud.com/mrlesmithjr/boxes/alpine311/\
versions/1578437753/providers/vmware_desktop.box",
        "provision": [
            {
                "type": "pyinfra",
                "path": "file1.py",
                "args": [
                    "a=1",
                    "b=true"
                ]
            }
        ]
    },
}
@patch('mech.utils.provision_file', return_value=True)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_WITH_PROVISIONING)
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_provision_file(mock_locate, mock_load_mechfile,
                             mock_provision_file, capfd):
    """Test 'mech provision' (using file provisioning)."""
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--show-only': None,
    }
    a_mech.provision(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_provision_file.assert_called()
    assert re.search(r' Provision ', out, re.MULTILINE)


@patch('mech.utils.load_mechfile', return_value=MECHFILE_WITH_PROVISIONING)
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_provision_with_pyinfra_show(mock_locate, mock_load_mechfile,
                                          capfd):
    """Test 'mech provision' (using file provisioning)."""
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'fourth',
        '--show-only': True,
    }
    a_mech.provision(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r' Provision ', out, re.MULTILINE)
    assert re.search(r'file1.py', out, re.MULTILINE)


@patch('mech.utils.provision_pyinfra', return_value=(None, None, None))
@patch('mech.utils.load_mechfile', return_value=MECHFILE_WITH_PROVISIONING)
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_provision_with_pyinfra_fails(mock_locate, mock_load_mechfile,
                                           mock_provision_pyinfra, capfd):
    """Test 'mech provision' (using file provisioning)."""
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'fourth',
        '--show-only': False,
    }
    a_mech.provision(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_provision_pyinfra.assert_called()
    assert re.search(r'Not Provisioned', out, re.MULTILINE)


@patch('mech.utils.load_mechfile', return_value=MECHFILE_WITH_PROVISIONING)
@patch('mech.utils.locate', return_value=None)
def test_mech_provision_not_started(mock_locate, mock_load_mechfile, capfd):
    """Test 'mech provision' (using file provisioning)."""
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': None,
        '--show-only': None,
    }
    a_mech.provision(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'VM not created', out, re.MULTILINE)


@patch('mech.utils.provision_shell', return_value=True)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_WITH_PROVISIONING)
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_provision_shell(mock_locate, mock_load_mechfile,
                              mock_provision_shell, capfd):
    """Test 'mech provision' (using shell provisioning)."""
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'second',
        '--show-only': None,
    }
    a_mech.provision(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_provision_shell.assert_called()
    assert re.search(r' Provision ', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.suspend', return_value=True)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_suspend(mock_locate, mock_load_mechfile,
                      mock_vmrun_suspend, capfd, mechfile_two_entries):
    """Test 'mech suspend' powered on."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
    }
    a_mech.suspend(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_suspend.assert_called()
    assert re.search(r'Suspended', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.suspend', return_value=None)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_suspend_fails(mock_locate, mock_load_mechfile,
                            mock_vmrun_suspend, capfd, mechfile_two_entries):
    """Test 'mech suspend' powered on."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
    }
    a_mech.suspend(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_suspend.assert_called()
    assert re.search(r'Not suspended', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_suspend_not_created(mock_locate, mock_load_mechfile,
                                  capfd, mechfile_two_entries):
    """Test 'mech suspend' not created."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': None,
    }
    a_mech.suspend(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'VM has not been created', out, re.MULTILINE)


@patch('os.chmod', return_value=True)
@patch('mech.vmrun.VMrun.installed_tools', return_value='running')
@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value="192.168.4.130")
@patch('subprocess.run')
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_ssh(mock_locate, mock_load_mechfile,
                  mock_subprocess_run, mock_get_ip, mock_installed_tools,
                  mock_chmod, mechfile_two_entries):
    """Test 'mech ssh'"""
    mock_load_mechfile.return_value = mechfile_two_entries
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.stdout = b'00:03:30 up 2 min,  load average: 0.00, 0.00, 0.00\n'
    mock_subprocess_run.stderr = b''
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--plain': None,
        '--command': 'uptime',
        '<extra-ssh-args>': 'blah',
    }
    filename = os.path.join(mech.utils.mech_dir(), 'insecure_private_key')
    a_mock = mock_open()
    with raises(SystemExit):
        with patch('builtins.open', a_mock, create=True):
            a_mech.ssh(arguments)
            mock_locate.assert_called()
            mock_load_mechfile.assert_called()
            mock_subprocess_run.assert_called()
            mock_installed_tools.assert_called()
            mock_get_ip.assert_called()
            mock_chmod.assert_called()
            a_mock.assert_called_once_with(filename, 'w')


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_ssh_not_created(mock_locate, mock_load_mechfile,
                              mechfile_two_entries, capfd):
    """Test 'mech ssh'"""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--plain': None,
        '--command': 'uptime',
        '<extra-ssh-args>': None,
    }
    a_mech.ssh(arguments)
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    out, _ = capfd.readouterr()
    assert re.search(r'VM not created', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.pause', return_value=True)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_pause(mock_locate, mock_load_mechfile,
                    mock_vmrun_pause, capfd, mechfile_two_entries):
    """Test 'mech pause' powered on."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--force': None,
    }
    a_mech.pause(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_pause.assert_called()
    assert re.search(r'Paused', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.pause', return_value=None)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_pause_not_paused(mock_locate, mock_load_mechfile,
                               mock_vmrun_pause, capfd, mechfile_two_entries):
    """Test 'mech pause' powered on."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--force': None,
    }
    a_mech.pause(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_pause.assert_called()
    assert re.search(r'Not paused', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_pause_not_created(mock_locate, mock_load_mechfile,
                                capfd, mechfile_two_entries):
    """Test 'mech pause' not created."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': None,
        '--force': None,
    }
    a_mech.pause(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r' not created', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.upgradevm', return_value=None)
@patch('mech.vmrun.VMrun.check_tools_state', return_value=False)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_upgrade_created_powered_off_upgrade_fails(mock_locate, mock_load_mechfile,
                                                        mock_check_tools_state,
                                                        mock_vmrun_upgradevm,
                                                        capfd, mechfile_two_entries):
    """Test 'mech upgrade' with vm created and powered off."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--force': None,
    }
    a_mech.upgrade(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_check_tools_state.assert_called()
    mock_vmrun_upgradevm.assert_called()
    assert re.search(r'Not upgraded', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.upgradevm', return_value='')
@patch('mech.vmrun.VMrun.check_tools_state', return_value=False)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_upgrade_created_powered_off_upgrade_works(mock_locate, mock_load_mechfile,
                                                        mock_check_tools_state,
                                                        mock_vmrun_upgradevm,
                                                        capfd, mechfile_two_entries):
    """Test 'mech upgrade' with vm created and powered off."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--force': None,
    }
    a_mech.upgrade(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_check_tools_state.assert_called()
    mock_vmrun_upgradevm.assert_called()
    assert re.search(r'Upgraded', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.check_tools_state', return_value="running")
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_upgrade_created__powered_on(mock_locate, mock_load_mechfile,
                                          mock_check_tools_state,
                                          capfd, mechfile_two_entries):
    """Test 'mech upgrade' with vm created and powered on."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--force': None,
    }
    a_mech.upgrade(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_check_tools_state.assert_called()
    assert re.search(r'VM must be stopped', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_upgrade_not_created(mock_locate, mock_load_mechfile,
                                  capfd, mechfile_two_entries):
    """Test 'mech upgrade' not created."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': None,
        '--force': None,
    }
    a_mech.upgrade(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r' not created', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.disable_shared_folders', return_value=True)
@patch('mech.vmrun.VMrun.unpause', return_value=True)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_resume(mock_locate, mock_load_mechfile,
                     mock_vmrun_unpause,
                     mock_vmrun_disable_shared_folders, capfd, mechfile_two_entries):
    """Test 'mech resume'."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--disable-shared-folders': True,
        '--force': True,
    }
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value='192.168.1.101') as mock_get_ip:
        a_mech.resume(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_vmrun_unpause.assert_called()
        mock_vmrun_disable_shared_folders.assert_called()
        mock_get_ip.assert_called()
        assert re.search(r'resumed', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.disable_shared_folders', return_value=True)
@patch('mech.vmrun.VMrun.unpause', return_value=True)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_resume_unknown_ip(mock_locate, mock_load_mechfile,
                                mock_vmrun_unpause,
                                mock_vmrun_disable_shared_folders, capfd, mechfile_two_entries):
    """Test 'mech resume'."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--disable-shared-folders': True,
        '--force': True,
    }
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value=None) as mock_get_ip:
        a_mech.resume(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_vmrun_unpause.assert_called()
        mock_vmrun_disable_shared_folders.assert_called()
        mock_get_ip.assert_called()
        assert re.search(r'resumed', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_resume_not_created(mock_locate, mock_load_mechfile,
                                 capfd, mechfile_two_entries):
    """Test 'mech resume'."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--disable-shared-folders': True,
        '--force': True,
    }
    a_mech.resume(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'VM not created', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.start', return_value=None)
@patch('mech.vmrun.VMrun.unpause', return_value=None)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_resume_unpause_unsuccessful_start_fails(mock_locate, mock_load_mechfile,
                                                      mock_vmrun_unpause,
                                                      mock_vmrun_start,
                                                      capfd, mechfile_two_entries):
    """Test 'mech resume'."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--disable-shared-folders': True,
        '--force': True,
    }
    a_mech.resume(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_unpause.assert_called()
    mock_vmrun_start.assert_called()
    assert re.search(r'VM not started', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.add_shared_folder', return_value=True)
@patch('mech.vmrun.VMrun.enable_shared_folders', return_value=True)
@patch('mech.vmrun.VMrun.unpause', return_value=True)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_resume_shared_folders(mock_locate, mock_load_mechfile,
                                    mock_vmrun_unpause,
                                    mock_enable_shared_folders, mock_add_shared_folder,
                                    capfd, mechfile_two_entries):
    """Test 'mech resume'."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': None,
        '--disable-shared-folders': False,
        '--force': True,
    }
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value='192.168.1.101') as mock_get_ip:
        a_mech.resume(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_vmrun_unpause.assert_called()
        mock_enable_shared_folders.assert_called()
        mock_add_shared_folder.assert_called()
        mock_get_ip.assert_called()
        assert re.search(r'Sharing folders', out, re.MULTILINE)
        assert re.search(r'resumed', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.add_shared_folder', return_value=True)
@patch('mech.vmrun.VMrun.enable_shared_folders', return_value=True)
@patch('mech.vmrun.VMrun.start', return_value=True)
@patch('mech.vmrun.VMrun.unpause', return_value=None)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_resume_unpause_fails_starts_successfully_with_shared_folders(
        mock_locate, mock_load_mechfile, mock_vmrun_unpause, mock_vmrun_start,
        mock_enable_shared_folders, mock_add_shared_folder,
        capfd, mechfile_two_entries):
    """Test 'mech resume'."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--disable-shared-folders': False,
        '--force': True,
    }
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value='192.168.1.101') as mock_get_ip:
        a_mech.resume(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_vmrun_unpause.assert_called()
        mock_vmrun_start.assert_called()
        mock_enable_shared_folders.assert_called()
        mock_add_shared_folder.assert_called()
        mock_get_ip.assert_called()
        assert re.search(r'Sharing folders', out, re.MULTILINE)
        assert re.search(r'started', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.start', return_value=True)
@patch('mech.vmrun.VMrun.unpause', return_value=None)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_resume_unpause_fails_starts_successfully_unknown_ip(
        mock_locate, mock_load_mechfile, mock_vmrun_unpause, mock_vmrun_start,
        capfd, mechfile_two_entries):
    """Test 'mech resume'."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--disable-shared-folders': True,
        '--force': True,
    }
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value=None) as mock_get_ip:
        a_mech.resume(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_vmrun_unpause.assert_called()
        mock_vmrun_start.assert_called()
        mock_get_ip.assert_called()
        assert re.search(r'started on an unknown', out, re.MULTILINE)


MECHFILE_BAD_ENTRY = {
    '': {
        'name':
        '',
        'box':
        'bento/ubuntu-18.04',
        'box_version':
        '201912.04.0'
    }
}
@patch('mech.utils.load_mechfile')
def test_mech_up_without_name(mock_load_mechfile):
    """Test 'mech up' (overriding name to be '') to test exception."""
    mock_load_mechfile.return_value = MECHFILE_BAD_ENTRY
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--detail': False,
        '--gui': False,
        '--disable-shared-folders': False,
        '--disable-provisioning': False,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '--no-nat': None,
        '--remove-vagrant': None,
        '<instance>': '',
    }
    with raises(AttributeError, match=r"Must provide a name for the instance."):
        a_mech.up(arguments)


@patch('mech.utils.load_mechfile')
def test_mech_up_with_name_not_in_mechfile(mock_load_mechfile,
                                           mechfile_one_entry):
    """Test 'mech up' with a name that is not in the Mechfile."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--detail': False,
        '--gui': False,
        '--disable-shared-folders': False,
        '--disable-provisioning': False,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '--no-nat': None,
        '--remove-vagrant': None,
        '<instance>': 'notfirst',
    }
    with raises(SystemExit, match=r" was not found in the Mechfile"):
        a_mech.up(arguments)


@patch('mech.utils.del_user', return_value='')
@patch('mech.vmrun.VMrun.start', return_value='')
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
def test_mech_up_already_started(mock_locate, mock_load_mechfile,
                                 mock_vmrun_start,
                                 mock_del_user, capfd,
                                 mechfile_one_entry):
    """Test 'mech up'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--gui': False,
        '--disable-shared-folders': True,
        '--disable-provisioning': True,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '--no-nat': None,
        '--remove-vagrant': True,
        '<instance>': None,
    }
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        a_mech.up(arguments)
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_vmrun_start.assert_called()
        mock_get_ip.assert_called()
        mock_del_user.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'started', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.run_script_in_guest', return_value='')
@patch('mech.vmrun.VMrun.installed_tools', return_value='running')
@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value="192.168.1.100")
@patch('mech.vmrun.VMrun.start', return_value='')
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
def test_mech_up_already_started_with_add_me(mock_locate, mock_load_mechfile,
                                             mock_vmrun_start, mock_vmrun_get_ip,
                                             mock_installed_tools,
                                             mock_run_script_in_guest, capfd,
                                             mechfile_one_entry_with_auth):
    """Test 'mech up'."""
    mock_load_mechfile.return_value = mechfile_one_entry_with_auth
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--gui': False,
        '--disable-shared-folders': True,
        '--disable-provisioning': True,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '--no-nat': None,
        '--remove-vagrant': None,
        '<instance>': None,
    }
    mock_file = mock_open(read_data='some_pub_key_data')
    with patch('builtins.open', mock_file, create=True):
        a_mech.up(arguments)
        mock_file.assert_called()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_vmrun_start.assert_called()
        mock_installed_tools.assert_called()
        mock_run_script_in_guest.assert_called()
        mock_vmrun_get_ip.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'started', out, re.MULTILINE)
        assert re.search(r'Added auth', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.start', return_value='')
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
def test_mech_up_already_started_but_could_not_get_ip(mock_locate, mock_load_mechfile,
                                                      mock_vmrun_start,
                                                      capfd, mechfile_one_entry):
    """Test 'mech up'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--gui': False,
        '--disable-shared-folders': True,
        '--disable-provisioning': True,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '--no-nat': None,
        '--remove-vagrant': None,
        '<instance>': None,
    }
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value='') as mock_get_ip:
        a_mech.up(arguments)
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_vmrun_start.assert_called()
        mock_get_ip.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'started on an unknown', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.start', return_value=True)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
def test_mech_up_already_started_but_on_unknnown_ip(mock_locate, mock_load_mechfile,
                                                    mock_vmrun_start, capfd,
                                                    mechfile_one_entry):
    """Test 'mech up'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--gui': False,
        '--disable-shared-folders': True,
        '--disable-provisioning': True,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '--no-nat': None,
        '--remove-vagrant': None,
        '<instance>': None,
    }
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value=False) as mock_get_ip:
        a_mech.up(arguments)
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_vmrun_start.assert_called()
        mock_get_ip.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'started on an unknown', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.start', return_value=None)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
def test_mech_up_problem(mock_locate, mock_load_mechfile,
                         mock_vmrun_start, capfd,
                         mechfile_one_entry):
    """Test 'mech up' when issue with starting VM"""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--gui': False,
        '--disable-shared-folders': True,
        '--disable-provisioning': True,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '--no-nat': None,
        '--remove-vagrant': None,
        '<instance>': None,
    }
    a_mech.up(arguments)
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_start.assert_called()
    out, _ = capfd.readouterr()
    assert re.search(r'not started', out, re.MULTILINE)


@patch('mech.utils.provision')
@patch('mech.vmrun.VMrun.start', return_value=True)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
def test_mech_up_with_provisioning(mock_locate, mock_load_mechfile,
                                   mock_vmrun_start,
                                   mock_provision, capfd, mechfile_one_entry):
    """Test 'mech up'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--gui': False,
        '--disable-shared-folders': True,
        '--disable-provisioning': False,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '--no-nat': None,
        '--remove-vagrant': None,
        '<instance>': None,
    }
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value='192.168.1.100') as mock_get_ip:
        a_mech.up(arguments)
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_vmrun_start.assert_called()
        mock_get_ip.assert_called()
        mock_provision.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'started', out, re.MULTILINE)


@patch('mech.utils.init_box')
@patch('mech.vmrun.VMrun.start', return_value=True)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_up_without_provisioning_without_shared_not_created(mock_locate,
                                                                 mock_load_mechfile,
                                                                 mock_vmrun_start,
                                                                 mock_init_box, capfd,
                                                                 mechfile_one_entry):
    """Test 'mech up'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--gui': False,
        '--disable-shared-folders': True,
        '--disable-provisioning': True,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '--no-nat': None,
        '--remove-vagrant': None,
        '<instance>': None,
    }
    mock_init_box.return_value = '/tmp/some.vmx'
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value='192.168.1.100') as mock_get_ip:
        a_mech.up(arguments)
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_vmrun_start.assert_called()
        mock_get_ip.assert_called()
        mock_init_box.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'started', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.enable_shared_folders')
@patch('mech.vmrun.VMrun.start', return_value=True)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
def test_mech_up_wth_shared_folders(mock_locate, mock_load_mechfile,
                                    mock_vmrun_start,
                                    mock_vmrun_enable_shared_folders,
                                    capfd, mechfile_one_entry):
    """Test 'mech up'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--gui': False,
        '--disable-shared-folders': False,
        '--disable-provisioning': True,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '--no-nat': None,
        '--remove-vagrant': None,
        '<instance>': None,
    }
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value='192.168.1.100') as mock_get_ip:
        a_mech.up(arguments)
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_vmrun_start.assert_called()
        mock_get_ip.assert_called()
        mock_vmrun_enable_shared_folders.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'started', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_ssh_config_not_created(mock_locate, mock_load_mechfile, capfd,
                                     mechfile_one_entry):
    """Test 'mech ssh-config' when vm is not created."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': None,
    }
    a_mech.ssh_config(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'not created', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate')
@patch('os.getcwd')
def test_mech_ssh_config_not_started(mock_getcwd, mock_locate, mock_load_mechfile,
                                     mechfile_one_entry):
    """Test 'mech ssh-config' when vm is created but not started."""
    mock_locate.return_value = '/tmp/first/some.vmx'
    mock_load_mechfile.return_value = mechfile_one_entry
    mock_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
    }
    with patch.object(mech.mech_instance.MechInstance, 'get_ip', return_value=None):
        with raises(SystemExit, match=r".*not yet ready for SSH.*"):
            a_mech.ssh_config(arguments)


@patch('os.chmod')
@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value='192.168.2.120')
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
@patch('os.getcwd')
def test_mech_ssh_config(mock_getcwd, mock_locate,  # pylint: disable=too-many-arguments
                         mock_load_mechfile, mock_get_guest_ip_address,
                         mock_chmod, capfd, mechfile_one_entry):
    """Test 'mech ssh-config'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    mock_getcwd.return_value = '/tmp'
    mock_chmod.return_value = 0
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
    }
    mock_file = mock_open()
    with patch('builtins.open', mock_file, create=True):
        a_mech.ssh_config(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_get_guest_ip_address.assert_called()
        mock_file.assert_called()
        mock_chmod.assert_called()
        assert re.search(r'Host first', out, re.MULTILINE)
        assert re.search(r'  User vagrant', out, re.MULTILINE)
        assert re.search(r'  Port 22', out, re.MULTILINE)


@patch('platform.system')
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_port_with_nat_from_linux(mock_locate, mock_load_mechfile,
                                       mock_platform_system,
                                       mechfile_one_entry):
    """Test 'mech port' with nat networking."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    port_arguments = {}
    port_arguments = {'<instance>': None}
    a_mock = MagicMock()
    a_mock.return_value = 'Linux'
    mock_platform_system.side_effect = a_mock
    with raises(SystemExit, match=r"This command is not supported on this OS."):
        a_mech.port(port_arguments)


HOST_NETWORKS = """Total host networks: 3
INDEX  NAME         TYPE         DHCP         SUBNET           MASK
0      vmnet0       bridged      false        empty            empty
1      vmnet1       hostOnly     true         172.16.11.0      255.255.255.0
8      vmnet8       nat          true         192.168.3.0      255.255.255.0"""
@patch('platform.system')
@patch('mech.vmrun.VMrun.list_port_forwardings', return_value='Total port forwardings: 0')
@patch('mech.vmrun.VMrun.list_host_networks', return_value=HOST_NETWORKS)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_port_with_nat_from_mac(mock_locate, mock_load_mechfile, mock_list_host_networks,
                                     mock_list_port_forwardings, mock_platform_system, capfd,
                                     mechfile_one_entry):
    """Test 'mech port' with nat networking."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    port_arguments = {}
    port_arguments = {'<instance>': None}
    a_mock = MagicMock()
    a_mock.return_value = 'Darwin'
    mock_platform_system.side_effect = a_mock
    a_mech.port(port_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_list_host_networks.assert_called()
    mock_list_port_forwardings.assert_called()
    mock_platform_system.assert_called()
    assert re.search(r'Total port forwardings: 0', out, re.MULTILINE)


@patch('platform.system')
@patch('mech.vmrun.VMrun.list_port_forwardings', return_value='Total port forwardings: 0')
@patch('mech.vmrun.VMrun.list_host_networks', return_value=HOST_NETWORKS)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_port_with_nat_and_instance_from_mac(mock_locate, mock_load_mechfile,
                                                  mock_list_host_networks,
                                                  mock_list_port_forwardings,
                                                  mock_platform_system, capfd,
                                                  mechfile_one_entry):
    """Test 'mech port first' with nat networking."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    port_arguments = {}
    port_arguments = {'<instance>': 'first'}
    a_mock = MagicMock()
    a_mock.return_value = 'Darwin'
    mock_platform_system.side_effect = a_mock
    a_mech.port(port_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_list_host_networks.assert_called()
    mock_list_port_forwardings.assert_called()
    mock_platform_system.assert_called()
    assert re.search(r'Total port forwardings: 0', out, re.MULTILINE)


HOST_NETWORKS = """Total host networks: 3
INDEX  NAME         TYPE         DHCP         SUBNET           MASK
0      vmnet0       bridged      false        empty            empty
1      vmnet1       hostOnly     true         172.16.11.0      255.255.255.0
8      vmnet8       nat          true         192.168.3.0      255.255.255.0"""
@patch('platform.system')
@patch('mech.vmrun.VMrun.list_port_forwardings', return_value='Total port forwardings: 0')
@patch('mech.vmrun.VMrun.list_host_networks', return_value=HOST_NETWORKS)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_port_with_nat_two_hosts_from_mac(mock_locate, mock_load_mechfile,
                                               mock_list_host_networks,
                                               mock_list_port_forwardings,
                                               mock_platform_system, capfd,
                                               mechfile_two_entries):
    """Test 'mech port' with nat networking and two instances."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    port_arguments = {}
    port_arguments = {'<instance>': None}
    a_mock = MagicMock()
    a_mock.return_value = 'Darwin'
    mock_platform_system.side_effect = a_mock
    a_mech.port(port_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_list_host_networks.assert_called()
    mock_list_port_forwardings.assert_called()
    mock_platform_system.assert_called()
    assert re.search(r'Total port forwardings: 0', out, re.MULTILINE)


HOST_NETWORKS_WITHOUT_NAT = """Total host networks: 2
INDEX  NAME         TYPE         DHCP         SUBNET           MASK
0      vmnet0       bridged      false        empty            empty
1      vmnet1       hostOnly     true         172.16.11.0      255.255.255.0"""
@patch('platform.system')
@patch('mech.vmrun.VMrun.list_host_networks', return_value=HOST_NETWORKS_WITHOUT_NAT)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_port_without_nat_from_mac(mock_locate, mock_load_mechfile,
                                        mock_list_host_networks,
                                        mock_platform_system, capfd,
                                        mechfile_one_entry):
    """Test 'mech port' without nat."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    port_arguments = {}
    port_arguments = {'<instance>': None}
    a_mock = MagicMock()
    a_mock.return_value = 'Darwin'
    mock_platform_system.side_effect = a_mock
    a_mech.port(port_arguments)
    _, err = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_list_host_networks.assert_called()
    mock_platform_system.assert_called()
    assert re.search(r'Cannot find a nat network', err, re.MULTILINE)


@patch('requests.get')
@patch('os.path.exists')
@patch('os.getcwd')
def test_mech_init(mock_os_getcwd, mock_os_path_exists,
                   mock_requests_get, capfd, catalog_as_json,
                   mech_init_arguments):
    """Test 'mech init' from Hashicorp'."""
    mock_os_getcwd.return_value = '/tmp'
    mock_os_path_exists.return_value = False
    global_arguments = {'--debug': False, '--cloud': None}
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = catalog_as_json

    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = mech_init_arguments
    arguments['<location>'] = 'bento/ubuntu-18.04'
    arguments['-add-me'] = None
    a_mech.init(arguments)
    out, _ = capfd.readouterr()
    assert re.search(r'Loading metadata', out, re.MULTILINE)


@patch('os.path.exists')
@patch('os.getcwd')
def test_mech_init_mechfile_exists(mock_os_getcwd, mock_os_path_exists,
                                   mech_init_arguments):
    """Test 'mech init' when Mechfile exists'."""
    mock_os_getcwd.return_value = '/tmp'
    mock_os_path_exists.return_value = True
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = mech_init_arguments
    arguments['<location>'] = 'bento/ubuntu-18.04'
    with raises(SystemExit, match=r".*already exists in this directory.*"):
        a_mech.init(arguments)


@patch('os.path.exists')
@patch('os.getcwd')
def test_mech_init_with_invalid_location(mock_os_getcwd, mock_os_path_exists, mech_add_arguments):
    """Test if we do not have a valid location. (must be in form of 'hashiaccount/boxname')."""
    mock_os_getcwd.return_value = '/tmp'
    mock_os_path_exists.return_value = False
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = mech_add_arguments
    arguments['<location>'] = 'bento'
    with raises(SystemExit, match=r"Provided box name is not valid"):
        a_mech.init(arguments)


@patch('requests.get')
@patch('os.getcwd')
def test_mech_add_mechfile_exists(mock_os_getcwd,
                                  mock_requests_get, capfd,
                                  catalog_as_json, mech_add_arguments):
    """Test 'mech add' when Mechfile exists'."""
    mock_os_getcwd.return_value = '/tmp'
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = catalog_as_json
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = mech_add_arguments
    arguments['<location>'] = 'bento/ubuntu-18.04'
    arguments['<name>'] = 'second'
    a_mech.add(arguments)
    out, _ = capfd.readouterr()
    mock_os_getcwd.assert_called()
    assert re.search(r'Loading metadata', out, re.MULTILINE)


def test_mech_add_mechfile_exists_no_name(mech_add_arguments):
    """Test 'mech add' when Mechfile exists but no name provided'."""
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = mech_add_arguments
    arguments['<location>'] = 'bento/ubuntu-18.04'
    arguments['<name>'] = None
    with raises(SystemExit, match=r".*Need to provide a name.*"):
        a_mech.add(arguments)


@patch('mech.utils.load_mechfile')
@patch('os.getcwd')
def test_mech_remove(mock_os_getcwd, mock_load_mechfile, capfd,
                     mechfile_one_entry):
    """Test 'mech remove'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    mock_os_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<name>': 'first',
    }
    a_mech.remove(arguments)
    out, _ = capfd.readouterr()
    mock_os_getcwd.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'Removed', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('os.getcwd')
def test_mech_remove_a_nonexisting_entry(mock_os_getcwd, mock_load_mechfile,
                                         mechfile_one_entry):
    """Test 'mech remove'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    mock_os_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<name>': 'second',
    }
    with raises(SystemExit, match=r".*There is no instance.*"):
        a_mech.remove(arguments)


def test_mech_remove_no_name():
    """Test 'mech remove' no name provided'."""
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<name>': None,
    }
    with raises(SystemExit, match=r".*Need to provide a name.*"):
        a_mech.remove(arguments)


@patch('mech.vmrun.VMrun.installed', return_value=True)
@patch('mech.vmrun.VMrun.list', return_value="Total running VMs: 0")
def test_mech_global_status(mock_list, mock_vmrun_installed, capfd):
    """Test 'mech global-status'."""
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {}
    a_mech.global_status(arguments)
    out, _ = capfd.readouterr()
    mock_list.assert_called()
    mock_vmrun_installed.assert_called()
    assert re.search(r'Total running VMs', out, re.MULTILINE)


PROCESSES = """UID        PID  PPID  C STIME TTY          TIME CMD
root         1     0  4 17:57 ?        00:00:00 /sbin/init
root         2     0  0 17:57 ?        00:00:00 [kthreadd]
root         3     2  0 17:57 ?        00:00:00 [kworker/0:0]
root         4     2  0 17:57 ?        00:00:00 [kworker/0:0H]
root         5     2  0 17:57 ?        00:00:00 [kworker/u2:0]
root         6     2  0 17:57 ?        00:00:00 [mm_percpu_wq]
root         7     2  0 17:57 ?        00:00:00 [ksoftirqd/0]
root         8     2  0 17:57 ?        00:00:00 [rcu_sched]
root         9     2  0 17:57 ?        00:00:00 [rcu_bh]"""
@patch('mech.utils.ssh')
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
@patch('os.getcwd')
def test_mech_ps(mock_getcwd, mock_locate, mock_load_mechfile, mock_ssh, capfd,
                 mechfile_two_entries):
    """Test 'mech ps'."""
    mock_ssh.return_value = 0, PROCESSES, ''
    mock_load_mechfile.return_value = mechfile_two_entries
    mock_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
    }
    a_mech.ps(arguments)
    out, _ = capfd.readouterr()
    mock_getcwd.assert_called()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_ssh.assert_called()
    assert re.search(r'kworker', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='')
@patch('os.getcwd')
def test_mech_ps_not_started_vm(mock_getcwd, mock_locate,
                                mock_load_mechfile, capfd,
                                mechfile_two_entries):
    """Test 'mech ps'."""
    mock_load_mechfile.return_value = mechfile_two_entries
    mock_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'second',
    }
    a_mech.ps(arguments)
    out, _ = capfd.readouterr()
    mock_getcwd.assert_called()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'not created', out, re.MULTILINE)


@patch('subprocess.run')
@patch('os.chmod', return_value=True)
@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value="192.168.1.100")
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_scp_host_to_guest(mock_locate,
                                mock_load_mechfile, mock_get_ip,
                                mock_chmod,
                                mock_subprocess_run,
                                mechfile_two_entries):
    """Test 'mech scp'."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<extra-ssh-args>': 'foo',
        '<src>': 'now',
        '<dst>': 'first:/tmp/now',
    }
    filename = os.path.join(mech.utils.mech_dir(), 'insecure_private_key')
    a_mock = mock_open()

    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.stdout = b''
    mock_subprocess_run.stderr = b''

    with patch.object(mech.mech_instance.MechInstance,
                      'get_vm_state', return_value="running") as mock_get_vm_state:
        with patch('builtins.open', a_mock, create=True):
            a_mech.scp(arguments)
            mock_locate.assert_called()
            mock_load_mechfile.assert_called()
            mock_subprocess_run.assert_called()
            mock_get_ip.assert_called()
            mock_chmod.assert_called()
            mock_get_vm_state.assert_called()
            a_mock.assert_called_once_with(filename, 'w')


@patch('subprocess.run')
@patch('os.chmod', return_value=True)
@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value="192.168.1.100")
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_scp_guest_to_host(mock_locate,
                                mock_load_mechfile, mock_get_ip,
                                mock_chmod,
                                mock_subprocess_run,
                                mechfile_two_entries):
    """Test 'mech scp'."""
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.stdout = b''
    mock_subprocess_run.stderr = b''

    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<extra-ssh-args>': None,
        '<src>': 'first:/tmp/now',
        '<dst>': '.',
    }
    filename = os.path.join(mech.utils.mech_dir(), 'insecure_private_key')
    a_mock = mock_open()
    with patch.object(mech.mech_instance.MechInstance,
                      'get_vm_state', return_value="running") as mock_get_vm_state:
        with patch('builtins.open', a_mock, create=True):
            a_mech.scp(arguments)
            mock_locate.assert_called()
            mock_load_mechfile.assert_called()
            mock_subprocess_run.assert_called()
            mock_get_ip.assert_called()
            mock_chmod.assert_called()
            mock_get_vm_state.assert_called()
            a_mock.assert_called_once_with(filename, 'w')


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_scp_guest_to_host_not_created(mock_locate,
                                            mock_load_mechfile,
                                            mechfile_two_entries):
    """Test 'mech scp'."""
    mock_load_mechfile.return_value = mechfile_two_entries
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<extra-ssh-args>': None,
        '<src>': 'first:/tmp/now',
        '<dst>': '.',
    }
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        a_mech.scp(arguments)
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()


def test_mech_scp_both_are_guests():
    """Test 'mech scp'."""
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<extra-ssh-args>': None,
        '<src>': 'first:/tmp/now',
        '<dst>': 'first:/tmp/now2',
    }
    with raises(SystemExit, match=r"Both src and dst are host destinations"):
        a_mech.scp(arguments)


def test_mech_scp_no_guests():
    """Test 'mech scp'."""
    global_arguments = {'--debug': False, '--cloud': None}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<extra-ssh-args>': None,
        '<src>': '/tmp/now',
        '<dst>': '/tmp/now2',
    }
    with raises(SystemExit, match=r"Could not determine instance name"):
        a_mech.scp(arguments)
