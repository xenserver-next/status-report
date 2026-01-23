# Developer Documentation for Xen-Bugtool

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=xenserver-next_status-report&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=xenserver-next_status-report)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=xenserver-next_status-report&metric=bugs)](https://sonarcloud.io/summary/new_code?id=xenserver-next_status-report)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=xenserver-next_status-report&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=xenserver-next_status-report)

This developer documentation provides detailed information about
the development environment for `xen-bugtool`,
a tool designed to assist with debugging XenServer issues.

For more information, see these README files:

Development practices and guidelines:
- [doc/development.md](doc/development.md): Development guidelines and best practices
- [doc/release.md](doc/release.md): Instructions for creating a new release

Setting up the development environment:
- [README-python-install.md](README-python-install.md) - Preparing your
  Development VM for running the test suite
- [README-Windows-WSL2.md](README-Windows-WSL2.md) - Windows and WSL2 setup tips

Automated tests:
- [doc/testing.md](doc/testing.md): Overview of the different types of tests
- [doc/pre-commit.md](doc/pre-commit.md):
  Using `pre-commit` to run tests and static analysis checks locally
- [doc/coverage.md](doc/coverage.md): Introduction on **coverage** from `pytest`

Documentation on pytest and its fixtures:
- [README-pytest.md](README-pytest.md):
  Introduction on the recommended pytest suite for unit tests
- [README-pytest-chroot.md](README-pytest-chroot.md):
  Introduction on the `pytest`-based integration test suite using namespaces
- [tests/unit/conftest-README.md](tests/unit/conftest-README.md):
  Introduction on the `pytest` fixtures defined in `tests/unit/conftest.py`

## Frequently asked Questions

### Why use unit tests, isn't testing optional when we have XenRT?

- By intentional design, the failure mode of the status report tool is to catch
  all possible exceptions and silently omit the collections that failed.
- XenRT does not have tests for missing files in the status reports.
- Therefore, XenRT has effectively no efficient testing of status reports.
- Most code changes can be tested more effectively using unit tests.
- The test suite runs with very high code coverage
  and is run on every commit by GitHub Actions.
- For development, the unit tests can be run in a controlled environment
  using `pre-commit run -av`. See [doc/pre-commit.md] for details.

### How to modernize the status-report tool with Python3

- Replace `try-except-pass` or `try-finally` with `contextlib.suppress`.
- Replace `%` formatting and "str1" + "str2", etc with `f-strings`.
- Use `pathlib` instead of `os.path`.
- Type annotations can now use type aliases for better readability

### What and where is the complexity in xenserver-status-report?

First, it is good to define what is meant by complexity. There are at least two
important measures of complexity:
Cyclomatic complexity and cognitive complexity are the two common software metrics.

#### Cyclomatic complexity

Most often computed on methods or functions, it indicates the number of possible
execution paths. It was first developed by Thomas J. McCabe, Sr. in 1976.

The larger the Cyclomatic complexity, the more difficult it is test the code
(i.e., Testability). Alternatively, this measure is a hint of how many distinct
test cases you need for having tested the code.

For good introduction, please see this article:
[Cognitive Complexity Vs Cyclomatic Complexity -- An Example With C#](
  https://www.c-sharpcorner.com/blogs/cognitive-complexity-vs-cyclomatic-complexity-an-example-with-c-sharp)

#### Cognitive complexity

This metric indicates how much it's difficult for a human to understand the code
and all its possible paths. Cognitive complexity will give more weight to nested
conditions that may supposedly be harder to understand if there are complex conditions.

#### Interpreting complexity metrics

Both metrics stand as code smells in case they reach a given threshold (often 10
or 15). Beyond these values, functions tend to be difficult to test and maintain
and are thus good candidates for a redesign or refactoring.

You should keep in mind that both metrics are independent of the number of lines
of code in your function. If you have 100 consecutive statements with no branches
(conditions, loops, etc.), you'll get a value of 1 for both of them.

#### Blind spots of complexity metrics
##### Consistent and easy to read Code style and formatting rules
Complexity metrics do not consider consistent coding style and formatting rules
that can be very helpful, or if not done well, make code worse to understand and
maintain.
##### Data structures and global variables joining functions into one unit.

Interconnecting functions and methods by the use of global variables and complex
data structures can raise the actual complexity beyond what the measured metrics.

For example, `xenserver-status-report` uses a number of global data structures
that join the most complex functions `main()`, `collect_data()`, `load_plugins()`
and `run_proc_groups()` and the functions they call into one big conglomerate.
Essentially, to get a metric that reflects this, you'd have to add the complexity
metrics of those to one large number.

#### Complexity scores and risk for testability and maintainability

| Score        | Cyclomatic  | Risk Type              |
| ------------ | ----------- | ---------------------- |
|      1 to 10 | Simple      | Not much risk          |
|     11 to 20 | Complex     | Low risk               |
|     21 to 50 | Too complex | Medium risk, attention |
| More than 50 | Too complex | Can't test, high risk  |

#### Cyclomatic complexity cores for main bugtool functions vs other functions

```bash
pip install radon
# Clone python-libs, and host-installer copy perfmon from xen-api, then run:
radon cc xen-bugtool host-installer/ perfmon xcp --total-average -nd --md
```

#### Conclusion

Due to the high CC, the testability is the lowest of all code checked so far.

Finally, testability for xen-bugtool is complicated even more by the fact that
some conditions like the checks that omit data from collection to do reaching
maximum size limits are quirky and have led in the past to unexpectedly omitting
potentially important files just because a change caused a different ordering for
the collection of files.

### References
- https://pypi.org/project/radon/
- https://radon.readthedocs.io/en/latest/
- https://medium.com/@commbigo/python-code-complexity-metrics-e6c87646c1c2
