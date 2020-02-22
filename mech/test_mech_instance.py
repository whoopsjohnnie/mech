# Copyright (c) 2020 Mike Kinney

"""mech tests"""
from unittest.mock import patch
from pytest import raises

import mech.command
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
