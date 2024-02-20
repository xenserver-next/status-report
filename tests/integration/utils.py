"""Utility functions to test xen-bugtool without any mocking"""

from __future__ import print_function

import filecmp
import os
import shutil
import sys
import tarfile
import zipfile
from subprocess import PIPE, Popen

from lxml.etree import XMLSchema, parse  # pytype: disable=import-error

# pyright: ignore[reportMissingImports]
if sys.version_info.major == 2:  # pragma: no cover
    from commands import getstatusoutput  # type:ignore[import-not-found]
else:
    from subprocess import getstatusoutput

BUGTOOL_OUTPUT_DIR = "/var/opt/xen/bug-report/"
BUGTOOL_DOM0_TEMPL = "tests/integration/dom0-template/"


def run(command):
    """Run the given shell command, print it's stdout and stderr and return them"""
    process = Popen(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    stdout, stderr = process.communicate()
    returncode = process.wait()
    print("# " + " ".join(command) + ":")
    if returncode:
        raise RuntimeError(returncode, stderr)
    print(stdout, stderr)
    return stdout, stderr


def assert_cmd(cmd, remove_file):
    """Run the given command, print its stdout and stderr and return them.

    Removes the given remove_file, the checks at the end of the tests cases
    expect all tested files to be removed, so they will discover file which
    have not been checked.
    """

    # If something causes an Exception, the remove_file will not be removed and
    # this will cause a final test failure check to trip and fail the test too:
    stdout, stderr = run(cmd)

    # After successful verification of the file, remove the checked output file:
    os.unlink(remove_file)
    return stdout, stderr


def assert_file(path, expected, only_first_line=False):
    """Return the contents of the passed bugtool output file for verification"""
    assert os.path.exists(path)
    with open(path) as handle:
        read_data = handle.read()
        if only_first_line:
            read_data = read_data.splitlines()[0]
        if read_data != expected:
            error_msg = "Data in %s does not match!" % path
            print(error_msg)
            print("- " + expected)
            print("+ " + read_data)
            #
            # Exit with an exception, and the file with unexpected contents
            # is also kept. Any files that are left in the extracted directory
            # will cause a final test failure check to trip and fail the test too:
            #
            assert RuntimeError(error_msg)

    # After successful verification of the file, remove the checked output file:
    os.unlink(path)


def assert_content_from_dom0_template(path, control_path=None):
    """Check the given path against the files from the test's Dom0 template"""

    assert path[0] != "/"  # We expect a relative path in the report archive
    control = BUGTOOL_DOM0_TEMPL + (control_path or path)
    print(control)
    if os.path.isdir(path):
        # path is a directory, compare it recursively using dircmp():
        result = filecmp.dircmp(path, control)
        if result.diff_files or result.right_only:  # pragma: no cover
            print(result.report)
            raise RuntimeError("Missing or Differing files found in " + path)
    else:
        if not os.path.exists(path):
            raise AssertionError("/%s is missing in the report archive" % path)
        if not filecmp.cmp(path, control):
            os.system("diff -u %s %s" % (path, control))  # pragma: no cover
            raise AssertionError("/%s from report has different content" % path)
    #
    # Remove the verified files and directories.
    #
    # The checks at the end of the tests cases expect all tested files to be removed,
    # so they will discover file which files have not been checked by the test.
    #
    try:
        os.unlink(path)
    except OSError:
        shutil.rmtree(path)


def extract(zip_or_tar_archive, archive_type):  # pragma: no cover
    """Extract a passed zip, tar or tar.bz2 archive into the current working directory"""
    if sys.version_info > (3, 0):
        if archive_type == "zip" and os.environ.get("GITHUB_ACTION"):
            # GitHub's Python3 is missing cp437 for unpack_archive()
            run(["unzip", zip_or_tar_archive])
        else:
            shutil.unpack_archive(zip_or_tar_archive)
    else:  # Python2.7 does not have shutil.unpack_archive():
        if archive_type == "zip":
            archive = zipfile.ZipFile(zip_or_tar_archive)  # type: zipfile.ZipFile|tarfile.TarFile
        elif archive_type == "tar":
            archive = tarfile.open(zip_or_tar_archive)
        elif archive_type == "tar.bz2":
            archive = tarfile.open(zip_or_tar_archive, "r:bz2")
        else:
            raise RuntimeError("Unsupported output archive type: %s" % archive_type)
        archive.extractall()
        archive.close()
    os.unlink(zip_or_tar_archive)


def run_bugtool_entry(archive_type, test_entries):
    """
    Execute the bugtool script with the given entries and prepare testing it.

    Prepare testing the output by extracting the bugball and switch into it.
    - Also validate the XMLSchema if the extracted inventory.xml so all tests
      have that check automatically.
    - Also create a symlink as ./tests that allows test cases to get test files.
    """

    os.environ["XENRT_BUGTOOL_BASENAME"] = test_entries

    command = "python%s ./xen-bugtool -y --output=%s --entries=%s" % (
        sys.version_info.major,
        archive_type,
        test_entries,
    )
    print("# " + command)
    error_code, output = getstatusoutput(command)

    print(output)
    if error_code:
        raise RuntimeError(output)

    src_dir = os.getcwd()

    #
    # Switch to the BUGTOOL_OUTPUT_DIR and extract the bugball in it.
    #
    # Because the test framework uses a tmpfs for it, it won't clutter
    # the development systems.
    #
    # This function leaves with the cwd in it for checking the output
    # data.
    #
    os.chdir(BUGTOOL_OUTPUT_DIR)
    extract(test_entries + "." + archive_type, archive_type)
    os.chdir(test_entries)

    # Validate the extracted inventory.xml using the XML schema from the test framework:
    with open(src_dir + "/tests/integration/inventory.xsd") as xml_schema:
        XMLSchema(parse(xml_schema)).assertValid(parse("inventory.xml"))
        # Remove valid inventory.xml (not removed files will make the tests fail):
        os.unlink("inventory.xml")
    # Add a symlink, so assert_content_from_dom0_template() can find the tests:
    os.symlink(src_dir + "/tests", "tests")
