# Copyright (c) 2020 Mike Kinney

"""mech tests"""
from unittest.mock import patch
from pytest import raises

import mech.mech
import mech.vmrun
import mech.mech_instance


def test_mech_instance_name_not_being_in_instance():
    """Test mech instance class."""
    with raises(SystemExit):
        mech.mech.MechInstance('first', {})


@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value="192.168.1.100")
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_instance(mock_locate, mock_get_ip_address,
                       mechfile_one_entry_with_auth_and_mech_use):
    """Test mech instance class."""
    inst = mech.mech.MechInstance('first', mechfile_one_entry_with_auth_and_mech_use)
    mock_locate.assert_called()
    print('inst.ip:{}'.format(inst.ip))
    inst.config_ssh()
    mock_get_ip_address.assert_called()


@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value="192.168.1.100")
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_instance_get_ip(mock_locate, mock_get_ip_address,
                              mechfile_one_entry_with_auth_and_mech_use):
    """Test get_ip method."""
    inst = mech.mech.MechInstance('first', mechfile_one_entry_with_auth_and_mech_use)
    ip = '192.168.2.112'
    inst.ip = ip
    assert inst.get_ip() == ip
    mock_locate.assert_called()


@patch('mech.utils.get_fallback_executable', return_value='/tmp/VBoxManage')
@patch('mech.vbm.VBoxManage.vm_state', return_value="running")
@patch('mech.utils.locate', return_value='/tmp/first/some.vbox')
def test_mech_instance_get_vm_state_virtualbox(mock_locate, mock_vm_state,
                                               mock_fallback,
                                               mechfile_one_entry_virtualbox):
    """Test get_vm_state method."""
    inst = mech.mech.MechInstance('first', mechfile_one_entry_virtualbox)
    assert inst.get_vm_state() == "running"
    mock_locate.assert_called()


@patch('mech.utils.get_fallback_executable', return_value='/tmp/VBoxManage')
@patch('mech.vbm.VBoxManage.get_vm_info', return_value="some output")
@patch('mech.utils.locate', return_value='/tmp/first/some.vbox')
def test_mech_instance_get_vm_info(mock_locate, mock_get_vm_info,
                                   mock_fallback,
                                   mechfile_one_entry_virtualbox):
    """Test get_vm_info method."""
    inst = mech.mech.MechInstance('first', mechfile_one_entry_virtualbox)
    assert inst.get_vm_info() == "some output"
    mock_locate.assert_called()
    mock_get_vm_info.assert_called()


# Note: We need the get_fallback_executable in some of these tests as
# the github tests are run on instances that do not have either vmware nor
# virtualbox installed. So, we have to "fake" finding the executable
# so the test will run. We cannot assert_called() these mocks as they
# only run when no providers are installed.
@patch('mech.vmrun.VMrun.installed_tools', return_value='running')
@patch('mech.utils.get_fallback_executable', return_value='/tmp/vmrun')
@patch('mech.utils.get_provider', return_value='fusion')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_instance_get_tools_state(mock_locate, mock_get_provider, mock_fallback,
                                       mock_installed_tools, mechfile_one_entry):
    """Test get_tools_state method."""
    inst = mech.mech.MechInstance('first', mechfile_one_entry)
    inst.tools_state = None
    assert inst.get_tools_state() == 'running'
    mock_locate.assert_called()
    mock_installed_tools.assert_called()


@patch('mech.utils.get_fallback_executable', return_value='/tmp/vmrun')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_instance_get_tools_state_silly(mock_locate, mock_fallback,
                                             mechfile_one_entry):
    """Test get_tools_state method."""
    inst = mech.mech.MechInstance('first', mechfile_one_entry)
    # just for code coverage
    inst.tools_state = 'running'
    assert inst.get_tools_state() == 'running'
    mock_locate.assert_called()


@patch('mech.utils.get_fallback_executable', return_value='/tmp/vmrun')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_instance_winrm_raw_config_no_ip(mock_locate, mock_fallback,
                                              mechfile_one_entry):
    """Test winrm_raw_config method."""
    inst = mech.mech.MechInstance('first', mechfile_one_entry)
    with raises(SystemExit):
        with patch.object(mech.mech_instance.MechInstance,
                          'get_ip', return_value=None):
            assert inst.winrm_raw_config()
