"""Regression tests for bugtool.load_plugins()"""


def test_load_plugins(bugtool, dom0_template):
    """Assert () returning arrays of the  in the dom0-template"""

    # Use the plugins found in the dom0_template "/etc/xensource/bugtool":
    bugtool.PLUGIN_DIR = dom0_template + "/etc/xensource/bugtool"
    # Only process the mock bugtool plugin:
    bugtool.entries = ["mock"]
    # Load the mock plugin:
    bugtool.load_plugins(just_capabilities=False)
    # Assert the set of properties of the created mock capability:
    assert bugtool.caps["mock"] == (
        "mock",
        "yes",
        -1,
        16384,
        -1,
        60,
        "text/plain",
        True,
        False,
        9,
    )
    # Assert the size of the files of the created mock inventory entry:
    assert bugtool.cap_sizes["mock"] > 0  # /etc/passwd should have content
    # Assert the entries added to the bugtool.data dict:
    assert bugtool.data == {
        "ls -l /etc": {
            "cap": "mock",
            "cmd_args": ["ls", "-l", "/etc"],
            "filter": None,
        },
        "/etc/passwd": {
            "cap": "mock",
            "filename": "/etc/passwd",
        },
        "/etc/group": {
            "cap": "mock",
            "filename": "/etc/group",
        },
        "/proc/self/status": {
            "cap": "mock",
            "filename": "/proc/self/status",
        },
        "proc_version": {
            "cap": "mock",
            "cmd_args": "cat /proc/version",
            "filter": None,
        },
    }

    # Assert the tree_output entries for /proc/sys/fs/inotify:
    entry_one, entry_two = bugtool.directory_specifications["/proc/sys/fs/inotify"]
    cap, regex, negate = entry_one
    assert cap == "mock"
    assert regex.pattern == ".*user_.*"
    assert negate
    cap, regex, negate = entry_two
    assert cap == "mock"
    assert regex.pattern == ".*max_user_instances.*"
    assert not negate

    # Assert the tree_output entry for /proc/sys/fs/epoll:
    entry_one, entry_two = bugtool.directory_specifications["/proc/sys/fs/epoll"]
    cap, regex, negate = entry_one
    assert cap == "mock"
    assert regex.pattern == ".*ax_user_watches"
    assert not negate
    cap, regex, negate = entry_two
    assert cap == "mock"
    assert regex.pattern == "no"
    assert not negate
