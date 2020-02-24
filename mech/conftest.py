# Copyright (c) 2020 Mike Kinney

"""Common pytest code."""
import json
import os
import pytest
import subprocess


from shutil import rmtree


@pytest.fixture
def mechfile_one_entry():
    """Return one mechfile entry."""
    return {
        'first': {
            'name': 'first',
            'box': 'bento/ubuntu-18.04',
            'box_version': '201912.04.0'
        }
    }


@pytest.fixture
def mechfile_one_entry_without_box_version():
    """Return one mechfile entry."""
    return {
        'first': {
            'name': 'first',
            'box': 'bento/ubuntu-18.04'
        }
    }


@pytest.fixture
def mechfile_one_entry_with_file():
    """Return one mechfile entry."""
    return {
        'name': 'first',
        'box': 'bento/ubuntu-18.04',
        'box_version': '201912.04.0',
        'file': '/tmp/somefile.box'
    }


@pytest.fixture
def mechfile_one_entry_with_auth():
    """Return one mechfile entry with auth."""
    return {
        'first': {
            'name': 'first',
            'box': 'bento/ubuntu-18.04',
            'box_version': '201912.04.0',
            'auth': {
                'username': 'bob',
                'pub_key': 'some_pub_key_data'
            }
        }
    }


@pytest.fixture
def mechfile_one_entry_with_auth_and_mech_use():
    """Return one mechfile entry with auth that has mech_use."""
    return {
        'first': {
            'name': 'first',
            'box': 'bento/ubuntu-18.04',
            'box_version': '201912.04.0',
            'auth': {
                'username': 'bob',
                'mech_use': 'true',
                'pub_key': 'some_pub_key_data'
            }
        }
    }


@pytest.fixture
def mechfile_two_entries():
    """Return two mechfile entries."""
    return {
        'first': {
            'name': 'first',
            'box': 'bento/ubuntu-18.04',
            'box_version': '201912.04.0',
            'shared_folders': [
                {
                    "host_path": ".",
                    "share_name": "mech"
                }
            ],
            'url':
            'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/'
            'versions/201912.04.0/providers/vmware_desktop.box'
        },
        'second': {
            'name': 'second',
            'box': 'bento/ubuntu-18.04',
            'box_version': '201912.04.0',
            'url':
            'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/'
            'versions/201912.04.0/providers/vmware_desktop.box'
        }
    }


CATALOG = """{
    "description": "foo",
    "short_description": "foo",
    "name": "bento/ubuntu-18.04",
    "versions": [
        {
            "version": "aaa",
            "status": "active",
            "description_html": "foo",
            "description_markdown": "foo",
            "providers": [
                {
                    "name": "vmware_desktop",
                    "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/aaa/providers/vmware_desktop.box",
                    "checksum": null,
                    "checksum_type": null
                }
            ]
        }
    ]
}"""
@pytest.fixture
def catalog():
    """Return a catalog."""
    return CATALOG


@pytest.fixture
def shell_provision_config():
    return [
        {
            "type": "shell",
            "path": "file1.sh",
            "args": [
                "a=1",
                "b=true",
            ],
        },
        {
            "type": "shell",
            "inline": "echo hello from inline"
        },
        {
            "type": "shell",
            "inline": "echo hello2 from inline",
            "args": []
        }
    ]


@pytest.fixture
def pyinfra_provision_config():
    return [
        {
            "type": "pyinfra",
            "path": "file1.py",
            "args": [
                "sudo=True",
                "b=1",
            ],
        },
        {
            "type": "pyinfra",
            "path": "file2.py",
        }
    ]


@pytest.fixture
def pyinfra_provision_http_config():
    return [
        {
            "type": "pyinfra",
            "path": "https://github.com/Fizzadar/pyinfra/blob/"
            "master/examples/docker_ce.py",
            "args": [
                "sudo=True"
            ],
        }
    ]


@pytest.fixture
def catalog_as_json():
    """Return a catalog as json."""
    return json.loads(CATALOG)


@pytest.fixture
def mech_add_arguments():
    """Return the default 'mech add' arguments."""
    return {
        '--force': False,
        '--box-version': None,
        '--name': None,
        '--box': None,
        '--add-me': None,
        '--use-me': None,
        '--provider': None,
        '<location>': None,
    }


@pytest.fixture
def mech_box_arguments():
    """Return the default 'mech box' arguments."""
    return {
        '--force': False,
        '--box-version': None,
        '<provider>': None,
        '<location>': None,
    }


@pytest.fixture
def mech_init_arguments():
    """Return the default 'mech init' arguments."""
    return {
        '--force': False,
        '--box-version': None,
        '--name': None,
        '--box': None,
        '--add-me': None,
        '--use-me': None,
        '--provider': None,
        '<location>': None,
    }


class Helpers:
    @staticmethod
    def get_mock_data_written(a_mock):
        """Helper function to get the data written to a mocked file."""
        written = ''
        for call in a_mock.mock_calls:
            tmp = '{}'.format(call)
            if tmp.startswith('call().write('):
                line = tmp.replace("call().write('", '')
                line = line.replace("')", '')
                line = line.replace("\\n", '\n')
                written += line
        return written

    @staticmethod
    def kill_pids(pids):
        """Kill all pids."""
        for pid in pids:
            results = subprocess.run(args='kill {}'.format(pid), shell=True, capture_output=True)
            if results.returncode != 0:
                print("Could not kill pid:{}".format(pid))

    @staticmethod
    def find_pids(search_string):
        """Return all pids that that match the search_string."""
        # print('search_string:{}'.format(search_string))
        pids = []
        results = subprocess.run(args="ps -ef | grep '{}' | grep -v grep"
                                 .format(search_string), shell=True, capture_output=True)
        # print('results:{}'.format(results))
        if results.returncode == 0:
            # we found a proc
            stdout = results.stdout.decode('utf-8')
            for line in stdout.split('\n'):
                data = line.split()
                if len(data) > 2:
                    # add pid to the collection
                    pids.append(data[1])
        # print('pids:{}'.format(pids))
        return pids

    @staticmethod
    def cleanup_dir_and_vms_from_dir(a_dir, names=['first']):
        """Kill processes and remove directory and re-create the directory.
           For VMware VMs, look for the .vmx part_of_dir matches the full path.
           For virtualbox look 'VBoxHeadless --comment <name of the instance>'
           Note: Unfortunately, the name is global, so you can only have one
           'first' isntance. Make instance name unique for int tests that use
           virtualbox.
       """
        # remove from virtualbox
        for name in names:
            results = subprocess.run(args="VBoxManage unregistervm {}".format(name),
                                     shell=True, capture_output=True)
            # print('results:{}'.format(results))
        # kill vmware processes
        Helpers.kill_pids(Helpers.find_pids('vmware-vmx.*' + a_dir + '/.mech/'))
        # kill virtualbox processes (if any)
        for name in names:
            Helpers.kill_pids(Helpers.find_pids('VBoxHeadless --comment {} '.format(name)))
        # clean up the vm files
        rmtree(a_dir, ignore_errors=True)
        # remove any "dead" instances in virtualbox
        results = subprocess.run(args="VBoxManage list vms", shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        vms = stdout.split('\n')
        # print('vms:{}'.format(vms))
        for line in vms:
            # print('line:{}'.format(line))
            parts = line.split(' ')
            if len(parts) > 1 and parts[0] == '"<inaccessible>"':
                results = subprocess.run(args="VBoxManage unregistervm {}".format(parts[1]),
                                         shell=True, capture_output=True)
                # print('results:{}'.format(results))
        # print('results:{}'.format(results))
        # re-create the directory to start afresh
        os.mkdir(a_dir)


@pytest.fixture
def helpers():
    """Helper functions for testing."""
    return Helpers
