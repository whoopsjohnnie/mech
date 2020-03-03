# Copyright (c) 2020 Mike Kinney

"""Unit tests for 'mech winrm'."""
import re

from unittest.mock import patch
from pypsrp.client import Client
from pytest import raises

import mech.command
import mech.mech
import mech.vmrun


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_winrm_config(mock_locate, mock_load_mechfile, capfd, mechfile_one_entry):
    """Test 'mech winrm config'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': 'first'}
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        a_mech.config(arguments)
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_get_ip.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'RDPHostName', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_winrm_config_not_created(mock_locate, mock_load_mechfile, capfd, mechfile_one_entry):
    """Test 'mech winrm config'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': 'first'}
    a_mech.config(arguments)
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    out, _ = capfd.readouterr()
    assert re.search(r'is not created', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_winrm_config_multiple(mock_locate, mock_load_mechfile, capfd, mechfile_one_entry):
    """Test 'mech winrm config'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': None}
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        a_mech.config(arguments)
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_get_ip.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'RDPHostName', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_winrm_run_command(mock_locate, mock_load_mechfile,
                                capfd, mechfile_one_entry):
    """Test 'mech winrm run'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': 'first', '--command': 'date /T', '--powershell': None}
    mock_rv = ('Tue 03/03/2020', 'foo', 0)
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        with patch.object(Client, 'execute_cmd', return_value=mock_rv) as mock_client_execute:
            a_mech.run(arguments)
            mock_locate.assert_called()
            mock_load_mechfile.assert_called()
            mock_get_ip.assert_called()
            mock_client_execute.assert_called()
            out, _ = capfd.readouterr()
            assert re.search(r'Tue 03/03/2020', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_winrm_run_powershell(mock_locate, mock_load_mechfile,
                                   capfd, mechfile_one_entry):
    """Test 'mech winrm run'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': 'first', '--command': None, '--powershell': 'Write-Host hello'}
    mock_rv = ('hello', None, False)
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        with patch.object(Client, 'execute_ps', return_value=mock_rv) as mock_client_execute:
            a_mech.run(arguments)
            mock_locate.assert_called()
            mock_load_mechfile.assert_called()
            mock_get_ip.assert_called()
            mock_client_execute.assert_called()
            out, _ = capfd.readouterr()
            assert re.search(r'hello', out, re.MULTILINE)


def test_mech_winrm_run_no_command_nor_powershell():
    """Test 'mech winrm run'."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': 'first', '--command': None, '--powershell': None}
    with raises(SystemExit, match=r"Command or Powershell is required"):
        a_mech.run(arguments)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_winrm_run_not_created(mock_locate, mock_load_mechfile,
                                    capfd, mechfile_one_entry):
    """Test 'mech winrm run'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': 'first', '--command': 'date /T', '--powershell': None}
    a_mech.run(arguments)
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    out, _ = capfd.readouterr()
    assert re.search(r'VM not created', out, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_winrm_copy(mock_locate, mock_load_mechfile,
                         capfd, mechfile_one_entry):
    """Test 'mech winrm copy'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': 'first', '<local>': 'now', '<remote>': 'now'}
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        with patch.object(Client, 'copy', return_value='now') as mock_client_copy:
            a_mech.copy(arguments)
            mock_locate.assert_called()
            mock_load_mechfile.assert_called()
            mock_get_ip.assert_called()
            mock_client_copy.assert_called()
            out, _ = capfd.readouterr()
            assert re.search(r'Copied', out, re.MULTILINE)


def test_mech_winrm_copy_no_local():
    """Test 'mech winrm copy'."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': 'first', '<local>': None, '<remote>': 'now'}
    with raises(SystemExit, match=r"local file required"):
        a_mech.copy(arguments)


def test_mech_winrm_copy_no_remote():
    """Test 'mech winrm copy'."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': 'first', '<local>': 'now', '<remote>': None}
    with raises(SystemExit, match=r"remote file required"):
        a_mech.copy(arguments)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_winrm_fetch(mock_locate, mock_load_mechfile,
                          capfd, mechfile_one_entry):
    """Test 'mech winrm fetch'."""
    mock_load_mechfile.return_value = mechfile_one_entry
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': 'first', '<local>': 'now', '<remote>': 'now'}
    with patch.object(mech.mech_instance.MechInstance,
                      'get_ip', return_value="192.168.1.145") as mock_get_ip:
        with patch.object(Client, 'fetch', return_value='now') as mock_client_fetch:
            a_mech.fetch(arguments)
            mock_locate.assert_called()
            mock_load_mechfile.assert_called()
            mock_get_ip.assert_called()
            mock_client_fetch.assert_called()
            out, _ = capfd.readouterr()
            assert re.search(r'Fetched', out, re.MULTILINE)


def test_mech_winrm_fetch_no_local():
    """Test 'mech winrm fetch'."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': 'first', '<local>': None, '<remote>': 'now'}
    with raises(SystemExit, match=r"local file required"):
        a_mech.fetch(arguments)


def test_mech_winrm_fetch_no_remote():
    """Test 'mech winrm fetch'."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechWinrm(arguments=global_arguments)
    arguments = {'<instance>': 'first', '<local>': 'now', '<remote>': None}
    with raises(SystemExit, match=r"remote file required"):
        a_mech.fetch(arguments)
