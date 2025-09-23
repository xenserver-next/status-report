# Unit tests with Code coverage with Codecov and Coveralls

[`pre-commit`](coverage.md) runs `pytest --cov` to collect code coverage
in its native SQLite database in the file `.coverage` and to generate
`xml` and `html` reports for upload and local viewing.

Responsible for tracing the collect the coverage is the Coverage.py package:
- https://coverage.readthedocs.io/en/latest/index.html

Pytest-cov integrates it into pytest and allows to configure it fine-grained:
- https://pytest-cov.readthedocs.io/en/latest/

### Coverage visualization using local html
[`pre-commit`](coverage.md) `pytest --cov` using the flags to create coverage reports in
`.git/coverage.html/index.html` for Python 3.

It runs a JavaScript application to visualize the Coverage data.
Simply download or move `.git/coverage.html` to a folder that you can open
with a regular JavaScript Web browser.


### Coverage visualization using Online services
[`pre-commit`](coverage.md) runs `pytest --cov` to collect code coverage from
unit tests and [GitHub CI](../.github/workflows/main.yml) uploads them to:
- https://app.codecov.io/gh/xenserver/status-report
- https://coveralls.io/github/xenserver/status-report

[Codecov.io](https://codecov.io) has more features, but it has some drawbacks:
- Their free plan only includes one developer, but may work after approval:
  - Access needs to be granted by their owner of the repository or the organisation.
- Uploads can be unreliable at times.

[Coveralls.io](https://Coveralls.io) is a good alternative that is much simpler:
- To access the coverage there, only a login using your GitHub account.

Both services are available since some time and are used by many other projects.
- For XenServer's use with a team of developers, both are in early exploration.
- The focus is on learning as a team which service works best in our daily use.

Both services have one big Caveat:

- They compare the lines that were covered before with the new line coverage.
- But if a pull request that changed code coverage gets merged, other branches
  for which CI uploads Code coverage must be rebased to the latest master.
  - If this is not done, Codecov.io may report a reduction of coverage and fail.
  - Therefore, always rebase new pushes onto the latest master.
  - **If you get an error for reduced coverage, rebase to the latest master.**
