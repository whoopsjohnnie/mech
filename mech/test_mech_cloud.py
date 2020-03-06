# Copyright (c) 2020 Mike Kinney

"""mech cloud tests"""
import re

from unittest.mock import patch
from click.testing import CliRunner

import mech.mech
import mech.vmrun
import mech.mech_instance
import mech.mech_cloud_instance
from mech.mech_cli import cli


def test_mech_cloud_init_no_host():
    """Test init()."""
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'init'])
    assert re.search('SystemExit', '{}'.format(result))


def test_mech_cloud_init_no_dir():
    """Test init()."""
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'init', 'host'])
    assert re.search('SystemExit', '{}'.format(result))


def test_mech_cloud_init_no_user():
    """Test init()."""
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'init', 'host', 'dir'])
    assert re.search('SystemExit', '{}'.format(result))


def test_mech_cloud_init_no_cloud_name():
    """Test init()."""
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'init', 'host', 'dir', 'bob'])
    assert re.search('SystemExit', '{}'.format(result))


def test_mech_cloud_init():
    """test init()."""
    runner = CliRunner()
    # mock 'init' as we do not really want to init/communicate with this host
    with patch.object(mech.mech_cloud_instance.MechCloudInstance,
                      'init') as mock_init:
        runner.invoke(cli, ['cloud', 'init', 'host', 'dir', 'bob', 'somecloud'])
        mock_init.assert_called()


@patch('mech.utils.cloud_exists', return_value=False)
def test_mech_cloud_remove_does_not_exist(mock_cloud_exists):
    """test init()."""
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'remove', 'somecloud'])
    assert re.search(r'does not exist', result.output)
    mock_cloud_exists.assert_called()


@patch('mech.utils.cloud_exists', return_value=True)
@patch('mech.utils.remove_mechcloudfile_entry')
def test_mech_cloud_remove_exists(mock_cloud_exists,
                                  mock_remove_mechcloudfile_entry):
    """test init()."""
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'remove', 'somecloud'])
    assert re.search(r'Removed', result.output, re.MULTILINE)
    mock_cloud_exists.assert_called()
    mock_remove_mechcloudfile_entry.assert_called()


@patch('mech.utils.load_mechcloudfile')
def test_mech_cloud_list(mock_load_mechcloudfile,
                         mechcloudfile_one_entry):
    """test init()."""
    mock_load_mechcloudfile.return_value = mechcloudfile_one_entry
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'list'])
    assert re.search(r'mech clouds', result.output, re.MULTILINE)
    assert re.search(r'tophat.example.com', result.output, re.MULTILINE)
    assert re.search(r'~/test1', result.output, re.MULTILINE)
    assert re.search(r'bob', result.output, re.MULTILINE)


@patch('mech.utils.load_mechcloudfile')
def test_mech_cloud_upgrade_one_cloud(mock_load_mechcloudfile,
                                      mechcloudfile_one_entry):
    """test init()."""
    mock_load_mechcloudfile.return_value = mechcloudfile_one_entry
    runner = CliRunner()
    with patch.object(mech.mech_cloud_instance.MechCloudInstance, 'upgrade',
                      return_value='some output'):
        runner.invoke(cli, ['cloud', 'upgrade', 'tophat'])


@patch('mech.utils.load_mechcloudfile')
def test_mech_cloud_upgrade_all_instances(mock_load_mechcloudfile,
                                          mechcloudfile_one_entry):
    """test init()."""
    mock_load_mechcloudfile.return_value = mechcloudfile_one_entry
    runner = CliRunner()
    with patch.object(mech.mech_cloud_instance.MechCloudInstance,
                      'upgrade', return_value='some output'):
        runner.invoke(cli, ['cloud', 'upgrade'])
