"""tests/integration/utils.py: utility functions to test xen-bugtool by invoking it"""
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
if sys.version_info.major == 2:
    from commands import getstatusoutput  # type:ignore[import-not-found] # pragma: no cover
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
    """Run the given command, print its stdout and stderr and return them. Remove the given remove_file"""
    stdout, stderr = run(cmd)
    # After successfuly verficiation of the files, remove the checked output file(missed files remain):
    os.unlink(remove_file)
    return stdout, stderr


def check_file(path):
    """Return the contents of the passed bugtool output file for verification"""
    with open(path) as handle:
        contents = handle.read()
    # After successfuly verficiation of the files, remove the checked output file (missed files remain):
    os.unlink(path)
    return contents


def assert_content_from_dom0_template(path, control_path=None):
    """Compare the contents of output directories or files with the test's Dom0 template directories"""
    assert path[0] != "/"
    control = BUGTOOL_DOM0_TEMPL + (control_path or path)
    print(control)
    if os.path.isdir(path):
        result = filecmp.dircmp(path, control)
        if result.diff_files or result.right_only:  # pragma: no cover
            print(result.report)
            raise RuntimeError("Missing or Differing files found in " + path)
    else:
        if not filecmp.cmp(path, control):
            os.system("cat " + path)  # pragma: no cover
            raise RuntimeError(control)
    # Remove verified output files/directories. Untested files will remain and cause the testcase to FAIL:
    try:
        os.unlink(path)
    except OSError:
        shutil.rmtree(path)


def extract(zip_or_tar_archive, archive_type):  # pragma: no cover
    """Extract a passed zip, tar or tar.bz2 archive into the current working directory"""
    if sys.version_info > (3, 0):
        if archive_type == "zip" and os.environ.get("GITHUB_ACTION"):
            run(["unzip", zip_or_tar_archive])  # GitHub's Py3 is missing cp437 for unpack_archive()
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
    """Run bugtool for the given entry or entries, extract the output, and chdir to it"""
    os.environ["XENRT_BUGTOOL_BASENAME"] = test_entries
    # For case the default python interpreter of the user is python3, we must use python2(for now):
    command = "python2 ./xen-bugtool -y --output=%s --entries=%s" % (archive_type, test_entries)
    print("# " + command)
    error_code, output = getstatusoutput(command)
    print(output)
    if error_code:
        raise RuntimeError(output)
    src_dir = os.getcwd()
    os.chdir(BUGTOOL_OUTPUT_DIR)
    output_file = test_entries + "." + archive_type
    print("# Unpacking " + BUGTOOL_OUTPUT_DIR + output_file + " and verifying inventory.xml")
    extract(output_file, archive_type)
    os.chdir(test_entries)
    # Validate the extracted inventory.xml using the XML schema from the test framework:
    with open(src_dir + "/tests/integration/inventory.xsd") as xml_schema:
        XMLSchema(parse(xml_schema)).assertValid(parse("inventory.xml"))
        # Remove valid inventory.xml (not removed files will make the tests fail):
        os.unlink("inventory.xml")
    # Add a symlink, so assert_content_from_dom0_template() can find the tests:
    os.symlink(src_dir + "/tests", "tests")
