"""tests/unit/conftest.py: pytest fixtures for unit-testing xen-bugtool

Introduction to fixtures:
https://docs.pytest.org/en/8.0.x/fixture.html

How to use fixtures:
https://docs.pytest.org/en/8.0.x/how-to/fixtures.html

The full documentation on fixtures:
https://docs.pytest.org/en/8.0.x/reference/fixtures.html
"""

from __future__ import print_function

import os
import shutil
import sys

import pytest


@pytest.fixture(scope="function")
def builtins():
    """Provide the builtins module name for Python 2.x and Python 3.x"""
    return "__builtin__" if sys.version_info < (3,) else "builtins"


@pytest.fixture(scope="session")
def testdir():
    """Test fixture to provide the directory of the dom0 template directory"""
    return os.path.dirname(__file__)


@pytest.fixture(scope="session")
def dom0_template(testdir):
    """Test fixture to get the directory of the dom0 template"""
    return testdir + "/../integration/dom0-template"


@pytest.fixture(scope="session")
def imported_bugtool(testdir, dom0_template):
    """Fixture to provide the xen-bugtool script as a module for unit tests"""

    def import_from_file(module_name, file_path):
        if sys.version_info.major == 2:  # pragma: no cover
            # Python 2.7, use the deprecated imp module (no alternative)
            # pylint: disable-next=deprecated-module
            import imp  # pyright: ignore[reportMissingImports]

            module = imp.load_source(module_name, file_path)

            # Prevent other code from importing the same module again:
            sys.modules[module_name] = module
            return module
        else:
            from importlib import machinery, util

            loader = machinery.SourceFileLoader(module_name, file_path)
            spec = util.spec_from_loader(module_name, loader)
            assert spec
            assert spec.loader
            module = util.module_from_spec(spec)

            # Prevent other code from importing the same module again:
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

    yield imported_bugtool  # provide the bugtool to the test function

    # Cleanup the bugtool data dict after each test as tests may modify it:
    imported_bugtool.data = {}
    sys.argv = ["xen-bugtool", "--unlimited"]
