# Copyright (c) 2020 Mike Kinney

"""MechCloudInstance tests"""

import re

from unittest.mock import patch
from pytest import raises


import mech.mech
import mech.vmrun
import mech.mech_cloud_instance


def test_mech_cloud_instance_name_not_being_in_instance():
    """Test mech instance class."""
    with raises(AttributeError):
        mech.mech_cloud_instance.MechCloudInstance('', {})


@patch('mech.utils.load_mechcloudfile')
def test_mech_cloud_instance(mock_load, mechcloudfile_one_entry):
    """Test mech instance class."""
    mock_load.return_value = mechcloudfile_one_entry
    inst = mech.mech_cloud_instance.MechCloudInstance('tophat', mechcloudfile_one_entry)
    inst.read_config('tophat')
    expected_config = {'name': 'tophat', 'hostname': 'tophat.example.com',
                       'directory': '~/test1', 'username': 'bob'}
    assert inst.config() == expected_config
    assert inst.name == 'tophat'
    assert inst.hostname == 'tophat.example.com'
    assert inst.directory == '~/test1'
    assert inst.username == 'bob'
    mock_load.assert_called()
    with raises(SystemExit):
        inst.set_hostname('')
    with raises(SystemExit):
        inst.set_directory('')
    with raises(SystemExit):
        inst.set_directory('something with spaces')
    with raises(SystemExit):
        inst.set_username('')


def test_mech_cloud_instance_read_config(mechcloudfile_one_entry):
    """Test read_config method."""
    inst = mech.mech_cloud_instance.MechCloudInstance('boo', mechcloudfile_one_entry)
    with raises(SystemExit):
        inst.read_config('boo')


@patch('mech.utils.save_mechcloudfile')
@patch('mech.utils.load_mechcloudfile')
def test_mech_cloud_instance_init_when_vmrun_and_virtualbox_is_found(mock_load, mock_save,
                                                                     capfd,
                                                                     mechcloudfile_one_entry):
    """Test init method."""
    mock_load.return_value = mechcloudfile_one_entry
    inst = mech.mech_cloud_instance.MechCloudInstance('tophat', mechcloudfile_one_entry)
    inst.read_config('tophat')
    with patch.object(mech.mech_cloud_instance.MechCloudInstance,
                      'ssh', return_value=(0, '', '')) as mock_ssh:
        inst.init()
        out, _ = capfd.readouterr()
        mock_load.assert_called()
        mock_save.assert_called()
        mock_ssh.assert_called()
        assert re.search(r'Creating directory', out, re.MULTILINE)
        assert re.search(r'Creating python', out, re.MULTILINE)
        assert re.search(r'Installing mikemech', out, re.MULTILINE)
        assert re.search(r'vmrun was found', out, re.MULTILINE)
        assert re.search(r'VBoxManage was found', out, re.MULTILINE)
        assert re.search(r'Done', out, re.MULTILINE)


@patch('mech.utils.save_mechcloudfile')
@patch('mech.utils.load_mechcloudfile')
def test_mech_cloud_instance_init_when_vmrun_and_virtualbox_are_not_found(mock_load, mock_save,
                                                                          capfd,
                                                                          mechcloudfile_one_entry):
    """Test init method."""
    mock_load.return_value = mechcloudfile_one_entry
    inst = mech.mech_cloud_instance.MechCloudInstance('tophat', mechcloudfile_one_entry)
    inst.read_config('tophat')
    with patch.object(mech.mech_cloud_instance.MechCloudInstance,
                      'ssh', return_value=(1, 'some output', 'some err')) as mock_ssh:
        inst.init()
        out, _ = capfd.readouterr()
        mock_load.assert_called()
        mock_save.assert_called()
        mock_ssh.assert_called()
        assert re.search(r'Creating directory', out, re.MULTILINE)
        assert re.search(r'Creating python', out, re.MULTILINE)
        assert re.search(r'Installing mikemech', out, re.MULTILINE)
        assert re.search(r'vmrun was not found', out, re.MULTILINE)
        assert re.search(r'VBoxManage was not found', out, re.MULTILINE)
        assert re.search(r'will not be very useful', out, re.MULTILINE)
        assert re.search(r'Done', out, re.MULTILINE)


@patch('mech.utils.load_mechcloudfile')
def test_mech_cloud_instance_upgrade(mock_load, capfd, mechcloudfile_one_entry):
    """Test upgrade method."""
    mock_load.return_value = mechcloudfile_one_entry
    inst = mech.mech_cloud_instance.MechCloudInstance('tophat', mechcloudfile_one_entry)
    inst.read_config('tophat')
    with patch.object(mech.mech_cloud_instance.MechCloudInstance,
                      'ssh', return_value=(0, 'some output', 'some err')) as mock_ssh:
        inst.upgrade()
        mock_ssh.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'Updating pip', out, re.MULTILINE)
        assert re.search(r'Updating mikemech', out, re.MULTILINE)
        assert re.search(r'Done', out, re.MULTILINE)


@patch('mech.utils.ssh_with_username', return_value=(1, 'some output', 'some error'))
@patch('mech.utils.load_mechcloudfile')
def test_mech_cloud_instance_ssh(mock_load, mock_ssh, mechcloudfile_one_entry):
    """Test ssh method."""
    mock_load.return_value = mechcloudfile_one_entry
    inst = mech.mech_cloud_instance.MechCloudInstance('tophat', mechcloudfile_one_entry)
    inst.read_config('tophat')
    rc, stdout, stderr = inst.ssh('uptime', True)
    assert rc == 1
    assert re.search(r'some output', stdout, re.MULTILINE)
    assert re.search(r'some error', stderr, re.MULTILINE)
