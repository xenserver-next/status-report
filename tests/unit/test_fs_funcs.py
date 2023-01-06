"""Regression tests for bugtool helper functions like get_recent_logs()"""


def test_get_recent_logs(bugtool):
    """Assert get_recent_logs() returning the most recent file(s)"""

    files = ["/proc/1/stat", "/proc/self/stat"]  # self/stat is more recent.
    # return the files, ordered by their modification time, most recent first:
    assert bugtool.get_recent_logs(files, 9) == files
    assert bugtool.get_recent_logs([files[1], files[0]], 9) == files
    # When verbosity is 1, only return the most recent file:
    assert bugtool.get_recent_logs(files, 1) == [files[1]]


def test_read_inventory(bugtool, dom0_template):
    """Assert readKeyValueFile() reading the a xensource inventory file"""

    inventory = bugtool.readKeyValueFile(dom0_template + bugtool.XENSOURCE_INVENTORY)
    assert inventory["PRODUCT_VERSION"] == "8.3.0"


def test_disk_list(bugtool):
    """Assert that the return value of disk_list() contains sda or nvme0n1"""
    assert "sda" in bugtool.disk_list() or "nvme0n1" in bugtool.disk_list()
