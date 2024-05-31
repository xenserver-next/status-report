"""tests/unit/test_filter_xapi_clusterd_db.py: Test filter_xapi_clusterd_db()

Steps taken for TDD - Test-Driven Develpment - for fixing CA-388587:

To write reliable unit tests, always start writing a failing test. And make
sure it fails for the right reasons.

Follow the Red, Green, Refactor principle of Test-Driven Development (TDD).

- Write a failing test (Red)
- make it pass, and    (Green)
- refactor the code.   (Refactor)

This plan was used for TDD of these test cases:
-----------------------------------------------

These tests were made to initially fail to cover two current bugtool bugs
because the filter_xapi_clusterd_db() function is not implemented correctly.

Now fixed bugs in filter_xapi_clusterd_db():

1.  The filter must replace "token": "secret-token" with: "token": "REMOVED"
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

DONE:
1.  Add additional XFAIL tests, one for each, which fail on the cases above
2.  Add additional PASS test:
    The filter must also work if "cluster_config" or/and "old_cluster_config"
    are missing.
3.  Add additional PASS test:
    The filter must also work if the "token" key is missing.
4.  The changes are added as additional commits and pushed.
    The individual sub-tests must be shown failing on each the cases above.
5.  The filter must be updated to handle these cases.
6.  The PR is then pushed again and then pass.
    Changes to the test should only be needed if e.g. logging was added
    to test the logging output.
"""

import json
import os
import re

import pytest

# Minimal example of a xapi-clusterd/db file, with sensitive data
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

    # -> Common setup: Define the file name of the temporary xAPI clusterd db.
    #
    temporary_test_clusterd_db = "tmp/xapi_clusterd_db.json"

    # -> Prepare:
    #
    # 1. Write the original xapi-clusterd/db contents to the temporary file
    # 2. Patch the bugtool module to use the temporary file for reading the db
    #
    with open(temporary_test_clusterd_db, "w") as f:
        f.write(original)

    bugtool.XAPI_CLUSTERD = temporary_test_clusterd_db

    # -> Act: Call the  filter function
    #
    filtered = bugtool.filter_xapi_clusterd_db("_")

    # -> Assert: Compare the filtered output with the expected output
    #
    try:
        assert json.loads(filtered) == json.loads(expected)
    except ValueError:  # For invalid json (to test handing of corrupted db)
        assert filtered == expected

    # -> Cleanup: Remove the temporary xapi clusterd file
    #
    # Remove the temporary file for the xapi-clusterd/db contents after the test
    # is done. The test fixtures used by the test functions check that the test
    # did not cause xen-bugtool to leave any temporary files files behind,
    # and this temporary file would also trigger that check.
    #
    os.remove(temporary_test_clusterd_db)


def test_removal_of_all_secrets(isolated_bugtool):
    """Assert that filter_xapi_clusterd_db() replaces all secrets in the db"""
    assert_filter_xapi_clusterd_db(isolated_bugtool, ORIGINAL, EXPECTED)


def check_assert_on_unexpected_differences_in_output(bugtool, expected, diff):
    """Self-test: Ensure that the assertion function asserts on unexpected output"""

    # -> Test setup:
    #
    # The expected output is modified to contain an unexpected token value
    # that should cause the assertion function to fail.

    # -> Act: Call the assertion function
    with pytest.raises(AssertionError) as exc_info:
        assert_filter_xapi_clusterd_db(bugtool, ORIGINAL, json.dumps(expected))

    # -> Assert: Check that the assertion function failed on the unexpected output
    #
    # The assertion function should assert on the differing token value
    # and the diff should be in the assertion error message

    if diff not in exc_info.value.args[0]:  # pragma: no cover
        print(exc_info.value.args)
        pytest.fail("The assertion function did not assert on the unexpected output")


def test_assertion_on_unexpected_token(isolated_bugtool):
    """Self-test: Ensure that the assertion function asserts on unexpected token"""

    # -> Test setup: Modify the expected output to contain an unexpected token value

    expected = json.loads(EXPECTED)
    expected["token"] = "unexpected token value"

    # -> Act and assert: Check that the assertion function fails on the unexpected output
    #    The assertion function should assert on the differing authkey value and the
    #    diff with the wrongly expected string should be in the assertion error message
    #
    # pytest-8 adds very fine-grained coloring of the assertion error message
    # which makes it harder to match the diff string in the assertion error message.
    # Apparently, we cannot disable the coloring for a single assertion, so we can
    # only check for the the unexpected token in the assertion:

    diff = "'token': 'unexpected token value'"
    check_assert_on_unexpected_differences_in_output(isolated_bugtool, expected, diff)


def test_assertion_on_unexpected_authkey(isolated_bugtool):
    """Self-test: Ensure that the assertion function asserts on unexpected authkey"""

    # -> Test setup: Modify the expected output to contain an unexpected authkey value

    expected = json.loads(EXPECTED)
    expected["cluster_config"]["authkey"] = "unexpected authkey value"

    # -> Act and assert: Check that the assertion function fails on the unexpected output
    #    The assertion function should assert on the differing authkey value
    #    and the wrongly expected string should be in the assertion error message

    diff = "unexpected authkey value"
    check_assert_on_unexpected_differences_in_output(isolated_bugtool, expected, diff)


def test_no_authkey(isolated_bugtool):
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
        isolated_bugtool,
        remove_authkey(ORIGINAL),
        remove_authkey(EXPECTED),
    )


def test_no_pems(isolated_bugtool):
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
        isolated_bugtool,
        remove_pems(ORIGINAL),
        remove_pems(EXPECTED),
    )


def test_no_blobs(isolated_bugtool):
    """Assert that filter_xapi_clusterd_db() handles missing blobs"""

    def remove_blobs(json_data):
        """Remove the pems.blobs key from the clusterd db"""
        data = json.loads(json_data)
        # sourcery skip: no-loop-in-tests
        for key in ["cluster_config", "old_cluster_config"]:
            if "pems" in data[key] and "blobs" in data[key]["pems"]:
                data[key]["pems"].pop("blobs")
        return json.dumps(data)

    assert_filter_xapi_clusterd_db(
        isolated_bugtool,
        remove_blobs(ORIGINAL),
        remove_blobs(EXPECTED),
    )


def test_no_config(isolated_bugtool):
    """Assert that filter_xapi_clusterd_db() handles missing cluster_configs"""

    def remove_cluster_configs(json_data):
        """Remove the {,old_}cluster_configs keys from the clusterd db"""
        data = json.loads(json_data)
        data.pop("cluster_config")
        data.pop("old_cluster_config")
        return json.dumps(data)

    assert_filter_xapi_clusterd_db(
        isolated_bugtool,
        remove_cluster_configs(ORIGINAL),
        remove_cluster_configs(EXPECTED),
    )


def test_no_token(isolated_bugtool):
    """Assert that filter_xapi_clusterd_db() handles missing token"""

    def remove_cluster_token(json_data):
        """Remove the token key from the clusterd db"""
        data = json.loads(json_data)
        data.pop("token")
        return json.dumps(data)

    assert_filter_xapi_clusterd_db(
        isolated_bugtool,
        remove_cluster_token(ORIGINAL),
        remove_cluster_token(EXPECTED),
    )


def test_no_database(isolated_bugtool):
    """Assert that filter_xapi_clusterd_db() handles missing token"""

    isolated_bugtool.XAPI_CLUSTERD = "/does/not/exist"
    assert isolated_bugtool.filter_xapi_clusterd_db("_") == ""


def test_invalid_db(isolated_bugtool, capsys):
    """Assert how filter_xapi_clusterd_db() handles a corrupted db"""

    # The filter must handle invalid json and return the expected output,
    # which no output, as the db is not readable and the filter should
    # return an empty string (in an ideal world, it would return an error message)
    assert_filter_xapi_clusterd_db(isolated_bugtool, "invalid json", "")

    with capsys.disabled():
        stdout = capsys.readouterr().out
        assert stdout.startswith("bugtool: Internal error: ")
        assert "filter_xapi_clusterd_db" in stdout
        assert "JSON" in stdout

    with open(isolated_bugtool.XEN_BUGTOOL_LOG, "r") as f:
        log = f.read()
        assert "filter_xapi_clusterd_db" in log
        assert "JSON" in log

    # Python2 error message
    log = re.sub(r"(?s)bugtool: Internal error:.*could be decoded\n\n", "", log)

    # Python3 error message is different
    log = re.sub(r"(?s)bugtool: Internal error:.*umn 1 \(char 0\)\n\n", "", log)

    with open(isolated_bugtool.XEN_BUGTOOL_LOG, "w") as f:
        f.write(log)
