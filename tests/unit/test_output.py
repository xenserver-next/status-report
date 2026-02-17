"""Unit tests for bugtool core functions creating minimal output archives"""

import os
import tarfile
import zipfile

from lxml.etree import XMLSchema, parse  # pytype: disable=import-error

MOCK_EXCEPTION_STRINGS = (
    "Traceback (most recent call last):",
    ", in collect_data",
    ", in mock_data_collector",
    'raise Exception("mock data collector failed")',
    "Exception: mock data collector failed",
)


def mock_data_collector(capability):
    """Mock data collector for the mock plugin"""

    # Assert that the mock data collector is called with the correct capability:
    assert capability == "mock"

    # Raise an exception to test the backtrace output in the bugtool log:
    # sourcery skip: raise-specific-error
    # pylint: disable-next=broad-exception-raised
    raise Exception("mock data collector failed")


ETC_PASSWD = "/etc/passwd"


def assert_valid_inventory_schema(inventory_tree):
    """Assert that the passed inventory validates against the inventory schema"""

    inventory_schema = os.path.dirname(__file__) + "/../integration/inventory.xsd"
    with open(inventory_schema) as xml_schema:
        XMLSchema(parse(xml_schema)).assertValid(inventory_tree)


def assert_mock_bugtool_plugin_output(temporary_directory, subdir, names):
    """Assertion check of the output files from the mock bugtool plugin"""

    # Assert the list of file names in the status report archive:
    expected_names = [
        subdir + "/etc/group",
        subdir + "/etc/passwd.tar",
        subdir + "/function_output.out",
        subdir + "/inventory.xml",
        subdir + "/ls-l-%etc.out",
        subdir + "/proc/self/status",
        subdir + "/proc/sys/fs/epoll/max_user_watches",
        subdir + "/proc/sys/fs/inotify/max_queued_events",
        subdir + "/proc/sys/fs/inotify/max_user_instances",
        subdir + "/proc_version.out",
    ]
    assert sorted(names) == expected_names

    extracted = "%s/%s/" % (temporary_directory, subdir)

    # Will be refactored to be more easy in a separate commit soon:
    assert_valid_inventory_schema(parse(extracted + "inventory.xml"))
    with open(extracted + "proc_version.out") as proc_version:
        assert proc_version.read().startswith("Linux version ")
    with open(extracted + "ls-l-%etc.out") as etc:
        assert etc.read().startswith("total ")
    with open(extracted + "proc/self/status") as status:
        assert status.read().startswith("Name:")
    with open(extracted + "proc/sys/fs/epoll/max_user_watches") as max_user_watches:
        assert int(max_user_watches.read()) > 0
    with open(extracted + "etc/group") as group:
        assert group.readline() == "root:x:0:\n"

    # Check the contents of the sub-archive "etc/passwd.tar":
    with tarfile.TarFile(extracted + ETC_PASSWD + ".tar") as tar:
        assert tar.getnames() == [subdir + ETC_PASSWD]
        # TarFile.extractfile() does not support context managers on Python2:
        passwd = tar.extractfile(subdir + ETC_PASSWD)
        assert passwd
        assert passwd.readline() == b"root:x:0:0:root:/root:/bin/bash\n"
        passwd.close()


def minimal_bugtool(bugtool, dom0_template, archive, subdir, mocker):
    """Load the plugins from the template and include the generated inventory"""

    mocker.patch("bugtool.time.strftime", return_value="time.strftime")
    # Load the mock plugin from dom0_template and process the plugin's caps:
    bugtool.PLUGIN_DIR = dom0_template + "/etc/xensource/bugtool"
    bugtool.entries = ["mock"]
    archive.declare_subarchive(ETC_PASSWD, subdir + ETC_PASSWD + ".tar")
    # For code coverage: This sub-archive will not be created as it has no file
    archive.declare_subarchive("/not/existing", subdir + "/not_created.tar")
    bugtool.load_plugins(just_capabilities=False)

    # Add a mock data collector function to the mock plugin that raises an exception:
    bugtool.func_output("mock", "function_output.out", mock_data_collector)

    # Add collecting the xen-bugtool.log file (as CAP_XEN_BUGTOOL) to the archive:
    bugtool.file_output(bugtool.CAP_XEN_BUGTOOL, [bugtool.XEN_BUGTOOL_LOG])

    # Mock the 2nd argument of the ls -l /etc to collect it using dom0_template:
    bugtool.data["ls -l /etc"]["cmd_args"][2] = dom0_template + "/etc"

    # Collect the data from the mock plugin and write the output to the archive:
    bugtool.collect_data(subdir, archive)
    bugtool.include_inventory(archive, subdir)
    archive.close()


def assert_minimal_bugtool(bugtool, state_archive, dom0_template, cap):
    """Check the output of the bugtool unit test.
    :param bugtool: The tested bugtool module object
    :param state_archive: The tested bugtool output archive.
    :param dom0_template: The dom0 template used in the unit test.
    :param cap: The output (stdout, stderr) pytest captured from the unit test.

    :raises AssertionError: When the output does not match the expected output.
    """
    captured_stdout = cap.readouterr().out

    # When debug output from ProcOutput is enabled, "Starting" is printed:
    if bugtool.ProcOutput.debug:
        version = "/usr/sbin/cat /proc/version"
        etc_dir = "ls -l %s/etc" % dom0_template
        for msg in [version, etc_dir]:
            assert "[time.strftime]  Starting '%s'\n" % msg in captured_stdout

    # Assert that the backtrace from the mock data collector is printed:
    for backtrace_string in MOCK_EXCEPTION_STRINGS:
        assert backtrace_string in captured_stdout

    filetype = "tarball" if ".tar" in state_archive.filename else "archive"
    written = "Writing %s %s successful.\n" % (filetype, state_archive.filename)
    assert captured_stdout[-len(written) :] == written


def test_tar_output(bugtool, tmp_path, dom0_template, mocker, capfd):
    """Assert that a bugtool unit test creates a valid minimal tar archive"""

    bugtool.BUG_DIR = tmp_path
    archive = bugtool.TarOutput("tarball", "tar", -1)
    subdir = "tar_dir"

    # Create a minimal bugtool output archive to test core functions:
    bugtool.ProcOutput.debug = True
    minimal_bugtool(bugtool, dom0_template, archive, subdir, mocker)

    with capfd.disabled():
        assert_minimal_bugtool(bugtool, archive, dom0_template, capfd)

    # Check the TarFile contents
    tmp = tmp_path.as_posix()
    with tarfile.TarFile(tmp + "/tarball.tar") as tar:
        tar.extractall(tmp)
        assert_mock_bugtool_plugin_output(tmp, subdir, tar.getnames())


def test_zip_output(bugtool, tmp_path, dom0_template, mocker, capfd):
    """Assert that a bugtool unit test creates a valid minimal zip archive"""

    bugtool.BUG_DIR = tmp_path
    archive = bugtool.ZipOutput("zipfile")
    subdir = "zip_dir"

    # Create a minimal bugtool output archive to test core functions:
    bugtool.ProcOutput.debug = True
    minimal_bugtool(bugtool, dom0_template, archive, subdir, mocker)

    with capfd.disabled():
        assert_minimal_bugtool(bugtool, archive, dom0_template, capfd)

    # Check the ZipFile contents
    tmp = tmp_path.as_posix()
    with zipfile.ZipFile(tmp + "/zipfile.zip") as zip:
        zip.extractall(tmp)
        assert_mock_bugtool_plugin_output(tmp, subdir, zip.namelist())
