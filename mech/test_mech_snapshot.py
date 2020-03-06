# Copyright (c) 2020 Mike Kinney

"""Unit tests for 'mech snapshot'."""
import re

from unittest.mock import patch
from click.testing import CliRunner

from mech.mech_cli import cli


@patch('mech.utils.load_mechfile')
@patch('os.getcwd')
def test_mech_snapshot_list_no_mechdir(mock_os_getcwd, mock_load_mechfile,
                                       mechfile_two_entries):
    """Test 'mech snapshot list' with no '.mech' directory."""
    mock_load_mechfile.return_value = mechfile_two_entries
    mock_os_getcwd.return_value = '/tmp'
    runner = CliRunner()
    with patch('os.walk') as mock_walk:
        # root, dirs, files
        mock_walk.return_value = [('./tmp', [], []), ]
        result = runner.invoke(cli, ['--debug', 'snapshot', 'list'])
        mock_walk.assert_called()
        mock_load_mechfile.assert_called()
        # ensure a header prints out
        assert re.search(r'Snapshots', result.output, re.MULTILINE)


SNAPSHOT_LIST_WITHOUT_SNAPSHOTS = """Snapshots for instance:first
Total snapshots: 0
Snapshots for instance:second
Instance (second) is not created."""
@patch('mech.vmrun.VMrun.list_snapshots', return_value=SNAPSHOT_LIST_WITHOUT_SNAPSHOTS)
@patch('mech.utils.load_mechfile')
@patch('os.getcwd')
def test_mech_snapshot_list_no_snapshots(mock_os_getcwd, mock_load_mechfile,
                                         mock_list_snapshots,
                                         mechfile_two_entries):
    """Test 'mech snapshot list' without any snapshots."""
    mock_load_mechfile.return_value = mechfile_two_entries
    mock_os_getcwd.return_value = '/tmp'
    runner = CliRunner()
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ('/tmp', ['first'], []),
            ('/tmp/first', [], ['some.vmx']),
        ]

        # with no args
        result = runner.invoke(cli, ['--debug', 'snapshot', 'list'])
        mock_walk.assert_called()
        mock_load_mechfile.assert_called()
        mock_list_snapshots.assert_called()
        assert re.search(r'Total snapshots: 0', result.output, re.MULTILINE)
        assert re.search(r'Instance \(second\) is not created.', result.output, re.MULTILINE)

        # single instance
        result = runner.invoke(cli, ['--debug', 'snapshot', 'list', 'first'])
        mock_load_mechfile.assert_called()
        mock_list_snapshots.assert_called()
        assert re.search(r'Total snapshots: 0', result.output, re.MULTILINE)


SNAPSHOT_LIST_WITH_SNAPSHOT = """Snapshots for instance:first
Total snapshots: 1
snap1
Snapshots for instance:second
Instance (second) is not created."""
@patch('mech.vmrun.VMrun.list_snapshots', return_value=SNAPSHOT_LIST_WITH_SNAPSHOT)
@patch('mech.utils.load_mechfile')
@patch('os.getcwd')
def test_mech_snapshot_list_with_snapshot(mock_os_getcwd, mock_load_mechfile,
                                          mock_list_snapshots,
                                          mechfile_two_entries):
    """Test 'mech snapshot list' with a snapshots."""
    mock_load_mechfile.return_value = mechfile_two_entries
    mock_os_getcwd.return_value = '/tmp'
    runner = CliRunner()
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ('/tmp', ['first'], []),
            ('/tmp/first', [], ['some.vmx']),
        ]

        # with no args
        result = runner.invoke(cli, ['--debug', 'snapshot', 'list'])
        mock_walk.assert_called()
        mock_load_mechfile.assert_called()
        mock_list_snapshots.assert_called()
        assert re.search(r'Total snapshots: 1', result.output, re.MULTILINE)
        assert re.search(r'Instance \(second\) is not created.', result.output, re.MULTILINE)

        # single instance
        result = runner.invoke(cli, ['--debug', 'snapshot', 'list', 'first'])
        mock_load_mechfile.assert_called()
        mock_list_snapshots.assert_called()
        assert re.search(r'Total snapshots: 1', result.output, re.MULTILINE)


@patch('mech.vmrun.VMrun.delete_snapshot')
@patch('mech.vmrun.VMrun.list_snapshots', return_value=SNAPSHOT_LIST_WITH_SNAPSHOT)
@patch('mech.utils.load_mechfile')
@patch('os.getcwd')
def test_mech_snapshot_delete_snapshot(mock_os_getcwd, mock_load_mechfile,
                                       mock_list_snapshots, mock_delete_snapshot,
                                       mechfile_two_entries):
    """Test 'mech snapshot delete'."""
    mock_load_mechfile.return_value = mechfile_two_entries
    mock_os_getcwd.return_value = '/tmp'
    runner = CliRunner()
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ('/tmp', ['first'], []),
            ('/tmp/first', [], ['some.vmx']),
        ]

        result = runner.invoke(cli, ['snapshot', 'list', 'first'])
        mock_load_mechfile.assert_called()
        mock_list_snapshots.assert_called()
        mock_delete_snapshot.return_value = None
        assert re.search(r'Total snapshots: 1', result.output, re.MULTILINE)

        result = runner.invoke(cli, ['snapshot', 'delete', 'snap2', 'first'])
        mock_delete_snapshot.assert_called()
        mock_list_snapshots.assert_called()
        assert re.search(r'Cannot delete', result.output, re.MULTILINE)

        # Note: delete_snapshots return None if could not delete, or '' if it could
        mock_delete_snapshot.return_value = ''
        result = runner.invoke(cli, ['--debug', 'snapshot', 'delete', 'snap1', 'first'])
        mock_delete_snapshot.assert_called()
        assert re.search(r' deleted', result.output, re.MULTILINE)

        mock_list_snapshots.return_value = SNAPSHOT_LIST_WITHOUT_SNAPSHOTS
        result = runner.invoke(cli, ['snapshot', 'list', 'first'])
        mock_list_snapshots.assert_called()
        mock_delete_snapshot.assert_called()
        assert re.search(r'Total snapshots: 0', result.output, re.MULTILINE)


@patch('mech.utils.load_mechfile')
def test_mech_snapshot_delete_snapshot_virtualbox(mock_load_mechfile,
                                                  mechfile_one_entry_virtualbox):
    """Test 'mech snapshot delete'."""
    mock_load_mechfile.return_value = mechfile_one_entry_virtualbox
    runner = CliRunner()
    result = runner.invoke(cli, ['snapshot', 'delete', 'snap1', 'first'])
    mock_load_mechfile.assert_called()
    assert re.search(r'Not yet implemented', result.output, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vbox')
def test_mech_snapshot_list_snapshot_virtualbox(mock_locate, mock_load_mechfile,
                                                mechfile_one_entry_virtualbox):
    """Test 'mech snapshot list'."""
    mock_load_mechfile.return_value = mechfile_one_entry_virtualbox
    runner = CliRunner()
    result = runner.invoke(cli, ['--debug', 'snapshot', 'list'])
    mock_load_mechfile.assert_called()
    mock_locate.assert_called()
    assert re.search(r'Not yet implemented', result.output, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vbox')
def test_mech_snapshot_save_snapshot_virtualbox(mock_locate, mock_load_mechfile,
                                                mechfile_one_entry_virtualbox):
    """Test 'mech snapshot list'."""
    mock_load_mechfile.return_value = mechfile_one_entry_virtualbox
    runner = CliRunner()
    result = runner.invoke(cli, ['--debug', 'snapshot', 'save', 'snap1', 'first'])
    mock_load_mechfile.assert_called()
    mock_locate.assert_called()
    assert re.search(r'Not yet implemented', result.output, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_snapshot_list_not_created(mock_locate, mock_load_mechfile,
                                        mechfile_one_entry):
    """Test 'mech snapshot list' when vm is not created."""
    mock_load_mechfile.return_value = mechfile_one_entry
    runner = CliRunner()
    result = runner.invoke(cli, ['snapshot', 'list', 'first'])
    mock_load_mechfile.assert_called()
    mock_locate.assert_called()
    assert re.search(r'not created', result.output, re.MULTILINE)


@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value=None)
def test_mech_snapshot_save_not_created(mock_locate, mock_load_mechfile,
                                        mechfile_one_entry):
    """Test 'mech snapshot save' when vm is not created."""
    mock_load_mechfile.return_value = mechfile_one_entry
    runner = CliRunner()
    result = runner.invoke(cli, ['snapshot', 'save', 'snap1', 'first'])
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'not created', result.output, re.MULTILINE)


@patch('mech.vmrun.VMrun.snapshot', return_value='Snapshot (snap1) on VM (first) taken')
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_snapshot_save_success(mock_locate, mock_load_mechfile,
                                    mock_snapshot, mechfile_one_entry):
    """Test 'mech snapshot save' successful."""
    mock_load_mechfile.return_value = mechfile_one_entry
    runner = CliRunner()
    result = runner.invoke(cli, ['snapshot', 'save', 'snap1', 'first'])
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_snapshot.assert_called()
    assert re.search(r' taken', result.output, re.MULTILINE)


@patch('mech.vmrun.VMrun.snapshot', return_value=None)
@patch('mech.utils.load_mechfile')
@patch('mech.utils.locate')
def test_mech_snapshot_save_failure(mock_locate, mock_load_mechfile,
                                    mock_vmrun_snapshot, mechfile_one_entry):
    """Test 'mech snapshot save' failure."""
    mock_locate.return_value = '/tmp/first/some.vmx'
    mock_load_mechfile.return_value = mechfile_one_entry
    runner = CliRunner()
    result = runner.invoke(cli, ['snapshot', 'save', 'snap1', 'first'])
    assert re.search('Warning: Could not take snapshot', '{}'.format(result))
