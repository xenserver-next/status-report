"""tests/unit/conftest.py: pytest fixtures for unit-testing functions in the xen-bugtool script"""
import os
import sys

import pytest


@pytest.fixture(scope="function")
def builtins():
    """
    Pytest fixture to return the name of the built-in module.
    The built-in module provides the built-in functions, exceptions, etc.
    It is needed to replace built-in functions like open() with a new mock.

    :returns (str): The name of the built-in module.
    """
    if sys.version_info < (3,):
        return "__builtin__"  # pragma: no cover
    return "builtins"


@pytest.fixture(scope="session")
def testdir():
    """Test fixture to get the directory of the unit test for finding other files relative to it"""
    return os.path.dirname(__file__)


@pytest.fixture(scope="session")
def dom0_template(testdir):
    """Test fixture to get the directory of the dom0 template and adding it's /usr/sbin to the PATH"""
    dom0_root_dir = testdir + "/../integration/dom0-template"
    return dom0_root_dir


@pytest.fixture(scope="session")
def imported_bugtool(testdir, dom0_template):
    """Test fixture to import the xen-bugtool script as a module for executing unit tests on functions"""

    # This uses the deprecated imp module because it needs also to run with Python2.7 for now:
    def import_from_file(module_name, file_path):
        if sys.version_info.major == 2:  # pragma: no cover
            import imp  # pylint: disable=deprecated-module  # pyright: ignore[reportMissingImports]

            return imp.load_source(module_name, file_path)
        else:
            # Py3.11+: Importing Python source code from a script without the .py extension:
            # https://gist.github.com/bernhardkaindl/1aaa04ea925fdc36c40d031491957fd3:
            from importlib import machinery, util

            loader = machinery.SourceFileLoader(module_name, file_path)
            spec = util.spec_from_loader(module_name, loader)
            assert spec
            assert spec.loader
            module = util.module_from_spec(spec)
            # Probably a good idea to add manually imported module stored in sys.modules
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module

    bugtool = import_from_file("xen-bugtool", testdir + "/../../xen-bugtool")
    bugtool.ProcOutput.debug = True
    # Prepend tests/mocks to force the use of our mock xen.lowlevel.xc module:
    sys.path.insert(0, testdir + "/../mocks")
    os.environ["PATH"] = dom0_template + "/usr/sbin"  # for modinfo, mdadm, etc
    return bugtool


@pytest.fixture(scope="function")
def bugtool(imported_bugtool):
    """Test fixture for unit tests, initializes the bugtool data dict for each test"""
    # Init import_bugtool.data, so each unit test function gets it pristine:
    imported_bugtool.data = {}
    sys.argv = ["xen-bugtool", "--unlimited"]
    return imported_bugtool


@pytest.fixture(scope="function")
def tmpdir(tmp_path):
    """Run test in a temporary directory and check leftovers after the test."""
    temp_dir = tmp_path.as_posix()

    curdir = os.getcwd()
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(curdir)

    entries = os.listdir(temp_dir)
    if entries:  # pragma: no cover
        pytest.fail("Test left files in tmpdir: " + ", ".join(entries))
