# Copyright (c) 2020 Mike Kinney

"""Test mech utils."""
import os
import re
import sys
import subprocess

from unittest.mock import patch, mock_open, MagicMock
from collections import OrderedDict
from pytest import raises

import mech.utils
import mech.mech_instance


@patch('os.getcwd')
def test_main_dir(mock_os_getcwd):
    """Test main_dir()."""
    mock_os_getcwd.return_value = '/tmp'
    main = mech.utils.main_dir()
    mock_os_getcwd.assert_called()
    assert main == '/tmp'


@patch('os.getcwd')
def test_mech_dir(mock_os_getcwd):
    """Test mech_dir()."""
    mock_os_getcwd.return_value = '/tmp'
    mechdir = mech.utils.mech_dir()
    mock_os_getcwd.assert_called()
    assert mechdir == '/tmp/.mech'


@patch('os.makedirs')
def test_makedirs(mock_os_makedirs):
    """Test makedirs()."""
    mock_os_makedirs.return_value = True
    mech.utils.makedirs('/tmp/1234')
    mock_os_makedirs.assert_called()


def test_confirm_yes():
    """Test confirm."""
    a_mock = MagicMock()
    a_mock.return_value = 'Y'
    with patch('mech.utils.raw_input', a_mock):
        assert mech.utils.confirm("Is this silly?")


def test_confirm_yes_by_default():
    """Test confirm."""
    a_mock = MagicMock()
    a_mock.return_value = ''
    with patch('mech.utils.raw_input', a_mock):
        assert mech.utils.confirm("Is this silly?")


def test_confirm_no_by_default():
    """Test confirm."""
    a_mock = MagicMock()
    a_mock.return_value = ''
    with patch('mech.utils.raw_input', a_mock):
        assert not mech.utils.confirm("Is this silly?", 'n')


def test_confirm_no():
    """Test confirm."""
    a_mock = MagicMock()
    a_mock.return_value = 'n'
    with patch('mech.utils.raw_input', a_mock):
        assert not mech.utils.confirm("Is this silly?")


def test_confirm_nonstandard_default():
    """Test confirm."""
    a_mock = MagicMock()
    a_mock.return_value = 'y'
    with patch('mech.utils.raw_input', a_mock):
        assert mech.utils.confirm("Is this silly?", 'q')


@patch('json.loads')
@patch('os.path.isfile')
@patch('os.getcwd')
def test_load_mechfile(mock_os_getcwd, mock_os_path_isfile, mock_json_loads):
    """Test mech_load_mechfile()."""
    mock_os_getcwd.return_value = '/tmp'
    expected = {}
    mock_json_loads.return_value = expected
    mock_os_path_isfile.return_value = True
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        assert mech.utils.load_mechfile() == expected
    a_mock.assert_called()
    mock_os_getcwd.assert_called()


@patch('json.loads')
@patch('os.path.isfile')
@patch('os.getcwd')
def test_load_mechfile_no_mechfile(mock_os_getcwd, mock_os_path_isfile, mock_json_loads):
    """Test mech_load_mechfile()."""
    mock_os_getcwd.return_value = '/tmp'
    expected = {}
    mock_json_loads.return_value = expected
    mock_os_path_isfile.return_value = False
    with raises(SystemExit):
        a_mock = mock_open()
        with patch('builtins.open', a_mock, create=True):
            mech.utils.load_mechfile()


@patch('json.loads')
@patch('os.path.isfile')
@patch('os.getcwd')
def test_load_mechfile_no_mechfile_should_not_exist(mock_os_getcwd, mock_os_path_isfile,
                                                    mock_json_loads):
    """Test mech_load_mechfile()."""
    mock_os_getcwd.return_value = '/tmp'
    expected = {}
    mock_json_loads.return_value = expected
    mock_os_path_isfile.return_value = False
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        got = mech.utils.load_mechfile(should_exist=False)
    assert got == expected
    mock_os_getcwd.assert_called()


@patch('os.path.isfile')
@patch('os.getcwd')
def test_load_mechfile_invalid_json(mock_os_getcwd, mock_os_path_isfile):
    """Test mech_load_mechfile()."""
    mock_os_getcwd.return_value = '/tmp'
    expected = {}
    # bad_json below is missing a comma between elements
    bad_json = '''{"foo": "bar" "foo2": 1}'''
    mock_os_path_isfile.return_value = True
    a_mock = mock_open(read_data=bad_json)
    with patch('builtins.open', a_mock, create=True):
        got = mech.utils.load_mechfile()
    assert got == expected
    a_mock.assert_called()
    mock_os_getcwd.assert_called()


def test_save_mechfile_empty_config():
    """Test save_mechfile with empty configuration."""
    filename = os.path.join(mech.utils.main_dir(), 'Mechfile')
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        assert mech.utils.save_mechfile({})
    a_mock.assert_called_once_with(filename, 'w+')
    a_mock.return_value.write.assert_called_once_with('{}')


def test_save_mechfile_one(helpers):
    """Test save_mechfile with one entry."""
    first_dict = {
        'first': {
            'name':
            'first',
            'box':
            'bento/ubuntu-18.04',
            'box_version':
            '201912.04.0',
            'url':
            'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/'
            'versions/201912.04.0/providers/vmware_desktop.box'
        }
    }
    first_json = '''{
  "first": {
    "box": "bento/ubuntu-18.04",
    "box_version": "201912.04.0",
    "name": "first",
    "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/versions/201912.04.0/providers/vmware_desktop.box"
  }
}'''  # noqa: 501
    filename = os.path.join(mech.utils.main_dir(), 'Mechfile')
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        assert mech.utils.save_mechfile(first_dict)
    a_mock.assert_called_once_with(filename, 'w+')
    assert first_json == helpers.get_mock_data_written(a_mock)


def test_save_mechfile_two(helpers):
    """Test save_mechfile with two entries."""
    two_dict = {
        'first': {
            'name':
            'first',
            'box':
            'bento/ubuntu-18.04',
            'box_version':
            '201912.04.0',
            'url':
            'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/'
            'versions/201912.04.0/providers/vmware_desktop.box'
        },
        'second': {
            'name':
            'second',
            'box':
            'bento/ubuntu-18.04',
            'box_version':
            '201912.04.0',
            'url':
            'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/'
            'versions/201912.04.0/providers/vmware_desktop.box'
        }
    }
    two_json = '''{
  "first": {
    "box": "bento/ubuntu-18.04",
    "box_version": "201912.04.0",
    "name": "first",
    "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/versions/201912.04.0/providers/vmware_desktop.box"
  },
  "second": {
    "box": "bento/ubuntu-18.04",
    "box_version": "201912.04.0",
    "name": "second",
    "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/versions/201912.04.0/providers/vmware_desktop.box"
  }
}'''  # noqa: 501
    filename = os.path.join(mech.utils.main_dir(), 'Mechfile')
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        assert mech.utils.save_mechfile(two_dict)
    a_mock.assert_called_once_with(filename, 'w+')
    assert two_json == helpers.get_mock_data_written(a_mock)


@patch('os.getlogin')
@patch('mech.utils.save_mechfile_entry')
@patch('mech.utils.build_mechfile_entry')
def test_init_mechfile_with_add_me_option(mock_build_mechfile_entry, mock_save_mechfile_entry,
                                          mock_os_getlogin):
    """Test init_mechfile."""
    mock_build_mechfile_entry.return_value = {}
    mock_save_mechfile_entry.return_value = True
    mock_os_getlogin.return_value = 'bob'
    assert mech.utils.init_mechfile(add_me=True)
    mock_build_mechfile_entry.assert_called()
    mock_save_mechfile_entry.assert_called()


@patch('os.getlogin')
@patch('mech.utils.save_mechfile_entry')
@patch('mech.utils.build_mechfile_entry')
def test_add_to_mechfile_with_add_me_option(mock_build_mechfile_entry, mock_save_mechfile_entry,
                                            mock_os_getlogin):
    """Test add_to_mechfile."""
    mock_build_mechfile_entry.return_value = {}
    mock_save_mechfile_entry.return_value = True
    mock_os_getlogin.return_value = 'bob'
    assert mech.utils.add_to_mechfile(add_me=True)
    mock_build_mechfile_entry.assert_called()
    mock_save_mechfile_entry.assert_called()


@patch('mech.vmrun.VMrun.run_script_in_guest', return_value='')
@patch('mech.vmrun.VMrun.installed_tools')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_add_auth(mock_locate, mock_installed_tools,
                  mock_run_script_in_guest, capfd,
                  mechfile_one_entry_with_auth_and_mech_use):
    """Test add_auth."""
    mock_installed_tools.return_value = "running"
    inst = mech.mech_instance.MechInstance('first', mechfile_one_entry_with_auth_and_mech_use)
    inst.user = 'vagrant'
    inst.password = 'vagrant'
    print('inst:{}'.format(inst))
    pub_key = 'some fake pub key'
    a_mock = mock_open(read_data=pub_key)
    with patch('builtins.open', a_mock, create=True):
        mech.utils.add_auth(inst)
        a_mock.assert_called()
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_installed_tools.assert_called()
        assert re.search(r'Adding auth', out, re.MULTILINE)
        assert re.search(r'Added auth', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.run_script_in_guest', return_value=None)
@patch('mech.vmrun.VMrun.installed_tools')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_add_auth_script_fails(mock_locate, mock_installed_tools,
                               mock_run_script_in_guest, capfd,
                               mechfile_one_entry_with_auth_and_mech_use):
    """Test add_auth."""
    mock_installed_tools.return_value = "running"
    inst = mech.mech_instance.MechInstance('first', mechfile_one_entry_with_auth_and_mech_use)
    inst.user = 'vagrant'
    inst.password = 'vagrant'
    print('inst:{}'.format(inst))
    pub_key = 'some fake pub key'
    a_mock = mock_open(read_data=pub_key)
    with patch('builtins.open', a_mock, create=True):
        mech.utils.add_auth(inst)
        a_mock.assert_called()
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_installed_tools.assert_called()
        assert re.search(r'Adding auth', out, re.MULTILINE)
        assert re.search(r'Did not add auth', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.run_script_in_guest', return_value=None)
@patch('mech.vmrun.VMrun.installed_tools')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_add_auth_could_not_read_pub_key(mock_locate, mock_installed_tools,
                                         mock_run_script_in_guest, capfd,
                                         mechfile_one_entry_with_auth_and_mech_use):
    """Test add_auth."""
    mock_installed_tools.return_value = "running"
    inst = mech.mech_instance.MechInstance('first', mechfile_one_entry_with_auth_and_mech_use)
    inst.user = 'vagrant'
    inst.password = 'vagrant'
    print('inst:{}'.format(inst))
    a_mock = mock_open(read_data=None)
    with patch('builtins.open', a_mock, create=True):
        mech.utils.add_auth(inst)
        a_mock.assert_called()
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_installed_tools.assert_called()
        assert re.search(r'Adding auth', out, re.MULTILINE)
        assert re.search(r'Could not read contents', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.run_script_in_guest', return_value=None)
@patch('mech.vmrun.VMrun.installed_tools')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_add_auth_no_username_in_auth(mock_locate, mock_installed_tools,
                                      mock_run_script_in_guest, capfd,
                                      mechfile_one_entry_with_auth_and_mech_use):
    """Test add_auth."""
    mock_installed_tools.return_value = "running"
    inst = mech.mech_instance.MechInstance('first', mechfile_one_entry_with_auth_and_mech_use)
    inst.user = 'vagrant'
    inst.password = 'vagrant'
    # remove username
    del inst.auth['username']
    print('inst:{}'.format(inst))
    mech.utils.add_auth(inst)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_installed_tools.assert_called()
    assert re.search(r'Adding auth', out, re.MULTILINE)
    assert re.search(r'Warning: Need a username', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.run_script_in_guest', return_value=None)
@patch('mech.vmrun.VMrun.installed_tools')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_add_auth_no_auth(mock_locate, mock_installed_tools,
                          mock_run_script_in_guest, capfd,
                          mechfile_one_entry):
    """Test add_auth."""
    mock_installed_tools.return_value = "running"
    inst = mech.mech_instance.MechInstance('first', mechfile_one_entry)
    inst.user = 'vagrant'
    inst.password = 'vagrant'
    print('inst:{}'.format(inst))
    mech.utils.add_auth(inst)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_installed_tools.assert_called()
    assert re.search(r'Adding auth', out, re.MULTILINE)
    assert re.search(r'No auth to add', out, re.MULTILINE)


def test_add_auth_no_instance():
    """Test add_auth when no instance."""
    with raises(SystemExit, match=r"Need to provide an instance"):
        mech.utils.add_auth(None)


def test_add_auth_no_vmx(mechfile_one_entry_with_auth_and_mech_use):
    """Test add_auth."""
    inst = mech.mech_instance.MechInstance('first', mechfile_one_entry_with_auth_and_mech_use)
    inst.user = ''
    inst.password = 'vagrant'
    inst.vmx = None
    with raises(SystemExit, match=r"Need to provide vmx"):
        mech.utils.add_auth(inst)


def test_add_auth_blank_user(mechfile_one_entry_with_auth_and_mech_use):
    """Test add_auth."""
    inst = mech.mech_instance.MechInstance('first', mechfile_one_entry_with_auth_and_mech_use)
    inst.user = ''
    inst.password = 'vagrant'
    inst.vmx = '/tmp/first/some.vmx'
    with raises(SystemExit, match=r"Need to provide user"):
        mech.utils.add_auth(inst)


def test_add_auth_password_is_none(mechfile_one_entry_with_auth_and_mech_use):
    """Test add_auth."""
    inst = mech.mech_instance.MechInstance('first', mechfile_one_entry_with_auth_and_mech_use)
    inst.user = 'vagrant'
    inst.password = None
    inst.vmx = '/tmp/first/some.vmx'
    with raises(SystemExit, match=r"Need to provide password"):
        mech.utils.add_auth(inst)


def test_add_auth_blank_passwod(mechfile_one_entry_with_auth_and_mech_use):
    """Test add_auth."""
    inst = mech.mech_instance.MechInstance('first', mechfile_one_entry_with_auth_and_mech_use)
    inst.user = 'vagrant'
    inst.password = ''
    inst.vmx = '/tmp/first/some.vmx'
    with raises(SystemExit, match=r"Need to provide password"):
        mech.utils.add_auth(inst)


def test_add_auth_user_is_none(mechfile_one_entry_with_auth_and_mech_use):
    """Test add_auth."""
    inst = mech.mech_instance.MechInstance('first', mechfile_one_entry_with_auth_and_mech_use)
    inst.user = None
    inst.password = 'vagrant'
    inst.vmx = '/tmp/first/some.vmx'
    with raises(SystemExit, match=r"Need to provide user"):
        mech.utils.add_auth(inst)


@patch('mech.vmrun.VMrun.installed_tools')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_add_auth_cannot_add_auth(mock_locate, mock_installed_tools,
                                  capfd,
                                  mechfile_one_entry_with_auth_and_mech_use):
    """Test add_auth."""
    mock_installed_tools.return_value = False
    inst = mech.mech_instance.MechInstance('first', mechfile_one_entry_with_auth_and_mech_use)
    inst.user = 'vagrant'
    inst.password = 'vagrant'
    with raises(SystemExit, match=r"Cannot add auth"):
        mech.utils.add_auth(inst)


def test_tar_cmd():
    """Test tar cmd.
    """
    a_mock = MagicMock()
    another_mock = MagicMock()
    yet_another_mock = MagicMock()
    yet_another_mock.returncode = 0
    yet_another_mock.return_value = 'blah blah blah --force-local boo --fast-read blah', None
    another_mock.communicate = yet_another_mock
    another_mock.communicate.returncode = 0
    another_mock.returncode = 0
    a_mock.return_value = another_mock
    a_mock.returncode = 0
    if sys.platform.startswith('darwin'):
        expected = ["tar", "--force-local", "--fast-read"]
    else:
        expected = ["tar", "--force-local"]
    with patch('subprocess.Popen', a_mock):
        got = mech.utils.tar_cmd(wildcards=True, fast_read=True, force_local=True)
        assert expected == got


def test_tar_cmd_when_tar_not_found():
    """Test tar cmd."""
    a_mock = MagicMock()
    a_mock.return_value = None
    a_mock.returncode = None
    a_mock.side_effect = OSError()
    with patch('subprocess.Popen', a_mock):
        tar = mech.utils.tar_cmd()
        assert tar is None


def test_config_ssh_string_empty():
    """Test config_ssh_string with empty configuration."""
    ssh_string = mech.utils.config_ssh_string({})
    assert ssh_string == "Host \n"


def test_config_ssh_string_simple():
    """Test config_ssh_string with a simple configuration."""
    config = {
        "Host": "first",
        "User": "foo",
        "Port": "22",
        "UserKnownHostsFile": "/dev/null",
        "StrictHostKeyChecking": "no",
        "PasswordAuthentication": "no",
        "IdentityFile": 'blah',
        "IdentitiesOnly": "yes",
        "LogLevel": "FATAL",
    }
    ssh_string = mech.utils.config_ssh_string(config)
    assert ssh_string == 'Host first\n  User foo\n  Port 22\n  UserKnownHostsFile /dev/null\n  StrictHostKeyChecking no\n  PasswordAuthentication no\n  IdentityFile blah\n  IdentitiesOnly yes\n  LogLevel FATAL\n'  # noqa: E501  pylint: disable=line-too-long


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_save_mechfile_entry_with_empty_mechfile(load_mock, save_mock):
    """Test save_mechfile_entry with no entries in the mechfile."""
    entry = {'first': {'name': 'first'}}
    assert mech.utils.save_mechfile_entry(entry, 'first', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_save_mechfile_entry_with_blank_name(load_mock, save_mock):
    """Test save_mechfile_entry with a blank name."""
    entry = {'first': {'name': 'first'}}
    assert mech.utils.save_mechfile_entry(entry, '', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_save_mechfile_entry_with_name_as_none(load_mock, save_mock):
    """Test save_mechfile_entry with name as None."""
    entry = {'first': {'name': 'first'}}
    assert mech.utils.save_mechfile_entry(entry, None, True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_save_mechfile_entry_twice(load_mock, save_mock):
    """Test save_mechfile_entry multiple times."""
    entry = {'first': {'name': 'first'}}
    assert mech.utils.save_mechfile_entry(entry, 'first', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()
    assert mech.utils.save_mechfile_entry(entry, 'first', True)


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_remove_mechfile_entry_with_empty_mechfile(load_mock, save_mock):
    """Test remove_mechfile_entry with no entries in the mechfile."""
    assert mech.utils.remove_mechfile_entry('first', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


@patch('mech.utils.load_mechfile', return_value={'first': {'name': 'first'}})
@patch('mech.utils.save_mechfile', return_value=True)
def test_remove_mechfile_entry(load_mock, save_mock):
    """Test remove_mechfile_entry."""
    assert mech.utils.remove_mechfile_entry('first', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


def test_parse_vmx():
    """Test parse_vmx."""
    partial_vmx = '''.encoding = "UTF-8"
bios.bootorder  = "hdd,cdrom"
checkpoint.vmstate     = ""

cleanshutdown = "FALSE"
config.version = "8"'''
    expected_vmx = OrderedDict([
        ('.encoding', '"UTF-8"'),
        ('bios.bootorder', '"hdd,cdrom"'),
        ('checkpoint.vmstate', '""'),
        ('cleanshutdown', '"FALSE"'),
        ('config.version', '"8"')
    ])
    a_mock = mock_open(read_data=partial_vmx)
    with patch('builtins.open', a_mock):
        assert mech.utils.parse_vmx(partial_vmx) == expected_vmx
    a_mock.assert_called()


@patch('mech.utils.parse_vmx')
def test_update_vmx_empty(mock_parse_vmx, helpers, capfd):
    """Test update_vmx."""
    expected_vmx = """ethernet0.addresstype = generated
ethernet0.bsdname = en0
ethernet0.connectiontype = nat
ethernet0.displayname = Ethernet
ethernet0.linkstatepropagation.enable = FALSE
ethernet0.pcislotnumber = 32
ethernet0.present = TRUE
ethernet0.virtualdev = e1000
ethernet0.wakeonpcktrcv = FALSE
"""
    mock_parse_vmx.return_value = {}
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        mech.utils.update_vmx('/tmp/first/one.vmx')
        a_mock.assert_called()
        got = helpers.get_mock_data_written(a_mock)
        assert expected_vmx == got
        out, _ = capfd.readouterr()
        assert re.search(r'Added network interface to vmx file', out, re.MULTILINE)


@patch('mech.utils.parse_vmx')
def test_update_vmx_with_a_network_entry(mock_parse_vmx, capfd):
    """Test update_vmx."""
    mock_parse_vmx.return_value = {'ethernet0.present': 'true'}
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        mech.utils.update_vmx('/tmp/first/one.vmx')
        assert not a_mock.called, 'should not have written anything to the vmx file'
        out, _ = capfd.readouterr()
        assert out == ''


@patch('mech.utils.parse_vmx')
def test_update_vmx_with_cpu_and_memory(mock_parse_vmx, helpers, capfd):
    """Test update_vmx."""
    mock_parse_vmx.return_value = {'ethernet0.present': 'true'}
    expected_vmx = '''ethernet0.present = true
numvcpus = "3"
memsize = "1025"
'''
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        mech.utils.update_vmx('/tmp/first/one.vmx', numvcpus=3, memsize=1025)
        a_mock.assert_called()
        got = helpers.get_mock_data_written(a_mock)
        assert expected_vmx == got
        out, _ = capfd.readouterr()
        assert out == ''


def test_build_mechfile_entry_no_location():
    """Test if None is used for location."""
    assert mech.utils.build_mechfile_entry(location=None) == {}


def test_build_mechfile_entry_https_location():
    """Test if location starts with 'https://'."""
    assert mech.utils.build_mechfile_entry(location='https://foo') == {
        'box': None,
        'box_version': None,
        'name': None,
        'provider': None,
        'shared_folders': [{'host_path': '.', 'share_name': 'mech'}],
        'url': 'https://foo'
    }


def test_build_mechfile_entry_http_location():
    """Test if location starts with 'http://'."""
    assert mech.utils.build_mechfile_entry(location='http://foo') == {
        'box': None,
        'box_version': None,
        'name': None,
        'provider': None,
        'shared_folders': [{'host_path': '.', 'share_name': 'mech'}],
        'url':
        'http://foo'
    }


def test_build_mechfile_entry_ftp_location():
    """Test if location starts with 'ftp://'."""
    assert mech.utils.build_mechfile_entry(location='ftp://foo') == {
        'box': None,
        'box_version': None,
        'name': None,
        'provider': None,
        'shared_folders': [{'host_path': '.', 'share_name': 'mech'}],
        'url': 'ftp://foo'
    }


def test_build_mechfile_entry_ftp_location_with_other_values():
    """Test if mechfile_entry is filled out."""
    expected = {
        'box': 'bbb',
        'box_version': 'ccc',
        'name': 'aaa',
        'provider': 'vmware',
        'shared_folders': [{'host_path': '.', 'share_name': 'mech'}],
        'url': 'ftp://foo'
    }
    assert mech.utils.build_mechfile_entry(location='ftp://foo', name='aaa',
                                           box='bbb', box_version='ccc',
                                           provider='vmware') == expected


def test_build_mechfile_entry_file_location_json(catalog):
    """Test if location starts with 'file:' and contains valid json."""

    # Note: Download/format json like this:
    # curl --header 'Accept:application/json' \
    #    'https://app.vagrantup.com/bento/boxes/ubuntu-18.04' | python3 -m json.tool
    expected = {
        'box': 'bento/ubuntu-18.04',
        'box_version': 'aaa',
        'name': 'first',
        'provider': 'vmware',
        'shared_folders': [{'host_path': '.', 'share_name': 'mech'}],
        'url':
        'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/aaa/providers/vmware_desktop.box'
    }
    a_mock = mock_open(read_data=catalog)
    with patch('builtins.open', a_mock):
        actual = mech.utils.build_mechfile_entry(location='file:/tmp/one.json')
        assert expected == actual
    a_mock.assert_called()


def test_build_mechfile_entry_file_location_but_file_not_found():
    """Test if location starts with 'file:' and file does not exist."""
    with patch('builtins.open', mock_open()) as mock_file:
        mock_file.side_effect = SystemExit()
        with raises(SystemExit):
            mech.utils.build_mechfile_entry(location='file:/tmp/one.box')


@patch('requests.get')
def test_build_mechfile_entry_file_location_external_good(mock_requests_get,
                                                          catalog_as_json):
    """Test if location talks to Hashicorp."""
    expected = {
        'box': 'bento/ubuntu-18.04',
        'box_version': 'aaa',
        'name': None,
        'provider': 'vmware',
        'shared_folders': [{'host_path': '.', 'share_name': 'mech'}],
        'url':
        'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/aaa/providers/vmware_desktop.box'
    }
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = catalog_as_json
    actual = mech.utils.build_mechfile_entry(location='bento/ubuntu-18.04')
    mock_requests_get.assert_called()
    assert expected == actual


def test_build_mechfile_entry_file_location_external_bad_location():
    """Test if we do not have a valid location. (must be in form of 'hashiaccount/boxname')."""
    with raises(SystemExit, match=r"Provided box name is not valid"):
        mech.utils.build_mechfile_entry(location='bento')


def test_deL_user_no_instance():
    """Test del_user."""
    with raises(SystemExit, match=r"Need to provide an instance"):
        mech.utils.del_user(None, 'bart')


def test_deL_user_vm_not_created():
    """Test del_user."""
    mock_inst = MagicMock()
    mock_inst.vmx = None
    with raises(SystemExit, match=r"VM must be created"):
        mech.utils.del_user(mock_inst, 'bart')


def test_deL_user_no_username_to_use_for_auth():
    """Test del_user."""
    mock_inst = MagicMock()
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.user = None
    with raises(SystemExit, match=r"A user is required"):
        mech.utils.del_user(mock_inst, 'bart')


def test_deL_user_no_user_provided():
    """Test del_user."""
    mock_inst = MagicMock()
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.user = 'bob'
    with raises(SystemExit, match=r"A username to delete is required"):
        mech.utils.del_user(mock_inst, None)


@patch('mech.utils.ssh', return_value='')
def test_deL_user(mock_ssh):
    """Test del_user."""
    mock_inst = MagicMock()
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.user = 'bob'
    mech.utils.del_user(mock_inst, 'homer')


def test_provision_no_instance():
    """Test provisioning."""
    with raises(SystemExit, match=r"Need to provide an instance to provision"):
        mech.utils.provision(instance=None, show=None)


def test_provision_no_vmx():
    """Test provisioning."""
    mock_inst = MagicMock()
    mock_inst.vmx = None
    mock_inst.provider = 'vmware'
    with raises(SystemExit, match=r"Need to provide vmx.*"):
        mech.utils.provision(instance=mock_inst, show=None)


def test_provision_no_vbox():
    """Test provisioning."""
    mock_inst = MagicMock()
    mock_inst.vbox = None
    mock_inst.provider = 'virtualbox'
    with raises(SystemExit, match=r"Need to provide vbox.*"):
        mech.utils.provision(instance=mock_inst, show=None)


@patch('mech.utils.scp', return_value='')
def test_provision_file(mock_scp):
    """Test provision_file"""
    mock_inst = MagicMock()
    mech.utils.provision_file(mock_inst, 'somefile', 'somedest')
    mock_scp.assert_called()


@patch('mech.utils.ssh')
def test_create_tempfile_in_guest(mock_ssh):
    """Test create_tempfile_in_guest"""
    expected = '/tmp/foo123'
    mock_ssh.return_value = None, expected, None
    mock_inst = MagicMock()
    got = mech.utils.create_tempfile_in_guest(mock_inst)
    mock_ssh.assert_called()
    assert got == expected


@patch('mech.vmrun.VMrun.installed_tools')
def test_provision_file_show(mock_installed_tools, capfd):
    """Test provisioning."""
    mock_installed_tools.return_value = "running"
    config = [
        {
            "type": "file",
            "source": "file1.txt",
            "destination": "/tmp/file1.txt",
        },
    ]
    mock_inst = MagicMock()
    mock_inst.name = 'first'
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.provision = config
    mech.utils.provision(instance=mock_inst, show=True)
    out, _ = capfd.readouterr()
    assert re.search(r'instance:', out, re.MULTILINE)


def test_provision_which_has_shell_show_only(capfd):
    """Test provisioning."""
    config = [
        {
            "type": "shell",
            "path": "file1.sh",
            "args": [
                "a=1",
                "b=true",
            ],
        },
    ]
    mock_inst = MagicMock()
    mock_inst.name = 'first'
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.provision = config
    mech.utils.provision(instance=mock_inst, show=True)
    out, _ = capfd.readouterr()
    assert re.search(r' instance:', out, re.MULTILINE)


@patch('mech.utils.provision_shell', return_value=None)
def test_provision_that_has_shell_with_issue(mock_provision_shell,
                                             capfd):
    """Test provisioning."""
    config = [
        {
            "type": "shell",
            "path": "file1.sh",
            "args": [
                "a=1",
                "b=true",
            ],
        },
    ]
    mock_inst = MagicMock()
    mock_inst.name = 'first'
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.provision = config
    mech.utils.provision(instance=mock_inst, show=None)
    out, _ = capfd.readouterr()
    mock_provision_shell.assert_called()
    assert re.search(r'Not Provisioned', out, re.MULTILINE)


def test_provision_with_unknown_type(capfd):
    """Test provisioning."""
    config = [
        {
            "type": "foo",
        },
    ]
    mock_inst = MagicMock()
    mock_inst.name = 'first'
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.provision = config
    mech.utils.provision(instance=mock_inst, show=None)
    out, _ = capfd.readouterr()
    assert re.search(r'Not Provisioned', out, re.MULTILINE)


@patch('mech.utils.ssh', return_value=[True, True, True])
@patch('mech.utils.scp', return_value=True)
@patch('os.path.isfile', return_value=True)
@patch('mech.utils.create_tempfile_in_guest', return_value='/tmp/foo')
def test_provision_shell(mock_create_tempfile, mock_isfile,
                         mock_scp, mock_ssh, capfd,
                         mechfile_one_entry_with_auth_and_mech_use):
    """Test provision_shell."""
    inst = mech.mech_instance.MechInstance('first',
                                           mechfile_one_entry_with_auth_and_mech_use)
    some_vmx = '/tmp/first/some.vmx'
    inst.vmx = some_vmx
    inst.created = True
    mech.utils.provision_shell(inst, inline=False, script_path='file1.sh', args=None)
    out, _ = capfd.readouterr()
    mock_create_tempfile.assert_called()
    mock_isfile.assert_called()
    mock_scp.assert_called()
    mock_ssh.assert_called()
    assert re.search(r'Configuring script', out, re.MULTILINE)
    assert re.search(r'Configuring environment', out, re.MULTILINE)
    assert re.search(r'Executing program', out, re.MULTILINE)


@patch('mech.utils.ssh', return_value=None)
@patch('mech.utils.scp', return_value=True)
@patch('os.path.isfile', return_value=True)
@patch('mech.utils.create_tempfile_in_guest', return_value='/tmp/foo')
def test_provision_shell_make_executable_fails(mock_create_tempfile, mock_isfile,
                                               mock_scp, mock_ssh, capfd,
                                               mechfile_one_entry_with_auth_and_mech_use):
    """Test provision_shell."""
    inst = mech.mech_instance.MechInstance('first',
                                           mechfile_one_entry_with_auth_and_mech_use)
    some_vmx = '/tmp/first/some.vmx'
    inst.vmx = some_vmx
    inst.created = True
    mech.utils.provision_shell(inst, inline=False, script_path='file1.sh', args=None)
    out, _ = capfd.readouterr()
    mock_create_tempfile.assert_called()
    mock_isfile.assert_called()
    mock_scp.assert_called()
    mock_ssh.assert_called()
    assert re.search(r'Configuring script', out, re.MULTILINE)
    assert re.search(r'Configuring environment', out, re.MULTILINE)
    assert re.search(r'Warning: Could not configure script', out, re.MULTILINE)


@patch('requests.get')
@patch('mech.utils.ssh', return_value=[True, True, True])
@patch('mech.utils.scp', return_value=True)
@patch('os.path.isfile', return_value=False)
@patch('mech.utils.create_tempfile_in_guest', return_value='/tmp/foo')
def test_provision_shell_from_http(mock_create_tempfile, mock_isfile,
                                   mock_scp, mock_ssh, mock_requests_get,
                                   capfd,
                                   mechfile_one_entry_with_auth_and_mech_use):
    """Test provision_shell."""
    inst = mech.mech_instance.MechInstance('first',
                                           mechfile_one_entry_with_auth_and_mech_use)
    some_vmx = '/tmp/first/some.vmx'
    inst.vmx = some_vmx
    inst.created = True
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.raise_for_status.return_value = None
    mock_requests_get.return_value.read.return_value = 'echo hello'
    mech.utils.provision_shell(inst, inline=False, script_path='http://example.com/file1.sh',
                               args=None)
    out, _ = capfd.readouterr()
    mock_create_tempfile.assert_called()
    mock_isfile.assert_called()
    mock_scp.assert_called()
    mock_ssh.assert_called()
    mock_requests_get.assert_called()
    assert re.search(r'Configuring script', out, re.MULTILINE)
    assert re.search(r'Configuring environment', out, re.MULTILINE)
    assert re.search(r'Executing program', out, re.MULTILINE)


@patch('mech.utils.ssh', return_value=[True, True, True])
@patch('mech.utils.scp', return_value=None)
@patch('os.path.isfile', return_value=True)
@patch('mech.utils.create_tempfile_in_guest', return_value='/tmp/foo')
def test_provision_shell_cannot_copy_file(mock_create_tempfile, mock_isfile,
                                          mock_scp, mock_ssh,
                                          capfd,
                                          mechfile_one_entry_with_auth_and_mech_use):
    """Test provision_shell."""
    inst = mech.mech_instance.MechInstance('first',
                                           mechfile_one_entry_with_auth_and_mech_use)
    some_vmx = '/tmp/first/some.vmx'
    inst.vmx = some_vmx
    inst.created = True
    mech.utils.provision_shell(inst, inline=False, script_path='file1.sh', args=None)
    out, _ = capfd.readouterr()
    mock_create_tempfile.assert_called()
    mock_isfile.assert_called()
    mock_ssh.assert_called()
    mock_scp.assert_called()
    assert re.search(r'Configuring script', out, re.MULTILINE)
    assert re.search(r'Warning: Could not copy file to guest', out, re.MULTILINE)


@patch('os.environ')
def test_get_fallback_executable_no_path_in_environ(mock_os_environ):
    """Weird case where PATH is is not in the environment."""
    mock_os_environ.return_value = ''
    assert mech.utils.get_fallback_executable() is None


def test_run_pyinfra_script_no_host():
    """Test pyinfra_script"""
    assert mech.utils.run_pyinfra_script(host=None, username=None) is None


def test_run_pyinfra_script_no_username():
    """Test pyinfra_script"""
    assert mech.utils.run_pyinfra_script(host='foo', username=None) is None


def test_run_pyinfra_script_script_is_none():
    """Test pyinfra_script"""
    assert mech.utils.run_pyinfra_script(host='foo', username='vagrant') is None


def test_run_pyinfra_script_script_no_script():
    """Test pyinfra_script"""
    assert mech.utils.run_pyinfra_script(host='foo', username='vagrant', script_path='') is None


@patch('os.path.exists', return_value=False)
def test_run_pyinfra_script_script_not_found(mock_path_exists):
    """Test pyinfra_script"""
    assert mech.utils.run_pyinfra_script(host='foo', username='vagrant',
                                         script_path='/tmp/file1.py') is None
    mock_path_exists.assert_called()


@patch('os.path.exists', return_value=True)
def test_run_pyinfra_script_script_does_not_end_in_py(mock_path_exists):
    """Test pyinfra_script"""
    assert mech.utils.run_pyinfra_script(host='foo', username='vagrant',
                                         script_path='/tmp/file1') is None
    mock_path_exists.assert_called()


@patch('mech.utils.pyinfra_installed', return_value=False)
@patch('os.path.exists', return_value=True)
def test_run_pyinfra_script_pyinfra_not_installed(mock_path_exists, mock_pyinfra_installed):
    """Test pyinfra_script"""
    assert mech.utils.run_pyinfra_script(host='foo', username='vagrant',
                                         script_path='/tmp/file1.py') is None
    mock_path_exists.assert_called()
    mock_pyinfra_installed.assert_called()


@patch('mech.utils.pyinfra_installed', return_value=True)
@patch('os.path.exists', return_value=True)
def test_run_pyinfra_script_pyinfra_success(mock_path_exists, mock_pyinfra_installed):
    """Test pyinfra_script"""
    mock_subprocess = MagicMock()
    mock_subprocess.return_value = subprocess.CompletedProcess(args='',
                                                               returncode=0,
                                                               stdout=b'',
                                                               stderr=b'')
    with patch('subprocess.run', mock_subprocess):
        return_code, stdout, stderr = mech.utils.run_pyinfra_script(host='foo', username='vagrant',
                                                                    script_path='/tmp/file1.py')
        assert return_code == 0
        assert stdout == ''
        assert stderr == ''
        mock_path_exists.assert_called()
        mock_pyinfra_installed.assert_called()
        mock_subprocess.assert_called()


@patch('mech.utils.pyinfra_installed', return_value=True)
@patch('os.path.exists', return_value=True)
def test_run_pyinfra_script_pyinfra_failed(mock_path_exists, mock_pyinfra_installed):
    """Test pyinfra_script"""
    mock_subprocess = MagicMock()
    mock_subprocess.return_value = subprocess.CompletedProcess(args='',
                                                               returncode=1,
                                                               stdout=b'some output',
                                                               stderr=b'some error')
    with patch('subprocess.run', mock_subprocess):
        return_code, stdout, stderr = mech.utils.run_pyinfra_script(host='foo', username='vagrant',
                                                                    script_path='/tmp/file1.py')
        assert return_code == 1
        assert stdout == 'some output'
        assert stderr == 'some error'
        mock_path_exists.assert_called()
        mock_pyinfra_installed.assert_called()
        mock_subprocess.assert_called()


def test_pyinfra_installed():
    """Test pyinfra_installed"""
    mock_subprocess = MagicMock()
    mock_subprocess.return_value = subprocess.CompletedProcess(args='', returncode=0)
    with patch('subprocess.run', mock_subprocess):
        assert mech.utils.pyinfra_installed()


def test_pyinfra_not_installed():
    """Test pyinfra_installed"""
    mock_subprocess = MagicMock()
    mock_subprocess.return_value = subprocess.CompletedProcess(args='', returncode=127)
    with patch('subprocess.run', mock_subprocess):
        assert not mech.utils.pyinfra_installed()


@patch('os.path.exists')
def test_get_fallback_executable(mock_os_path_exists):
    """Find vmrun in PATH."""
    mock_os_path_exists.return_value = True
    with patch.dict('os.environ', {'PATH': '/tmp:/tmp2'}):
        got = mech.utils.get_fallback_executable()
    expected = '/tmp/vmrun'
    assert got == expected
    mock_os_path_exists.assert_called()


@patch('os.path.exists')
def test_darwin_executable_when_installed(mock_os_path_exists):
    """Find vmrun in PATH."""
    expected = '/Applications/VMware Fusion.app/Contents/Library/vmrun'
    mock_os_path_exists.return_value = True
    got = mech.utils.get_darwin_executable()
    assert expected == got
    mock_os_path_exists.assert_called()


@patch('os.path.exists')
def test_darwin_executable_when_not_installed(mock_os_path_exists):
    """Find vmrun in PATH."""
    # deal with a different file returns a different mocked value
    def side_effect(filename):
        if filename == '/Applications/VMware Fusion.app/Contents/Library/vmrun':
            return False
        else:
            return True
    mock_os_path_exists.side_effect = side_effect
    expected = '/tmp/vmrun'
    with patch.dict('os.environ', {'PATH': '/tmp:/tmp2'}):
        got = mech.utils.get_darwin_executable()
    assert expected == got


@patch('os.path.exists')
def test_get_fallback_executable_when_exe(mock_os_path_exists):
    """Find vmrun.exe in PATH."""
    # deal with a different file returns a different mocked value
    def side_effect(filename):
        if filename == '/tmp/vmrun.exe':
            return True
        else:
            return False
    mock_os_path_exists.side_effect = side_effect
    expected = '/tmp/vmrun.exe'
    with patch.dict('os.environ', {'PATH': '/tmp:/tmp2'}):
        got = mech.utils.get_fallback_executable()
    assert expected == got


def test_catalog_to_mechfile_when_empty_catalog():
    """Test catalog_to_mechfile."""
    catalog = {}
    with raises(SystemExit):
        mech.utils.catalog_to_mechfile(catalog)


@patch('mech.utils.locate')
def test_init_box_cannot_find_valid_box(mock_locate):
    """Test init_box."""
    mock_locate.return_value = None
    with raises(SystemExit):
        mech.utils.init_box(name='first')


@patch('mech.utils.makedirs', return_value=True)
@patch('mech.utils.add_box')
@patch('mech.utils.locate')
def test_init_box_cannot_extract_box(mock_locate, mock_add_box, mock_makedirs):
    """Test init_box."""
    a_mock = MagicMock()
    another_mock = MagicMock()
    yet_another_mock = MagicMock()
    yet_another_mock.returncode = 0
    yet_another_mock.return_value = 'someoutput', None
    another_mock.communicate = yet_another_mock
    another_mock.communicate.returncode = 0
    another_mock.returncode = 0
    a_mock.return_value = another_mock
    a_mock.returncode = 0
    mock_locate.return_value = None
    mock_add_box.return_value = 'bento', '1.23', 'ubuntu'
    with raises(SystemExit, match=r"Cannot extract box"):
        with patch('subprocess.Popen', a_mock):
            mech.utils.init_box(name='first', box='bento/ubuntu', box_version='1.23')


@patch('tarfile.open')
@patch('mech.utils.makedirs', return_value=True)
@patch('mech.utils.add_box')
@patch('mech.utils.locate')
def test_init_box_when_no_vmx_after_extraction(mock_locate, mock_add_box,
                                               mock_makedirs, mock_tarfile_open):
    """Test init_box."""
    mock_subprocess_popen = MagicMock()
    mock_tarfile_open = MagicMock()
    yet_another_mock = MagicMock()
    yet_another_mock.returncode = 0
    yet_another_mock.return_value = 'someoutput', None
    mock_subprocess_popen.returncode = 0
    mock_locate.return_value = False
    mock_add_box.return_value = 'bento', '1.23', 'ubuntu'
    with raises(SystemExit, match=r"Cannot locate a VMX"):
        with patch('subprocess.Popen', mock_subprocess_popen):
            mech.utils.init_box(name='first', box='bento/ubuntu', box_version='1.23')
            mock_locate.assert_called()
            mock_add_box.assert_called()
            mock_makedirs.assert_called()
            mock_tarfile_open.assert_called()


@patch('mech.utils.update_vmx', return_value='/tmp/first/some.vmx')
@patch('tarfile.open')
@patch('mech.utils.makedirs', return_value=True)
@patch('mech.utils.add_box')
@patch('mech.utils.locate')
def test_init_box_success(mock_locate, mock_add_box, mock_makedirs,
                          mock_tarfile_open, mock_update_vmx):
    """Test init_box."""
    mock_subprocess_popen = MagicMock()
    mock_tarfile_open = MagicMock()
    mock_tarfile_open.returncode = 0
    yet_another_mock = MagicMock()
    yet_another_mock.returncode = 0
    yet_another_mock.return_value = 'someoutput', None
    mock_subprocess_popen.returncode = 0
    # pytest tip: If you need to mock the same function multiple times,
    # put it into a list like the next line. Then mech.utils.locate() is
    # called the first time, it returns False. Subsequent two calls
    # return True. Mind blown.
    mock_locate.side_effect = [False, True, True]
    mock_add_box.return_value = 'bento', '1.23', 'ubuntu'
    with patch('subprocess.Popen', mock_subprocess_popen):
        mech.utils.init_box(name='first', box='bento/ubuntu', box_version='1.23')
        mock_locate.assert_called()
        mock_add_box.assert_called()
        mock_makedirs.assert_called()
        mock_update_vmx.assert_called()


@patch('mech.utils.mech_dir')
@patch('mech.utils.copyfile')
@patch('mech.utils.makedirs')
@patch('mech.utils.tar_cmd')
def test_add_box_file(mock_tar_cmd, mock_makedirs, mock_copyfile, mock_mech_dir):
    """Test add_box_file."""
    mock_tarfile_open = MagicMock()
    mock_tarfile_open.returncode = 0
    mock_tarfile_open.return_value.getnames.return_value = ['aaa', 'some.vmx']
    mock_tar_cmd.return_value = None
    mock_mech_dir.return_value = '/tmp'
    with patch('tarfile.open', mock_tarfile_open, create=True):
        box, box_version = mech.utils.add_box_file(box='bento/ubuntu',
                                                   box_version='1.23',
                                                   filename='/tmp/foo.box')
        mock_tarfile_open.assert_called()
        mock_tar_cmd.assert_called()
        mock_makedirs.assert_called()
        mock_copyfile.assert_called()
        assert box == '/tmp/boxes/bento/ubuntu/1.23/foo.box'
        assert box_version == '1.23'


@patch('mech.utils.tar_cmd')
def test_add_box_file_do_not_save(mock_tar_cmd):
    """Test add_box_file."""
    mock_tarfile_open = MagicMock()
    mock_tarfile_open.returncode = 0
    mock_tarfile_open.return_value.getnames.return_value = ['aaa', 'some.vmx']
    mock_tar_cmd.return_value = None
    with patch('tarfile.open', mock_tarfile_open, create=True):
        box, box_version = mech.utils.add_box_file(box='bento/ubuntu',
                                                   box_version='1.23',
                                                   filename='/tmp/foo.box',
                                                   save=False)
        mock_tarfile_open.assert_called()
        mock_tar_cmd.assert_called()
        assert box == '/tmp/foo.box'
        assert box_version == '1.23'


@patch('mech.utils.tar_cmd')
def test_add_box_file_that_has_leading_slashes(mock_tar_cmd):
    """Test add_box_file."""
    mock_tarfile_open = MagicMock()
    mock_tarfile_open.returncode = 0
    mock_tarfile_open.return_value.getnames.return_value = ['/aaa', '/some.vmx']
    mock_tar_cmd.return_value = None
    with raises(SystemExit, match=r"This box is comprised of filenames starting with"):
        with patch('tarfile.open', mock_tarfile_open, create=True):
            mech.utils.add_box_file(box='bento/ubuntu', box_version='1.23', filename='/tmp/foo.box')


def test_add_mechfile_with_empty_mechfile():
    """Test add_mechfile."""
    mech.utils.add_mechfile(mechfile_entry={})


@patch('mech.utils.add_box_file', return_value='')
def test_add_mechfile_with_boxfile(mock_add_box_file, mechfile_one_entry_with_file):
    """Test add_mechfile."""
    mech.utils.add_mechfile(mechfile_entry=mechfile_one_entry_with_file)
    mock_add_box_file.assert_called()


@patch('requests.get')
@patch('mech.utils.locate')
def test_add_box_url(mock_locate, mock_requests_get, catalog_as_json):
    """Test init_box."""
    mock_locate.return_value = False
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = catalog_as_json
    got = mech.utils.add_box_url(name='first', box='abox', box_version='aver', url='')
    assert got is None


@patch('os.getlogin', return_value='bob')
@patch('os.path.expanduser', return_value='/home/bob/id_rsa.pub')
def test_get_info_for_auth(mock_path_expanduser, mock_getlogin):
    """Test get_info_for_auth."""
    expected = {'auth': {'username': 'bob', 'pub_key': '/home/bob/id_rsa.pub', 'mech_use': False}}
    got = mech.utils.get_info_for_auth()
    assert got == expected


@patch('sys.platform', return_value='atari')
def test_get_provider(mock_sys_platform):
    """Test get_provider simulating an Atari 800XL."""
    a_mock = MagicMock()
    another_mock = MagicMock()
    yet_another_mock = MagicMock()
    yet_another_mock.returncode = 0
    another_mock.communicate = yet_another_mock
    another_mock.communicate.returncode = 0
    another_mock.returncode = 0
    a_mock.return_value = another_mock
    a_mock.returncode = 0
    with patch('subprocess.Popen', a_mock):
        provider = mech.utils.get_provider('/tmp/vmrun')
        assert provider == 'ws'


@patch('sys.platform', return_value='nt')
def test_get_provider_simulate_win(mock_sys_platform):
    """Test get_provider simulating windows."""
    a_mock = MagicMock()
    another_mock = MagicMock()
    yet_another_mock = MagicMock()
    yet_another_mock.returncode = 0
    another_mock.communicate = yet_another_mock
    another_mock.communicate.returncode = 0
    another_mock.returncode = 0
    a_mock.return_value = another_mock
    a_mock.returncode = 0
    with patch('subprocess.Popen', a_mock):
        provider = mech.utils.get_provider('/tmp/vmrun')
        assert provider == 'ws'


def test_valid_provider():
    """Test valid_provider."""
    assert mech.utils.valid_provider('vmware')
    assert mech.utils.valid_provider('virtualbox')
    assert not mech.utils.valid_provider(None)
    assert not mech.utils.valid_provider('')
    assert not mech.utils.valid_provider('atari')


def test_vm_ready_based_on_state():
    """Test vm_ready_based_on_state."""
    assert mech.utils.vm_ready_based_on_state('powered on')
    assert mech.utils.vm_ready_based_on_state('running')
    assert mech.utils.vm_ready_based_on_state('started')
    assert not mech.utils.vm_ready_based_on_state('unkown')
    assert not mech.utils.vm_ready_based_on_state('paused')
    assert not mech.utils.vm_ready_based_on_state('power off')
