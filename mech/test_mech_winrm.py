# Copyright (c) 2020 Mike Kinney

"""Unit tests for 'mech winrm'."""
import re

from unittest.mock import patch
from pypsrp.client import Client
from click.testing import CliRunner

import mech.mech
import mech.vmrun
from mech.mech_cli import cli


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_winrm_config(mock_locate, mock_load_mechfile, mechfile_one_entry):
    """Test 'mech winrm config'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    runner = CliRunner()
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        result = runner.invoke(cli, ['winrm', 'config', 'first'])
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_get_ip.assert_called()
        assert re.search(r'RDPHostName', result.output, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_winrm_config_not_created(mock_locate, mock_load_mechfile, mechfile_one_entry):
    """Test 'mech winrm config'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    runner = CliRunner()
    result = runner.invoke(cli, ['winrm', 'config', 'first'])
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'is not created', result.output, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_winrm_config_multiple(mock_locate, mock_load_mechfile, mechfile_one_entry):
    """Test 'mech winrm config'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    runner = CliRunner()
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        result = runner.invoke(cli, ['winrm', 'config'])
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_get_ip.assert_called()
        assert re.search(r'RDPHostName', result.output, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_winrm_run_command(mock_locate, mock_load_mechfile,
                                mechfile_one_entry):
    """Test 'mech winrm run'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    runner = CliRunner()
    mock_rv = ('Tue 03/03/2020', 'foo', 0)
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        with patch.object(Client, 'execute_cmd', return_value=mock_rv) as mock_client_execute:
            # hmm... space in arg... ok?
            result = runner.invoke(cli, ['winrm', 'run', '--command', 'date /T', 'first'])
            mock_locate.assert_called()
            mock_load_mechfile.assert_called()
            mock_get_ip.assert_called()
            mock_client_execute.assert_called()
            assert re.search(r'Tue 03/03/2020', result.output, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_winrm_run_powershell(mock_locate, mock_load_mechfile,
                                   mechfile_one_entry):
    """Test 'mech winrm run'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    runner = CliRunner()
    mock_rv = ('hello', None, False)
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        with patch.object(Client, 'execute_ps', return_value=mock_rv) as mock_client_execute:
            result = runner.invoke(cli, ['winrm', 'run', '--powershell',
                                         'Write-Host hello', 'first'])
            mock_locate.assert_called()
            mock_load_mechfile.assert_called()
            mock_get_ip.assert_called()
            mock_client_execute.assert_called()
            assert re.search(r'hello', result.output, re.MULTILINE)


def test_mech_winrm_run_no_command_nor_powershell():
    """Test 'mech winrm run'."""
    runner = CliRunner()
    result = runner.invoke(cli, ['winrm', 'run', 'first'])
    assert re.search('Command or Powershell is required', '{}'.format(result.exception))


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_winrm_run_not_created(mock_locate, mock_load_mechfile,
                                    mechfile_one_entry):
    """Test 'mech winrm run'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    runner = CliRunner()
    result = runner.invoke(cli, ['winrm', 'run', '--command', 'date /T', 'first'])
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'VM not created', result.output, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_winrm_copy(mock_locate, mock_load_mechfile,
                         mechfile_one_entry):
    """Test 'mech winrm copy'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    runner = CliRunner()
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        with patch.object(Client, 'copy', return_value='now') as mock_client_copy:
            result = runner.invoke(cli, ['winrm', 'copy', 'now', 'now', 'first'])
            mock_locate.assert_called()
            mock_load_mechfile.assert_called()
            mock_get_ip.assert_called()
            mock_client_copy.assert_called()
            assert re.search(r'Copied', result.output, re.MULTILINE)


def test_mech_winrm_copy_no_local():
    """Test 'mech winrm copy'."""
    runner = CliRunner()
    result = runner.invoke(cli, ['winrm', 'copy', 'now', 'first'])
    assert re.search('SystemExit', '{}'.format(result))


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_winrm_fetch(mock_locate, mock_load_mechfile,
                          mechfile_one_entry):
    """Test 'mech winrm fetch'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    runner = CliRunner()
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        with patch.object(Client, 'fetch', return_value='now') as mock_client_fetch:
            result = runner.invoke(cli, ['winrm', 'fetch', 'now', 'now', 'first'])
            mock_locate.assert_called()
            mock_load_mechfile.assert_called()
            mock_get_ip.assert_called()
            mock_client_fetch.assert_called()
            assert re.search(r'Fetched', result.output, re.MULTILINE)


def test_mech_winrm_fetch_no_local():
    """Test 'mech winrm fetch'."""
    runner = CliRunner()
    result = runner.invoke(cli, ['winrm', 'fetch', 'now', 'first'])
    assert re.search('SystemExit', '{}'.format(result))
