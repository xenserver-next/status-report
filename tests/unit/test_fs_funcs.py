"""Regression tests for bugtool helper functions like get_recent_logs()"""


def test_read_inventory(bugtool, dom0_template):
    """Assert readKeyValueFile() reading the a xensource inventory file"""

    inventory = bugtool.readKeyValueFile(dom0_template + bugtool.XENSOURCE_INVENTORY)
    assert inventory["PRODUCT_VERSION"] == "8.3.0"


def test_disk_list(bugtool):
    """Assert that the return value of disk_list() contains sda or nvme0n1"""
    assert "sda" in bugtool.disk_list() or "nvme0n1" in bugtool.disk_list()
