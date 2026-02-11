# Running checks using pre-commit

## Running CI checks locally (and in GitHub CI) using `pre-commit`

This project uses `pre-commit` to run the tests in a defined, clean environment:

- It fixes the code style of the tests with black and of `xen-bugtool` with darker
- It runs `pytest` with coverage and checks the coverage on the changed lines
- It runs `pylint`, `mypy`, `pyright` and `pytype`:

The pre-commit configuration defines how it runs
`pytest`, `pylint` and static analysis using `mypy`, `pyright`, and `pytype`.

Links:

- <https://mypy.readthedocs.io/en/stable/>
- <https://microsoft.github.io/pyright/>
- <https://google.github.io/pytype/user_guide.html>

- Because this project is now using Python3.6+, type annotations (PEP 484)
  no longer need to be in comments, but can be in the code directly.

  However, for compatibility with Python3.6 and type annotations like `list[str]`
  and `str | None` are not supported in Python3.6, so the older syntax
  `List[str]` and `Optional[str]` from the `typing` module have to be used,
  or continue to use type comments as before (described in PEP 484).
  See https://docs.python.org/3/library/typing.html#typing.List

To run all checks on all files, run:

```bash
uv pip install pre-commit
. .venv/bin/activate  # (if using a virtualenv)
pre-commit run -av
```

Without -a, it would only run hooks for staged files with changes.
With `-a`, `pre-commit run -a` runs all fixes and checks.

You can skip checks if you commit by passing `SKIP=` in the environment:

```py
export SKIP=mypy,pylint;git commit -m "quick save"  # (or for --amend)
```

Only the 1st invocation of pre-commit will be slow as it creates `virtualenv`s
for each sub-hook configured in its configuration file
[`.pre-commit-config.yaml`](.pre-commit-config.yaml). Subsequent runs are fast.

If a formatting hook like trailing-whitespace fails, just run `git add -p` to
stage the whitespace fixes into the index and run pre-commit again.
Or, if you already installed pre-commit as a git commit hook, commit again.

When you are ready to use pre-commit as a pre-commit hook in this clone,
run this command to install it. Until uninstalled from this repo, it will
then run on each commit. This is completely optional and just a matter of
preference:

```bash
pre-commit install
```

## Videos about pre-commit

### The easy way to keep your repos tidy (5 minutes)
[![The easy way to keep your repos tidy.](https://img.youtube.com/vi/psjz6rwzMdk/0.jpg)](https://www.youtube.com/watch?v=psjz6rwzMdk)

### Python Pre-Commit Hooks Setup in a single video (9 minutes)
[![Python Pre-Commit Hooks Setup in a single video](https://img.youtube.com/vi/Wmw-VGSjSNg/0.jpg)](https://www.youtube.com/watch?v=Wmw-VGSjSNg)

### Configuring Pre-Commit Hooks to Automate Python Testing and Linting in vscode (15 mins)
[![Configuring Pre-Commit Hooks to Automate Python Testing and Linting in vscode](https://img.youtube.com/vi/moVieAAk_xo/0.jpg)](https://www.youtube.com/watch?moVieAAk_xo)

## Advanced: Run pre-commit hooks as part of `git rebase -i`

Ideally, if possible, pre-commit hooks should run on every commit to ensure that
each works without any errors, even when checking out an intermediary commit.
This is needed to allow for `git bisect` for finding commits causing breakage.

However, by default, `pre-commit` does not run during `git rebase` commands.
It checks only regular commits, not amends and not rebases.

`pre-commit` can be run during `git rebase` explicitly by using:
    git rebase -x 'pre-commit run --from-ref HEAD~ --to-ref HEAD' HEAD~1

Note: Replace the `1` with the number of commits to run the pre-commit hooks on.

When moving changes between commits while rebasing, they can get broken.

To fix these issues to make them clean for `git bisect` and make each
new commit in the stack work for itself, you can use a git alias:

```ml
[alias]
    prebase = rebase -x 'pre-commit run --from-ref HEAD~ --to-ref HEAD'
```

When using `git prebase -i` instead of `git rebase -i`, pre-commit will
run the configured commit hooks for each commit of the rebase.

This ensures that tests also pass on each intermediate commit.

When, during a `git prebase -i`, a pre-commit hook fails or makes changes,
the `rebase` stops. These are the steps to fix such failed rebase:

- Review which errors were raised by the `pre-commit` hooks.
- In case formatters fixed the causes already, check `git diff`.
- Fix the errors and stage the fixes using `git add <file>`.
- Run `git rebase --continue` to try to continue the rebase to the next step.

A very helpful explanation by the author of a book on git is here:
<https://adamj.eu/tech/2022/11/07/pre-commit-run-hooks-rebase/>
