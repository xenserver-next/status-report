# Documentation of `tests/unit/conftest.py`

## Overview

`conftest.py` is a special file used by the `pytest` framework.
It is a local plugin for your tests, where you can define fixtures, hooks,
and other configuration for your tests.

`pytest` automatically discovers `conftest.py`, and makes
the fixtures in it available to all tests in its directory.

This is described in the `pytest` documentation:
<https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files>

The tests in [`tests/unit/`](.) use it for three classes of tests:

- [Unit-testing](https://en.wikipedia.org/wiki/Unit_testing) of single functions
- [Functional testing](https://en.wikipedia.org/wiki/Functional_testing)
  of a chain of functions, testing their in- and output
- [Integration testing](https://en.wikipedia.org/wiki/Integration_testing)
  of `xen-bugtool` the main code of [`xen-bugtool`](../../xen-bugtool)
  - by calling its function `main()` in [`tests/unit/test_main.py`](test_main.py)

## Fixtures provided by `tests/unit/conftest.py`

Fixtures are functions that set up and tear down test environments.
They are decorated with `@pytest.fixture`.
Fixtures defined in `conftest.py` are available to all test files
in the same directory and subdirectories.

Links to the [`pytest`](https://docs.pytest.org/en/8.0.x/how-to/index.html#how-to)
documentation pages about fixtures:

- [An introduction to fixtures](https://docs.pytest.org/en/8.0.x/fixture.html):
  Quick intro into the topic of fixtures
- [How to use fixtures](https://docs.pytest.org/en/8.0.x/how-to/fixtures.html):
  A How-To that demonstrates fixtures using examples
- [The reference on fixtures](https://docs.pytest.org/en/8.0.x/reference/fixtures.html):
  The reference documentation on pytest fixtures

These are the fixtures defined in [`tests/unit/conftest.py`](conftest.py),
their name and purpose is:

- `builtins`: Provide the name of the built-in module for Python 2.x and Python 3.x
- `testdir`: Provide the directory of the unit test for locating files relative to it.
- `dom0_template`: Provide the directory of the dom0 template.
- `imported_bugtool`: Import
      [`xen-bugtool`](../../xen-bugtool) as a module for executing tests with coverage.
- `bugtool`: Provide the [`xen-bugtool`](../../xen-bugtool)
      module for tests, initialized for running tests.
- `in_tmpdir`: Provide each test a
   [`tmpdir`](https://docs.pytest.org/en/4.6.x/tmpdir.html#the-tmpdir-fixture)
   as its current working directory.
- `bugtool_log`: Like `in_tmpdir`, and check if `bugtool.XEN_BUGTOOL_LOG` received logs
- `isolated_bugtool`: Like `bugtool_log`, and make
   [`tmpdir`](https://docs.pytest.org/en/4.6.x/tmpdir.html#the-tmpdir-fixture)
   read-only.

## Fixtures

### `builtins`

- **Purpose**: Provide the `builtins` module for *Python 2.x* and
  *Python 3.x*

- **Example**:

    ```python
    def test_example(builtins, mocker):
        # `builtins` provides the builtins module for Python 2 and Python 3:
        mocker.patch(builtins + ".open", mocker.mock_open(read_data="data"))
    ```

### `testdir`

- **Purpose**: Provide the directory of the main [tests/](..) directory
- **Example**:

    ```python
    @pytest.fixture
    def dom0_template(testdir):
        # relative to testdir, provide the dom0-template directory
        return testdir + "/../integration/dom0-template"
    ```

### `dom0_template`

- **Purpose**: Provide the directory of the dom0 template directory
- **Example**:

    ```python
    def test_example(bugtool, dom0_template):
        # Provide fixtures and test cases with access to example files.
        # Their location is `tests/integration/dom0_template/[etc/..]`:
        with open(dom0_template + "/etc/xensource/inventory.xml") as f:
            bugtool.parse_inventory_data(f.read())
    ```

### `imported_bugtool`

- **Purpose**: Import the `xen-bugtool` script as a module for
               executing unit tests on functions.
- **Scope**: The entire `pytest` session, it only runs once.
- **Use case**: Only for other fixtures that prepare it for tests.
- **Example use**:

    ```python
    @pytest.fixture(scope="function")
    def bugtool(imported_bugtool):
        """Initializes the bugtool data dict for each test"""
        # Init import_bugtool.data, so each unit test function gets is pristine:
        imported_bugtool.data = {}
        sys.argv = ["xen-bugtool", "--unlimited"]
        yield imported_bugtool  # After test case exit, control comes back.
        # Cleanup the bugtool data dict after each test, tests may modify it:
        imported_bugtool.data = {}
        sys.argv = ["xen-bugtool", "--unlimited"]
    ```

### `bugtool`

- **Purpose**: Initialize the data dictionary for each test.
- **Example**:

    ```python
    def test_example(bugtool):
        # Test specific functionalities of the bugtool using initialized data
        assert bugtool.data == {}
    ```

### `in_tmpdir`

- **Purposes**:

  - Provide the [`tmpdir`](https://docs.pytest.org/en/6.2.x/tmpdir.html#the-tmpdir-fixture)
    fixture.
    - `cd` into it before yielding control switch back afterwards.
    - Offer the [`py.path.local`](https://py.readthedocs.io/en/latest/path.htm)
      object which provides
      [`os.path`](https://docs.python.org/3/library/os.path.html).
      - See the **Example 2** below on how to use it.

- **Examples**:

    ```python
    # Example 1: Test requests the fixture using a decorator:
    @pytest.usefixtures("in_tmpdir")
    def test_runs_in_tmpdir(bugtool):
        assert bugtool.function_creating_files_in_the_cwd()
        # restore & cleanup is taken care of by the fixtures.
    ```

    ```python
    # Example 2: Get fixture as argument of type py.path.local:
    def test_prepares_tmpdir_for_testing(in_tmpdir, bugtool):
        # Use tmpdir's py.path.local to create a file with data:
        in_tmpdir.mkdir("tmp").join("db.json").write(json_data)
        # Call a helper ensuring the code behaves as expected:
        assert_expected_data(bugtool, global_expected_data)
    ```

### `bugtool_log`

- **Purpose**: Like `in_tmpdir` and provide the bugtool fixture.

  It adds checking the file located at `bugtool.XEN_BUGTOOL_LOG` for output.
- **Example**:

    ```python
    def test_not_generating_unexpected_logs(bugtool_log):
        # This fixture fails this test and shows "message"
        with open(bugtool_log.XEN_BUGTOOL_LOG, "a") as f:
            f.write("message")
    ```

### `isolated_bugtool`

- **Purpose**: Like `bugtool_log` and make the working directory read-only.
- **Example**:

    ```python
    def test_cannot_write_to_its_current_directory(isolated_bugtool):
        # The code under test can't write its working directory:
        open("file", "w")  # will raise an Exception
    ```

## Further Reading

Links to the [documentation](https://docs.pytest.org/en/8.0.x/how-to/index.html#how-to)
pages about fixtures:

- [An introduction to fixtures](https://docs.pytest.org/en/8.0.x/fixture.html):
  Quick intro into the topic of fixtures
- [How to use fixtures](https://docs.pytest.org/en/8.0.x/how-to/fixtures.html):
  A How-To that demonstrates fixtures using examples
- [The full documentation on fixtures](https://docs.pytest.org/en/8.0.x/reference/fixtures.html):
  The reference documentation on pytest fixtures
