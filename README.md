# Developer Documentation for Xen-Bugtool

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=xenserver-next_status-report&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=xenserver-next_status-report)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=xenserver-next_status-report&metric=bugs)](https://sonarcloud.io/summary/new_code?id=xenserver-next_status-report)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=xenserver-next_status-report&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=xenserver-next_status-report)

This developer documentation provides detailed information about
the development environment for `xen-bugtool`,
a tool designed to assist with debugging XenServer issues.

For more information, see these README files:
- [README-python-install.md](README-python-install.md) - Preparing your
  Development VM for running the test suite
- [README-pytest.md](README-pytest.md) - Introduction on the recommended pytest suite for unit tests
- [README-pytest-chroot.md](README-pytest-chroot.md) - Introduction on the `pytest-chroot` test suite
- [README-Windows-WSL2.md](README-Windows-WSL2.md) - Windows and WSL2 setup tips
- [doc/pre-commit.md](doc/pre-commmit.md):
  Using `pre-commit` to run the test and static analysis checks locally
- [doc/coverage.md](doc/coverage.md): Introduction on **coverage** from `pytest`

## Frequently asked Questions

### How stable and well-tested is the Python3 support in `xen-bugtool`?
- It is completely stable and well-tested from usage on XS9:
  The last Python3 issue was fixed 25 March 2024, and since then,
  there have been no further Python3 issues.
- The test suite runs with very high code coverage on both Python2 and Python3
  and is run on every commit by GitHub Actions.

### Is Python2 support still needed?
No. As regular support for XenServer 8.2 has ended, and there are no plans
to backport big changes to XenServer 8.2, Python2 support is no longer needed.

### Why was Python2 support kept for so long?
In case of backporting complex changes to XenServer 8.2, actual use of Python2
mode on XenServer 8.4 provided confidence that Python2 support was still working.
But this aspect is no longer a concern.

### What are the benefits of dropping Python2 support?
- Switching `xen-bugtool` to Python3 on XenServer 8.4 too should de-risk it from
  breaking its Python2 support accidentally when making changes to `xen-bugtool`:
- As developers now use Python3, the risk of accidentally breaking Python2 support
  exists. With Python2 support dropped, this risk is gone.
- Also, more friendly Python3 features become available:

  - `contextlib` context manager `suppress` instead of try-except or try-finally.
  - `f-strings` instead of the older `%` formatting and "str1" + "str1", etc.
  - `pathlib` instead of `os.path`
  - Type annotations that can use type aliases for better readability

# How is the change to Python3-only implemented?

In this repo, the change to Python3-only is implemented in these steps:
1. Switch the shebang line to `#!/usr/bin/env python3`
2. Disable the Python2 test runs in GitHub Actions.

In the RPM spec file, the change to Python3-only is implemented by:
3. Replace the `python2` RPM dependencies with `python3` dependencies

Once this is done, python2 compatibility code can be removed.

But, there is no hurry to do this, as the Python2 compatibility code
is negligible and does not affect the main code paths.

#### Which python2 compatibility code can be removed?

There are only 5 (yes, just five) conditions in the status-report code where
there is a tiny special case for Python2/Python3. Compared to the total size
of over 2390 lines of the program, this is totally negligible.

Being free to use more elegant Python3 features can make the code
easier to read and maintain, which can reduce cognitive load over time.

The main change is that with Python3-only, the code can use more elegant
constructs like `contextlib.suppress` instead of try-except or
try-finally, and `f-strings` instead of the older `%` formatting.

However, removing these five simple if conditions that run next to no code
does not change the overall code that much.

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
