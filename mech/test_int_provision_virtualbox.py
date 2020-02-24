# Copyright (c) 2020 Mike Kinney

"""Mech integration tests: provisioning tests using virtualbox provider
   Note: 'no-nat' (bridged) networking must be used for the test that
   provisions using pyinfra because the ubuntu server needs to install
   using apt. (over the internet)
"""
import re
import subprocess

import pytest


@pytest.mark.int
def test_int_provision(helpers):
    """Provision testing."""

    test_dir = "tests/int/provision_virtualbox/tmp"
    helpers.cleanup_dir_and_vms_from_dir(test_dir, names=['first', 'second',
                                                          'third', 'fourth'])

    # copy files from parent dir
    command = "cp ../file* .; cp ../Mechfile ."
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stdout == ''
    assert stderr == ''
    assert results.returncode == 0

    # up without provisioning and with no-nat
    command = "mech up --no-nat --disable-provisioning"
    expected_lines = [r".first.*started",
                      r".second.*started",
                      r".third.*started",
                      r".fourth.*started"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # show provisioning
    command = "mech provision -s"
    expected_lines = [r"first.*Provision 2 entries",
                      r"second.*Provision 3 entries",
                      r"fourth.*Provision 1 entries",
                      r"Nothing"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # ensure there is no file on first
    command = 'mech ssh -c "ls -al /tmp/file1.txt" first'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("No such file or directory", stdout)
    assert results.returncode != 0

    # ensure there is no file on second (testing shell non-inline shell provisioning)
    command = 'mech ssh -c "ls -al /tmp/file1.sh.out" second'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("No such file or directory", stdout)
    assert results.returncode != 0

    # ensure there is no file on second (testing shell inline shell provisioning)
    command = 'mech ssh -c "ls -al /tmp/inline_test.out" second'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("No such file or directory", stdout)
    assert results.returncode != 0

    # ensure the package 'npm' is not installed on fourth
    command = 'mech ssh -c "dpkg -l npm" fourth'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert re.search("no packages found matching npm", stdout)
    assert stderr == ''
    assert results.returncode != 0

    # provision
    command = "mech provision"
    expected_lines = [r"first.*Provision 2 entries",
                      r"second.*Provision 3 entries",
                      r"fourth.*Provision 1 entries",
                      r"Nothing"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # ensure file exists now on first
    command = 'mech ssh -c "ls -al /tmp/file1.txt" first'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("/tmp/file1.txt", stdout)
    assert results.returncode == 0

    # ensure file exists now on second from non-inline shell provisioning
    command = 'mech ssh -c "ls -al /tmp/file1.sh.out" second'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("/tmp/file1.sh.out", stdout)
    assert results.returncode == 0

    # ensure file1.sh.out has the args
    command = """mech ssh -c "grep 'a=1 b=true' /tmp/file1.sh.out" second"""
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("a=1 b=true", stdout)
    assert results.returncode == 0

    # ensure file exists now on second from inline shell provisioning
    command = 'mech ssh -c "ls -al /tmp/inline_test.out" second'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("/tmp/inline_test.out", stdout)
    assert results.returncode == 0

    # ensure package 'npm' *is* installed on fourth (should have been installed
    # as part of the pyinfra provisioning)
    command = 'mech ssh -c "dpkg -l npm" fourth'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("npm", stdout)
    assert results.returncode == 0

    # ensure provisioning runs during "up"
    command = "mech up"
    expected_lines = [r"first.*Provision 2 entries",
                      r"second.*Provision 3 entries",
                      r"fourth.*Provision 1 entries",
                      r"Nothing"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # destroy
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
