# Copyright (c) 2020 Mike Kinney

"""Unit tests for 'mech box'."""
import re

from unittest.mock import patch
from click.testing import CliRunner

from mech.mech_cli import cli


@patch('os.getcwd')
def test_mech_box_list_no_mechdir(mock_os_getcwd):
    """Test 'mech box list' with no '.mech' directory."""
    mock_os_getcwd.return_value = '/tmp'
    runner = CliRunner()
    with patch('os.walk') as mock_walk:
        # root, dirs, files
        mock_walk.return_value = [('./tmp', [], []), ]
        result = runner.invoke(cli, ['box', 'list'])
        mock_walk.assert_called()
        # ensure a header prints out
        assert re.search(r'BOX', result.output, re.MULTILINE)


@patch('os.getcwd')
def test_mech_box_list_empty_boxes_dir(mock_os_getcwd):
    """Test 'mech box list' with no directories in '.mech/boxes' directory."""
    mock_os_getcwd.return_value = '/tmp'
    runner = CliRunner()
    with patch('os.walk') as mock_walk:
        # root, dirs, files
        mock_walk.return_value = [('/tmp', ['boxes', ], []), ]
        result = runner.invoke(cli, ['box', 'list'])
        mock_walk.assert_called()
        # ensure a header prints out
        assert re.search(r'BOX', result.output, re.MULTILINE)


@patch('os.getcwd')
def test_mech_box_list_one_box(mock_os_getcwd):
    """Test 'mech box list' with one box present."""
    mock_os_getcwd.return_value = '/tmp'
    runner = CliRunner()
    with patch('os.walk') as mock_walk:
        # simulate: bento/ubuntu-18.04/201912.04.0/vmware_desktop.box
        mock_walk.return_value = [
            ('/tmp', ['boxes'], []),
            ('/tmp/boxes', ['bento'], []),
            ('/tmp/boxes/vmware/bento', ['ubuntu-18.04'], []),
            ('/tmp/boxes/vmware/bento/ubuntu-18.04', ['201912.04.0'], []),
            ('/tmp/boxes/vmware/bento/ubuntu-18.04/201912.04.0', [], ['vmware_desktop.box']),
        ]
        result = runner.invoke(cli, ['box', 'list'])
        mock_walk.assert_called()
        assert re.search(r'ubuntu-18.04', result.output, re.MULTILINE)


@patch('requests.get')
@patch('os.path.exists')
@patch('os.getcwd')
def test_mech_box_add_new(mock_os_getcwd, mock_os_path_exists,
                          mock_requests_get, catalog_as_json):
    """Test 'mech box add' from Hashicorp'."""
    mock_os_path_exists.return_value = False
    mock_os_getcwd.return_value = '/tmp'
    runner = CliRunner()
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = catalog_as_json
    result = runner.invoke(cli, ['box', 'add', '--provider', 'vmware', 'bento/ubuntu-18.04'])
    assert re.search(r'Checking integrity', result.output, re.MULTILINE)


@patch('requests.get')
@patch('os.path.exists')
@patch('os.getcwd')
def test_mech_box_add_existing(mock_os_getcwd, mock_os_path_exists,
                               mock_requests_get, catalog_as_json):
    """Test 'mech box add' from Hashicorp'."""
    mock_os_getcwd.return_value = '/tmp'
    mock_os_path_exists.return_value = True
    runner = CliRunner()
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = catalog_as_json
    result = runner.invoke(cli, ['box', 'add', 'bento/ubuntu-18.04'])
    assert re.search(r'Loading metadata', result.output, re.MULTILINE)


@patch('shutil.rmtree')
@patch('os.path.exists')
def test_mech_box_remove_exists(mock_os_path_exists, mock_rmtree):
    """Test 'mech box remove'."""
    mock_os_path_exists.return_value = True
    mock_rmtree.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, ['--debug', 'box', 'remove', '--version', 'somever',
                                 '--provider', 'vmware', '--name', 'bento/ubuntu-18.04'])
    mock_os_path_exists.assert_called()
    mock_rmtree.assert_called()
    assert re.search(r'Removed ', result.output, re.MULTILINE)


@patch('os.path.exists')
def test_mech_box_remove_does_not_exists(mock_os_path_exists):
    """Test 'mech box remove'."""
    mock_os_path_exists.return_value = False
    runner = CliRunner()
    result = runner.invoke(cli, ['box', 'remove', '--version', 'somever', '--provider',
                                 'vmware', '--name', 'bento/ubuntu-18.04'])
    mock_os_path_exists.assert_called()
    assert re.search(r'No boxes were removed', result.output, re.MULTILINE)
