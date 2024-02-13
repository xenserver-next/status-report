"""tests/unit/test_dir_list.py: Unit-Test bugtool.dir_list(cap, path_list)"""


def test_dir_list(bugtool):
    """Test the bugtool function dir_list(cap, path_list) to perform as expected"""

    # Arguments for the positive test:
    cap = bugtool.CAP_XENSERVER_CONFIG
    path_list = [__file__.replace(".", "*")]

    # Assert that mis-matching cap causes no output in bugtool.data:
    bugtool.entries = [bugtool.CAP_DISK_INFO, cap, bugtool.CAP_PAM]
    bugtool.dir_list(cap=bugtool.CAP_XENSERVER_LOGS, path_list=path_list)
    assert bugtool.data == {}

    # Assert that mis-matching path_list results in no bugtool.data:
    bugtool.dir_list(cap=cap, path_list=[__file__ + "*notexist*"])
    assert bugtool.data == {}

    # Assert matching cap and path_list produces expected_data
    bugtool.dir_list(cap=cap, path_list=path_list)

    expected_data = {
        "ls -l "
        + __file__: {
            "filter": None,
            "cap": "xenserver-config",
            "cmd_args": [
                "ls",
                "-l",
                __file__,
            ],
        }
    }
    assert bugtool.data == expected_data
