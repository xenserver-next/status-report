"""Regression tests for the bugtool helper function mdadm_arrays()"""


def test_mdadm_arrays(bugtool, dom0_template):
    """Assert mdadm_arrays() returning arrays dom0_template/usr/sbin/mdadm"""
    bugtool.MDADM = dom0_template + "/usr/sbin/mdadm"
    assert list(bugtool.mdadm_arrays()) == ["/dev/md0", "/dev/md1"]


def test_module_info(bugtool, dom0_template):
    """Assert module_info() returning module names from test_module_info.modules"""

    bugtool.PROC_MODULES = __file__.replace(".py", ".modules")
    bugtool.MODINFO = dom0_template + "/usr/sbin/modinfo"
    output = bugtool.module_info(bugtool.CAP_KERNEL_INFO)
    assert output == "modinfo for tcp_diag\nmodinfo for udp_diag\nmodinfo for inet_diag\n"


def test_multipathd_topology(bugtool, dom0_template):
    """Assert multipathd_topology() returning the output of the faked multipathd tool"""

    bugtool.MULTIPATHD = dom0_template + "/usr/sbin/multipathd"
    assert bugtool.multipathd_topology(bugtool.CAP_MULTIPATH) == "multipathd-k"
