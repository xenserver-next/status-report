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
  Using `pre-commit` to run the test and static analysis checks locally
- [doc/coverage.md](doc/coverage.md): Introduction on **coverage** from `pytest`

Documentation on pytest and its fixtures:
- [README-pytest.md](README-pytest.md): Introduction on the recommended pytest suite for unit tests
- [README-pytest-chroot.md](README-pytest-chroot.md):
  Introduction on the `pytest`-based integration test suite using namespaces
- [tests/unit/conftest-README.md](tests/unit/conftest-README.md):
  Introduction on the `pytest` fixtures defined in `tests/unit/conftest.py`

## Frequently asked Questions

### Is the master branch ready for Python3?

Yes, it is ready for testing with Python in XS9 using Python3.11 to be precise.

But, there are still 7 open subtasks below CP-48020 (remaining Py2->Py3 work)
that are not yet done.

See the related question on whether we should remove support for Python2.

### Should we remove Python2 compatibility to make the code simple?

There are three misconceptions in this question:

#### Python2 is not ready to be removed.
There are still 7 open tasks below CP-48020 (remaining Python2 to Python3 work)
that are not yet done.
- `xenserver-status-report` needs to be validated on Python3 in order to use it
  for production use on Python3, and the open tasks are an indication that there
  are a few cases that need testing.

#### We need the current code to be Python2-compatible for backports or Hotfixes for the Yangtze release.

Example:
UPD-990 for the Yangtze release contains CP-41238 ([XSI-1344] Bugtool should
contain up-to-date RRDs):
- The fix for CP-41238/XSI-1344 depends on other commits on master.
- Instead of backporting these large changes (potentially introducing errors)
  and having to maintain that older branch for the Yangtze release, it will be
  less work to use master for UPD-990 for fixing XSI-1344.
  - Because we use master for XS8 as well, master is in constant production use
    with Python2 in:
    - XenRT
    - Internal diagnostics
    - Customer support.
  - Therefore, we know that master is already in production use since quite some
    time with Python2, and we can safely use master for the Yangtze hotfix UPD-990 too.
  - This means, due to the constant testing in XenRT and Customer support, we
    know that we can safely deploy master for Yangtze hotfixes like UPD-990.

This benefit alone is quite big.

#### The Python2 conditions are trivial, and the complexity is elsewhere.

There are only 5 (yes, just five) conditions in the status-report code where
there is a tiny special case for Python2/Python3. Compared to the total size
of over 2390 lines of the program, this is totally negligible.

That means it does not increase or decrease the complexity by any perceivable
amount:
- Five simple if conditions that have no real code below them have very low
  complexity by any measure.

See the next question for the concrete data that fosters this point.

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
of code in your function. If you have 100 consecutive statements with no branches (conditions, loops, etc.), you'll get a value of 1 for both of them.

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

##### Output:

| Filename | Name | Type | Start:End Line | Complexity | Classification |
| -------- | ---- | ---- | -------------- | ---------- | -------------- |
| xen-bugtool | main | F | 777:1359 | 84 | F |
| xen-bugtool | load_plugins | F | 1761:1827 | 27 | D |
| xen-bugtool | collect_data | F | 701:758 | 21 | D |
| host-installer/install.py | go | F | 89:325 | 60 | F |
| host-installer/backend.py | performInstallation | F | 293:446 | 31 | E |
| host-installer/backend.py | partitionTargetDisk | F | 525:587 | 21 | D |
| host-installer/disktools.py | DOSPartitionTool.writeThisPartitionTable | M | 839:912 | 23 | D |
| host-installer/restore.py | restoreFromBackup | F | 17:177 | 33 | E |
| host-installer/product.py | ExistingInstallation._readSettings | M | 101:412 | 75 | F |
| host-installer/diskutil.py | probeDisk | F | 467:530 | 21 | D |
| host-installer/init | main | F | 92:247 | 35 | E |
| host-installer/init | configureNetworking | F | 28:85 | 24 | D |
| host-installer/tui/repo.py | confirm_load_repo | F | 207:283 | 21 | D |
| host-installer/tui/network.py | get_iface_configuration | F | 15:134 | 29 | D |
| host-installer/tui/installer/screens.py | get_name_service_configuration | F | 795:962 | 28 | D |
| perfmon | main | F | 1307:1522 | 38 | E |
| perfmon | VMMonitor.get_default_variable_config | M | 858:917 | 23 | D |
| xcp/cpiofile.py | CpioFile.open | M | 1003:1083 | 22 | D |
| xcp/bootloader.py | Bootloader.readExtLinux | M | 110:194 | 32 | E |
| xcp/bootloader.py | Bootloader.readGrub | M | 197:301 | 28 | D |
| xcp/bootloader.py | Bootloader.readGrub2 | M | 304:463 | 26 | D |
| xcp/bootloader.py | Bootloader.writeGrub2 | M | 557:619 | 23 | D |
| xcp/net/ifrename/dynamic.py | DynamicRules.generate | M | 147:227 | 23 | D |
| xcp/net/ifrename/logic.py | rename_logic | F | 125:366 | 41 | F |
| xcp/net/ifrename/logic.py | rename | F | 368:498 | 35 | E |
| xcp/net/ifrename/static.py | StaticRules.load_and_parse | M | 103:210 | 25 | D |
| xcp/net/ifrename/static.py | StaticRules.generate | M | 212:292 | 23 | D |

#### Verdict

As the five 5 conditions do not change the functionality of the main code paths,
Python2 compatibility code does not change these complexity numbers.

#### Summary on CC (Cyclomatic Complexity) results
Only `host-installer/install.py/go()` (CC=60) comes close `bugtool/main()` (CC=84).

The other projects are larger, when summarizing their CC into one number, this
indicates that other projects need more tests.

#### Conclusion

Due to the high CC, the testability is the lowest of all code checked so far.

Finally, testability for xen-bugtool is complicated even more by the fact that
some conditions like the checks that omit data from collection to do reaching
maximum size limits are quirky and have led in the past to unexpectedly omitting
potentially important files just because a change caused a different ordering for
the collection of files.

This was triggered for example, by the change to collect up-to-date RRDs that
we'll need to provide as an HotFix for the Yangtze release. This was discovered
only much later during manual use while working on completely unrelated issues.

Because of this Testability is a problem, it is risky to make such changes.

When the testability is a challenge, there is one other concept that can be applied,
which is the concept of “proven in use”, where you have confidence by it being
proven in use.

This result is a testament that keeping Python2 compatibility is necessary.
We need it to have a good “proven in use” statement for confidence in backporting
complex changes like collection of up-to-date RRDs (see above) to the Yangtze release
for Hotfixes.

### References
- https://pypi.org/project/radon/
- https://radon.readthedocs.io/en/latest/
- https://medium.com/@commbigo/python-code-complexity-metrics-e6c87646c1c2
