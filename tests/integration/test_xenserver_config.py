"""Test xen-bugtool --entries=server-config"""

import os

from .utils import (
    assert_cmd,
    assert_file,
    run_bugtool_entry,
    assert_content_from_dom0_template,
)


def test_xenserver_config(output_archive_type):
    """
    Run xen-bugtool --entries=xenserver-config in test jail
    (created by auto-fixtures, see README-pytest-chroot.md)
    """
    entry = "xenserver-config"

    run_bugtool_entry(output_archive_type, entry)

    # Check the output of xen-bugtool --entries=xenserver-config:

    assert_file("ls-lR-%opt%xensource.out", "/opt/xensource:", only_first_line=True)
    assert_file("ls-lR-%etc%xensource%static-vdis.out", "")
    assert_file("static-vdis-list.out", "list")

    # Assert the contents of the extracted etc/systemd.tar

    # etc/systemd.tar's toplevel directory is os.environ["XENRT_BUGTOOL_BASENAME"]
    os.chdir("..")

    # Extract the etc/systemd.tar file:
    assert_cmd(["tar", "xvf", entry + "/etc/systemd.tar"], entry + "/etc/systemd.tar")

    # Change back to the bugtool output to check the etc/systemd directory:
    os.chdir(entry)

    assert_content_from_dom0_template("etc/systemd")
    assert_content_from_dom0_template("etc/xensource-inventory")

    # Sample SNMP config files are currently not in the dom0_template!
    # Reading them records the error message in the file content, do we want this?
    # I think the "Failed to filter" is redundant in it.
    # Maybe decide on a standardized error for missing files in bugtool?

    # TODO: To be clarified or fixed as part of CP-46759 or a follow-up!

    for input_file in [
        "/etc/snmp/snmp.xs.conf",
        "/etc/snmp/snmpd.xs.conf",
        "/var/lib/net-snmp/snmpd.conf",
    ]:
        assert_file(
            input_file.split("/")[-1].replace(".", "_") + ".out",
            # That's a very long error message an the 1st two parts are redundant:
            "Failed to filter %s "
            "[Errno 2] "
            "No such file or directory: '%s'" % (input_file, input_file),
        )
