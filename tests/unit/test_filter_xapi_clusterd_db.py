"""tests/unit/test_filter_xapi_clusterd_db.py: Test filter_xapi_clusterd_db()

TODO:

This test must be made to fail to cover two current bugtool bugs
because the filter_xapi_clusterd_db() function is not implemented correctly.

Current Bugs in filter_xapi_clusterd_db():

1.  The filter must replace "token": "secret-token", with "token": "REMOVED"
2.  The filter must also work if the "pems" key is missing
3.  The filter must also work if "pems.blobs" is missing
4.  The filter must also work if "authkey" is missing
    Points 2-4 above apply to "cluster_config" and "old_cluster_config".

Explanation for PASS tests: Those are the cases that are currently passing.
Explanation for XFAIL tests: Those are the cases that are currently failing
and must be fixed:
- They use the pytest.mark.xfail decorator to mark the tests as expected to fail.
- They are marked with "XFAIL" in the test output.
- The pytest.mark.xfail decorator must be removed after the bug is fixed
  to ensure the test is run and passes in the future.

TODO START:

1.  Add additional XFAIL tests, one for each, which fail on the cases above
[DONE]

2.  Add additional PASS test:
    The filter must also work if "cluster_config" or/and "old_cluster_config"
    are missing.
[DONE]

3.  Add additional PASS test:
    The filter must also work if the "token" key is missing.
[DONE]

4.  The changes are added as additional commits and pushed.
    The individual sub-tests must be shown failing on each the cases above.
[DONE] (done for each case)

5.  The filter must be updated to handle these cases.
[DONE] (done for each case)

6.  The PR is then pushed again and then pass.
[DONE]

    Changes to the test should only be needed if e.g. logging was added
    to test the logging output.

Ideally, if there is capacity for it, pre-commit hooks should run on every
commit to ensure that each works without any errors

This can be done by running:
    git rebase -x 'pre-commit run --from-ref HEAD~ --to-ref HEAD' HEAD~1
[DONE] (for all commits in this PR)

Replace the `1` with the number of commits to run the pre-commit hooks on.
This opens an editor with the commits and checks to run on them. When it,
by mistake contains one or more commits that are not only the ones that
are in the current PR, remove them all commits from the editor and save
the file. In this case `git rebase` will do nothing and no commits are changed.

With all of these TODO done, step-by-step, in order, work will be complete.

Tip:

Run `pip install pre-commit` and then use `pre-commit run`
to check the code and run all unit tests and checks before committing
and pushing the code.

pre-commit run will:
- remove trailing whitespace from the code for uniformity
- fix the code style of the tests with black and of xen-bugtool with darker
- run unit tests with coverage and check the coverage on the changed lines

If you run `pre-commit install`, it will run on every commit in your own clone.

TODO END.

"""

import json
import os

import pytest


# Minimal example of a xapi-clusterd/db file, with sensitive data
# BUG: The new cluster_config has no "pems" key, so the filter has to be updated
# to handle this case, pass data and still filter the "old_cluster_config" key.
ORIGINAL = r"""
{
    "token": "secret-token",
    "cluster_config": {
        "pems": {
            "blobs": "secret-blob"
        },
        "authkey": "secret-key"
    },
    "old_cluster_config": {
        "pems": {
            "blobs": "secret-blob"
        },
        "authkey": "secret-key"
    },
    "max_config_version": 1
}"""

# Same as original, but with passwords and private data replaced by: "REMOVED"
# BUG: "secret-token" has to be replaced by "REMOVED"
EXPECTED = r"""{
    "token": "REMOVED",
    "cluster_config": {
        "pems": {
            "blobs": "REMOVED"
        },
        "authkey": "REMOVED"
    },
    "old_cluster_config": {
        "pems": {
            "blobs": "REMOVED"
        },
        "authkey": "REMOVED"
    },
    "max_config_version": 1
}"""


def assert_filter_xapi_clusterd_db(bugtool, original, expected):
    """Assert that filter_xapi_clusterd_db() replaces sensitive strings"""

    # -------------------------------------------------------------------------
    # Common setup:
    # -------------
    # - Define the file name of the temporary xAPI clusterd db.
    #
    # Notes:
    # ------
    # - To allow for checking of logged errors, the tmpdir fixture is used.
    #
    # - The tmpdir fixture changes the current working directory to a temporary
    #   directory, so that temporary files that are not explicitly created in
    #   another temporary directory are created in its temporary directory.
    #
    # - After the test function returns, the tmpdir fixture checks for any
    #   temporary files that were created in the temporary directory and
    #   will raise an error if any are found, so that the code can be fixed
    #   to not leave temporary files behind.
    #
    #   For example, if bugtool function calls `log()` to log an error, this
    #   will create the xen-bugtool.log file in the temporary directory.
    #
    #   The tmpdir fixture will raise an error if the xen-bugtool.log file is
    #   found in the temporary directory after the test function returns.
    #
    #   This way, the errors are caught and fixed before the code is pushed.
    #
    # - Another benefit of using the tmpdir fixture is that because the
    #   fixture already changes the current working directory to a temporary
    #   directory, the path to the temporary directory is not needed to be
    #   passed to the test functions, and the test functions can be written
    #   in a more readable way.
    #
    #   For example, the path to the temporary directory is not needed to be
    #   passed and used in this function to create the temporary xAPI clusterd
    #   db file, and the test function can be written in a more readable way.
    #
    temporary_test_clusterd_db = "xapi_clusterd_db.json"
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Prepare:
    # --------
    #
    # 1. Write the original xapi-clusterd/db contents to the temporary file
    # 2. Patch the bugtool module to use the temporary file for reading the db
    #
    with open(temporary_test_clusterd_db, "w") as f:
        f.write(original)

    bugtool.XAPI_CLUSTERD = temporary_test_clusterd_db
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Act:
    # ----
    #
    # -> Call the  filter function
    #
    filtered = bugtool.filter_xapi_clusterd_db("_")
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Assert:
    # -------
    #
    # -> Compare the filtered output with the expected output
    #
    try:
        assert json.loads(filtered) == json.loads(expected)
    except ValueError:  # For invalid json (to test handing of corrupted db)
        assert filtered == expected

    os.remove(temporary_test_clusterd_db)
    # -------------------------------------------------------------------------


@pytest.mark.usefixtures("tmpdir")
def test_pems_blobs(bugtool):
    """Assert that filter_xapi_clusterd_db() replaces pems.blobs strings"""
    assert_filter_xapi_clusterd_db(bugtool, ORIGINAL, EXPECTED)


# CA-358870: filter_xapi_clusterd_db: remove token from the report
@pytest.mark.usefixtures("tmpdir")
def test_remove_token(bugtool):
    """CA-358870: Assert that filter_xapi_clusterd_db() removes the token"""

    # Load the expected output and remove the token from it
    expected = json.loads(EXPECTED)
    expected["token"] = "REMOVED"
    expected_json = json.dumps(expected)

    assert_filter_xapi_clusterd_db(bugtool, ORIGINAL, expected_json)


# CA-388587: filter_xapi_clusterd_db: do not fail on missing authkey
@pytest.mark.usefixtures("tmpdir")
def test_no_authkey(bugtool):
    """Assert that filter_xapi_clusterd_db() handles missing authkey"""

    def remove_authkey(json_data):
        """Remove the authkey from the clusterd db"""
        data = json.loads(json_data)
        # sourcery skip: no-loop-in-tests
        for key in ["cluster_config", "old_cluster_config"]:
            if "authkey" in data[key]:
                data[key].pop("authkey")
        return json.dumps(data)

    assert_filter_xapi_clusterd_db(
        bugtool,
        remove_authkey(ORIGINAL),
        remove_authkey(EXPECTED),
    )


# CA-388587: filter_xapi_clusterd_db: do not fail on missing pems
@pytest.mark.usefixtures("tmpdir")
def test_no_pems(bugtool):
    """Assert that filter_xapi_clusterd_db() handles missing pems"""

    def remove_pems(json_data):
        """Remove the pems key from the clusterd db"""
        data = json.loads(json_data)
        # sourcery skip: no-loop-in-tests
        for key in ["cluster_config", "old_cluster_config"]:
            if "pems" in data[key]:
                data[key].pop("pems")
        return json.dumps(data)

    assert_filter_xapi_clusterd_db(
        bugtool,
        remove_pems(ORIGINAL),
        remove_pems(EXPECTED),
    )


# CA-388587: filter_xapi_clusterd_db: do not fail on missing pems.blobs
@pytest.mark.usefixtures("tmpdir")
def test_no_blobs(bugtool):
    """Assert that filter_xapi_clusterd_db() handles missing pems.blobs"""

    def remove_blobs(json_data):
        """Remove the pems.blobs key from the clusterd db"""
        data = json.loads(json_data)
        # sourcery skip: no-loop-in-tests
        for key in ["cluster_config", "old_cluster_config"]:
            if "pems" in data[key] and "blobs" in data[key]["pems"]:
                data[key]["pems"].pop("blobs")
        return json.dumps(data)

    assert_filter_xapi_clusterd_db(
        bugtool,
        remove_blobs(ORIGINAL),
        remove_blobs(EXPECTED),
    )


@pytest.mark.usefixtures("tmpdir")
def test_no_config(bugtool):
    """Assert that filter_xapi_clusterd_db() handles missing cluster_configs"""

    def remove_cluster_configs(json_data):
        """Remove the {,old_}cluster_configs keys from the clusterd db"""
        data = json.loads(json_data)
        data.pop("cluster_config")
        data.pop("old_cluster_config")
        return json.dumps(data)

    assert_filter_xapi_clusterd_db(
        bugtool,
        remove_cluster_configs(ORIGINAL),
        remove_cluster_configs(EXPECTED),
    )


@pytest.mark.usefixtures("tmpdir")
def test_no_token(bugtool):
    """Assert that filter_xapi_clusterd_db() handles missing token"""

    def remove_cluster_token(json_data):
        """Remove the token key from the clusterd db"""
        data = json.loads(json_data)
        data.pop("token")
        return json.dumps(data)

    assert_filter_xapi_clusterd_db(
        bugtool,
        remove_cluster_token(ORIGINAL),
        remove_cluster_token(EXPECTED),
    )


@pytest.mark.usefixtures("tmpdir")
def test_no_database(bugtool):
    """Assert that filter_xapi_clusterd_db() handles missing token"""

    bugtool.XAPI_CLUSTERD = "/does/not/exist"
    assert bugtool.filter_xapi_clusterd_db("_") == ""


@pytest.mark.usefixtures("tmpdir")
def test_invalid_db(bugtool, capsys):
    """Assert how filter_xapi_clusterd_db() handles a corrupted db"""

    # The filter must handle invalid json and return the expected output,
    # which no output, as the db is not readable and the filter should
    # return an empty string (in an ideal world, it would return an error message)
    assert_filter_xapi_clusterd_db(bugtool, "invalid json", "")

    with capsys.disabled():
        stdout = capsys.readouterr().out
        assert stdout.startswith("bugtool: Internal error: ")
        assert "filter_xapi_clusterd_db" in stdout
        assert "JSON" in stdout

    with open(bugtool.XEN_BUGTOOL_LOG, "r") as f:
        log = f.read()
        assert "Internal error" in log
        assert "filter_xapi_clusterd_db" in log
        assert "JSON" in log

    os.remove(bugtool.XEN_BUGTOOL_LOG)
