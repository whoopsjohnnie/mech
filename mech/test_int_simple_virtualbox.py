# Copyright (c) 2020 Mike Kinney

"""Mech integration tests: simple ones (including virtualbox smoke)"""
import re
import subprocess
import platform

import pytest


@pytest.mark.int
def test_int_smoke_virtualbox(helpers):
    """Smoke test most options using virtualbox."""

    test_dir = "tests/int/simple_virtualbox"
    helpers.cleanup_dir_and_vms_from_dir(test_dir, names=['first'])

    # should init
    command = "mech init --provider virtualbox bento/ubuntu-18.04"
    expected_lines = ["Initializing", "Loading metadata", "has been initialized", "mech up"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # should start
    command = "mech up"
    expected_lines = ["virtualbox", "Extracting", "Getting IP", "started",
                      "Not yet implemented"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # should be able to re-up, verify 'start' alias works, too
    commands = ["mech up", "mech start"]
    expected_lines = ["Getting IP", "started"]
    for command in commands:
        results = subprocess.run(commands, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stderr == ''
        assert results.returncode == 0
        for line in expected_lines:
            print(line)
            assert re.search(line, stdout, re.MULTILINE)

    # test 'mech ps'
    command = "mech ps first"
    expected_lines = ["Not yet implemented"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech global-status'
    command = "mech global-status"
    expected_lines = ['first']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech list'
    commands = ["mech ls", "mech list"]
    expected_lines = ['first', 'ubuntu', 'virtualbox']
    for command in commands:
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stderr == ''
        assert results.returncode == 0
        for line in expected_lines:
            print(line)
            assert re.search(line, stdout, re.MULTILINE)

    # test 'mech stop'
    command = "mech stop"
    expected_lines = ['Stopped']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech stop' again
    command = "mech stop"
    expected_lines = ['Not stopped']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech start'
    command = "mech start"
    expected_lines = ['started']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech pause'
    command = "mech pause"
    expected_lines = ['Not yet implemented']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech resume'
    command = "mech resume"
    expected_lines = ['Not yet implemented']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech suspend'
    command = "mech suspend"
    expected_lines = ['Not yet implemented']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech resume' after suspend
    command = "mech resume"
    expected_lines = ['Not yet implemented']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech ssh' (different forms)
    commands = ["mech ssh -c 'uptime' first", "mech ssh --command 'uptime' first"]
    expected_lines = ['load average']
    for command in commands:
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stderr == ''
        assert results.returncode == 0
        for line in expected_lines:
            print(line)
            assert re.search(line, stdout, re.MULTILINE)

    # test 'mech scp' to guest
    command = "date > now; mech scp now first:/tmp"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stdout == ''
    assert stderr == ''
    assert results.returncode == 0

    # test 'mech scp' from guest
    command = "mech scp first:/tmp/now ."
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stdout == ''
    assert stderr == ''
    assert results.returncode == 0

    # test 'mech ip first'
    command = "mech ip first"
    expected = r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout)

    if platform.system() == "Linux":
        # test "mech port"
        command = "mech port"
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stdout == ''
        assert stderr.strip() == 'This command is not supported on this OS.'
        assert results.returncode == 1
    else:
        # test "mech port"
        command = "mech port"
        expected = "Not yet implemented"
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stderr == ''
        assert results.returncode == 0
        assert re.search(expected, stdout, re.MULTILINE)

    # test "mech box list" (and alias)
    commands = ["mech box list", "mech box ls"]
    expected = r"ubuntu"
    for command in commands:
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stderr == ''
        assert results.returncode == 0
        assert re.search(expected, stdout, re.MULTILINE)

    # test "mech snapshot list" (and alias)
    commands = ["mech snapshot list", "mech snapshot ls"]
    expected = "Not yet implemented"
    for command in commands:
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stderr == ''
        assert results.returncode == 0
        assert re.search(expected, stdout, re.MULTILINE)

    # test "mech snapshot save"
    command = "mech snapshot save snap1 first"
    expected = "Not yet implemented"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout)

    # test "mech snapshot save" with same args again
    # command = "mech snapshot save snap1 first"
    # results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    # stdout = results.stdout.decode('utf-8')
    # stderr = results.stderr.decode('utf-8')
    # assert stdout == ''
    # assert re.search('A snapshot with the name already exists', stderr)
    # assert results.returncode == 1

    # test "mech snapshot list" (and alias) again (now that we have one)
    # commands = ["mech snapshot list", "mech snapshot ls"]
    # expected = "Total snapshots: 1"
    # for command in commands:
    #     results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    #     stdout = results.stdout.decode('utf-8')
    #     stderr = results.stderr.decode('utf-8')
    #     assert stderr == ''
    #     assert results.returncode == 0
    #     assert re.search(expected, stdout, re.MULTILINE)

    # test "mech snapshot delete"
    command = "mech snapshot delete snap1 first"
    expected = "Not yet implemented"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout)

    # should be able to destroy
    command = "mech destroy -f"
    expected = "Deleting"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout)

    # clean up at the end
    helpers.cleanup_dir_and_vms_from_dir(test_dir)
