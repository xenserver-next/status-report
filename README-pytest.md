# The pytest-based Xen-Bugtool Test Environment

See [doc/testing.md](doc/testing.md) for general introduction to testing
`xenserver-status-report`.

The test environment contains two classes of test frameworks:

- [tests/unit](tests/unit): Classic unit test framework using pytest fixtures.
  - It provides a number of pytest fixtures for testing functions including
    the `main()` function of Xen-Bugtool, which allows to run any kind of test.

- [tests/integration](tests/integration) runs `xen-bugtool` in a container with
  simulated `root` capabilities, allowing any regular user to test `xen-bugtool`
  without patching it and without requiring special system configuration.

  In this framework, two kinds of tests exist:
  - Legacy shell scripts: They run in GitHub CI Containers and not locally
  - Python-based container test suite: Uses Linux namespace to enter into
    a simulated, rootless chroot container that runs locally on any modern
    Linux development VM without any setup.

  Caveats:
  Because the test start `xen-bugtool` in a container, collecting code coverage
  from them would require merging the collected code coverage from each test.
  Because this is not yet implemented, these currently do not contribute to
  the reported code coverage.

  See [README-pytest-chroot.md](README-pytest-chroot.md)
  for further introduction on the `pytest-chroot` test suite.


## Testing this project

To run the tests using, simply run `pytest`.

The pytest.ini configures `pytest` to show you logs of failed tests.

For development, do show also logs from passing tests, run `pytest -rA`

In case a test fails on an asserting, use `pytest -vv` to get the full assert.

### Introduction to `pytest`, `pytest.mark` and `pytest fixtures`:

[![Automated Testing in Python with `pytest`, `tox`, and GitHub Actions](https://img.youtube.com/vi/DhUpxWjOhME/0.jpg)](https://www.youtube.com/watch?v=DhUpxWjOhME)

Note: For simplicity, this project uses `pre-commit` instead of `tox`:
`pre-commit` is much easier to handle and pre-commit also provides
the possibility install it as a pre-commit hook:

Whenever in this Video, `tox` is mentioned, think of `pre-commit` instead!

See [README-pre-commmit.md](README-pre-commmit.md)
on using `pre-commit` to run the test and analysis suites locally.


## Running the Xen-Bugtool Test Environment

```py
# Run the Python-based container test suite
python3 -m pytest tests/integration
```

```py
# Run the Unit tests:
python3 -m pytest tests/unit
```

```py
# Run a specific Unit test module
python3 -m pytest tests/unit/test_filter_xapi_clusterd_db.py
```

### Debugging code and cases using the `logging` module

Pytest captures the `stdout` and `stderr` of the test case and the code under
test, as some test cases check the output:

- Thus, using `print()` would break these test cases.
- `pytest --capture=no` disables capturing the output of the code under test.
  But this may not work well for test cases that assert the output.

Instead, add new, dedicated logs to the test case or the code under test.

You can do this by instrumenting the code at the desired location using `logging`:

```py
import logging; logging.warning("variable=%s", variable)
```

This works because `xen-bugtool` does not use the `logging` module in the code
under test.

As a result, it is available for debugging purposes.

### Easy way to define a custom breakpoint in the code under test

Without using extra tools or IDEs, the easiest way to debug a test case is to
add a breakpoint in the code under test. To get an interactive python debugger
prompt, add the following line to the code at the desired location:

```py
import pdb; pdb.set_trace()
```

The test case will stop at this location and provide an interactive
debugging prompt to inspect variables and step through the code.

See <https://docs.pytest.org> for more documentation on `pytest`.


## Test cases for xenserver-status-report

See [doc/testing.md](doc/testing.md) for the different types of tests.

### Unit Tests in [tests/unit](tests/unit)

- [`test_filter_xapi_clusterd_db.py`](tests/unit/test_filter_xapi_clusterd_db.py):

  Tests a function in multiple ways to assert that it works with different input
  data and generates expected output.

  It has good amount of inline comments and should be used as the basis for new tests.

- [`test_xapidb_filter.py`](tests/unit/test_xapidb_filter.py):
  Simple test case passing XML to a function filtering it.
- [`test_snmp.py`](tests/unit/test_snmp.py):
  Ditto, but for testing the filtering of SNMP config data
- [`test_fs_funcs.py`](tests/unit/test_fs_funcs.py):
  Examples for testing functions that need to access some files of Dom0
- [`test_dir_list.py`](tests/unit/test_dir_list.py):
  Example of testing function that writes xen-bugtool's global data

### Integration tests (also in [tests/unit](tests/unit))

- [`test_load_plugins.py`](tests/unit/test_load_plugins.py):
  Tests the ingestion of a bugtool plugin and its effect on the global state
- [`test_process_output.py`](tests/unit/test_process_output.py):
  Tests functions run external programs and collects their output.
- [`test_output.py`](tests/unit/test_output.py):

  Generate bug-reports using all output formats and verify the output
  by directly calling the functions without involving `main()`.

### End-to-End tests

- [`tests/unit/test_main.py`](tests/unit/test_main.py):

  Calls `xen-bugtool`'s `main()` to generate bug-reports using all output
  formats and verifies the output.

## Discussion on the current state of testing of `xen-bugtool`

- Unit test cover the cases where we need to supply different input data.
- Integration and E2E tests use files from
[`tests/integration/dom0-template`](tests/integration/dom0-template) directly:
  - We can start to add tests that copy these files into the virtual
    [pyfakefs](https://pytest-pyfakefs.readthedocs.io/en/v3.7.2/usage.html)
    file system to test using a virtual file system.
  - It allows to vary the input data to test different kinds of input data.
  - Six test cases of [python-libs](https://github.com/xenserver/python-libs)
    use it very successfully.

- Currently, the End-to-End and integration tests provide most code coverage,
  which we urgently needed to verify the correctness of the Python3 migrations.

- Unit tests to ensure that the individual functions handle specific correctly
  are needed still.


## Suggested `pytest` plugins for development of test cases

### pytest-pickled
When updating existing tests or developing new code with new test coverage, we might want to
ignore all other tests. This can be achieved with an exciting plugin called `pytest-picked`:
`pytest --picked` will collect all test modules that were newly created or changed but not
yet committed in a Git repository and run only them.

### pytest-sugar
`pytest-sugar` is a plugin that, once installed, automatically changes the format of the
`pytest` standard output to include a graphical %-progress bar when running the test suite.

### Installation of these pytest plugins
For nicer diffs of dictionaries, arrays, and the like,
use `pytest-clarity` or `pytest-icdiff`:

```py
pip install "pytest<7" pytest-picked pytest-sugar pytest-clarity # pytest-icdiff
```

For more information to debug `pytest` test suites see: https://stribny.name/blog/pytest/
