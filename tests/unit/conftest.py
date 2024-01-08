"""tests/unit/conftest.py: pytest fixtures for unit-testing functions in the xen-bugtool script"""
import os

import pytest


@pytest.fixture(scope="session")
def testdir():
    """Test fixture to get the directory of the unit test for finding other files relative to it"""
    return os.path.dirname(__file__)


@pytest.fixture(scope="session")
def dom0_template(testdir):
    """Test fixture to get the directory of the dom0 template and adding it's /usr/sbin to the PATH"""
    dom0_root_dir = testdir + "/../integration/dom0-template"
    os.environ["PATH"] = dom0_root_dir + "/usr/sbin"  # for modinfo, mdadm, etc
    return dom0_root_dir


@pytest.fixture(scope="session")
def imported_bugtool(testdir):
    """Test fixture to import the xen-bugtool script as a module for executing unit tests on functions"""

    # This uses the deprecated imp module because it needs also to run with Python2.7 for now:
    def import_from_file(module_name, file_path):
        import sys

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
    return bugtool


@pytest.fixture(scope="function")
def bugtool(imported_bugtool):
    """Test fixture for unit tests, initializes the bugtool data dict for each test"""
    # Init import_bugtool.data, so each unit test function gets it pristine:
    imported_bugtool.data = {}
    return imported_bugtool
