"""conftest.py: Test fixtures to test xen-bugtool using namespaces, supported on any Linux and GitHub CI"""
from __future__ import print_function

import os

import pytest

from namespace_container import activate_private_test_namespace, mount, umount
from utils import BUGTOOL_DOM0_TEMPL, BUGTOOL_OUTPUT_DIR, run


@pytest.fixture(autouse=True, scope="session")
def create_and_enter_test_environment():
    """At the start of the pytest session, activate a namespace with bindmounts for testing xen-bugtool"""
    activate_private_test_namespace(BUGTOOL_DOM0_TEMPL, ["/etc", "/opt", "/usr/sbin", "/usr/lib/systemd"])
    os.environ["PYTHONPATH"] = "tests/mocks"


# zip, tar, tar.bz2 are the three output formats suppored by xen_bugtool:
@pytest.fixture(scope="function", params=("zip", "tar", "tar.bz2"))
def output_archive_type(request):
    """Parameterized fixture which causes the tests to run for each of the three output_archive_types"""
    return request.param


@pytest.fixture(autouse=True, scope="function")
def run_test_functions_with_private_tmpfs_output_directory():
    """Generator fixture to run each test function with a private bugtool output directory using tmpfs"""
    # Works in conjunction of having entered a private test namespace for the entire pytest session before:
    mount(target="/var", fs="tmpfs", options="size=128M")
    # To provide test files below /var, subdirectores can be bind-mounted/created here
    # (or the tmpfs mount above could be done on BUGTOOL_OUTPUT_DIR)
    # run_bugtool_entry() will chdir to the output directory, so change back afterwards:
    srcdir = os.getcwd()
    yield
    os.chdir(BUGTOOL_OUTPUT_DIR)
    # Assert that the test case did not leave any unchecked output fileas in the output directory:
    remaining_files = []
    for currentpath, _, files in os.walk("."):
        for file in files:
            remaining_files.append(os.path.join(currentpath, file))
    if remaining_files:
        print("Remaining (possibly unchecked) files found:")
        print(remaining_files)
        os.chdir(BUGTOOL_OUTPUT_DIR)
        run(["find", "-type", "f"])
        os.chdir(srcdir)
        print("Ensure that these files are checked, remove them when checked.")
        umount("/var")
        raise RuntimeError("Remaining (possibly unchecked) files found. Run 'pytest -rF' for logs")
    os.chdir(srcdir)
    umount("/var")
