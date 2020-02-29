# Copyright (c) 2020 Mike Kinney

"""mech cloud tests"""
import re

from unittest.mock import patch
from pytest import raises

import mech.command
import mech.mech
import mech.vmrun
import mech.mech_instance


def test_mech_cloud_init_no_name():
    """Test init()."""
    arguments = {
        '--hostname': None,
        '--directory': None,
        '--username': None,
        '<cloud-instance>': None
    }
    mc = mech.mech.MechCloud(arguments=arguments)
    with raises(AttributeError, match=r"Must provide a name for the cloud instance"):
        mc.init(arguments)


def test_mech_cloud_init_no_hostname():
    """test init()."""
    arguments = {
        '--hostname': None,
        '--directory': None,
        '--username': None,
        '<cloud-instance>': 'somecloud'
    }
    mc = mech.mech.MechCloud(arguments=arguments)
    with raises(SystemExit, match=r"A non-blank hostname is required"):
        mc.init(arguments)


def test_mech_cloud_init_no_directory():
    """test init()."""
    arguments = {
        '--hostname': 'somehost',
        '--directory': None,
        '--username': None,
        '<cloud-instance>': 'somecloud'
    }
    mc = mech.mech.MechCloud(arguments=arguments)
    with raises(SystemExit, match=r"A non-blank directory is required"):
        mc.init(arguments)


def test_mech_cloud_init_directory_with_spaces():
    """test init()."""
    arguments = {
        '--hostname': 'somehost',
        '--directory': 'some dir',
        '--username': 'someuser',
        '<cloud-instance>': 'somecloud'
    }
    mc = mech.mech.MechCloud(arguments=arguments)
    with raises(SystemExit, match=r"directory cannot contain spaces"):
        mc.init(arguments)


def test_mech_cloud_init_no_username():
    """test init()."""
    arguments = {
        '--hostname': 'somehost',
        '--directory': 'somedir',
        '--username': None,
        '<cloud-instance>': 'somecloud'
    }
    mc = mech.mech.MechCloud(arguments=arguments)
    with raises(SystemExit, match=r"A non-blank username is required"):
        mc.init(arguments)


@patch('mech.utils.save_mechcloudfile')
def test_mech_cloud_init(mock_save_mechcloudfile):
    """test init()."""
    arguments = {
        '--hostname': 'somehost',
        '--directory': 'somedir',
        '--username': 'someuser',
        '<cloud-instance>': 'somecloud'
    }
    mc = mech.mech.MechCloud(arguments=arguments)
    mc.init(arguments)
    mock_save_mechcloudfile.assert_called()


@patch('mech.utils.cloud_exists', return_value=False)
def test_mech_cloud_remove_does_not_exist(mock_cloud_exists,
                                          capfd):
    """test init()."""
    arguments = {
        '<cloud-instance>': 'somecloud'
    }
    mc = mech.mech.MechCloud(arguments=arguments)
    mc.remove(arguments)
    out, _ = capfd.readouterr()
    assert re.search(r'does not exist', out)
    mock_cloud_exists.assert_called()


@patch('mech.utils.cloud_exists', return_value=True)
@patch('mech.utils.remove_mechcloudfile_entry')
def test_mech_cloud_remove_exists(mock_cloud_exists,
                                  mock_remove_mechcloudfile_entry,
                                  capfd):
    """test init()."""
    arguments = {
        '<cloud-instance>': 'somecloud'
    }
    mc = mech.mech.MechCloud(arguments=arguments)
    mc.remove(arguments)
    out, _ = capfd.readouterr()
    assert re.search(r'Removed', out, re.MULTILINE)
    mock_cloud_exists.assert_called()
    mock_remove_mechcloudfile_entry.assert_called()


@patch('mech.utils.load_mechcloudfile')
def test_mech_cloud_list(mock_load_mechcloudfile, capfd,
                         mechcloudfile_one_entry):
    """test init()."""
    arguments = {}
    mc = mech.mech.MechCloud(arguments=arguments)
    mock_load_mechcloudfile.return_value = mechcloudfile_one_entry
    mc.list(arguments)
    out, _ = capfd.readouterr()
    assert re.search(r'mech clouds', out, re.MULTILINE)
    assert re.search(r'tophat.example.com', out, re.MULTILINE)
    assert re.search(r'~/test1', out, re.MULTILINE)
    assert re.search(r'bob', out, re.MULTILINE)


@patch('mech.utils.load_mechcloudfile')
def test_mech_cloud_upgrade_one_cloud(mock_load_mechcloudfile,
                                      mechcloudfile_one_entry):
    """test init()."""
    arguments = {
        '<cloud-instance>': 'tophat'
    }
    mc = mech.mech.MechCloud(arguments=arguments)
    mock_load_mechcloudfile.return_value = mechcloudfile_one_entry
    with patch.object(mech.mech.MechCloudInstance, 'upgrade', return_value='some output'):
        mc.upgrade(arguments)


@patch('mech.utils.load_mechcloudfile')
def test_mech_cloud_upgrade_all_instances(mock_load_mechcloudfile,
                                          mechcloudfile_one_entry):
    """test init()."""
    arguments = {
        '<cloud-instance>': None
    }
    mc = mech.mech.MechCloud(arguments=arguments)
    mock_load_mechcloudfile.return_value = mechcloudfile_one_entry
    with patch.object(mech.mech.MechCloudInstance, 'upgrade', return_value='some output'):
        mc.upgrade(arguments)
