#!/bin/bash
# This test is expected to be run as root in a container(docker, podman, toolbox, apptainer, (s)chroot):
# It is currently started from .github/workflows/tests.yml
# Precondition: python with all dependencies from requirements.txt is installed
# WARNING: This is running as user root in the container it runs in!
#
# exit on any error
set -o errexit
set -o pipefail
if [[ -n "$TRACE" ]]; then set -o xtrace; fi
set -o nounset
: ${PYTHON:=python2}

# Prepare test container: Mock the files used by this test
cp -a tests/integration/dom0-template/* /
mkdir -p  /var/log/sa
echo sa  >/var/log/sa/sa01
echo sr  >/var/log/sa/sar31
ln -sf    /bin/echo /bin/sar

# Enter a clean test environment
rm -rf   .tmp/tests/sar-file-collection
mkdir -p .tmp/tests/sar-file-collection
cd       .tmp/tests/sar-file-collection
export PYTHONPATH=~-/tests/mocks

# Check that mocking xen.lowlevel.xc works for this test
$PYTHON -c "from xen.lowlevel.xc import Error, xc;xc().domain_getinfo()"

# Run xen-bugtool --entries=xenserver-logs to capture the dummy SAR files
# and run the mocked sar command:
$PYTHON ~-/xen-bugtool -y --entries=xenserver-logs --output=tar --outfd=1 |
    tar xvf - --strip-components=1

# Show a detailed file list in the outlog log for human analysis in case of errors
find * -type f -print0 | xargs -0 ls -l

# Validate the results of collecting the mocked data:
grep -q '^sa$' var/log/sa/sa01
grep -q '^sr$' var/log/sa/sar31

# xen-bugtool is expected to call sar -A, and the symlink to echo captures it:
grep -q '^-A$' sar-A.out

# There is likely a xml tool to check the file names, in inventory.xml,
# but after verfiying the the files were included it should be sufficent
# check that they are also mentioned int the inventory.xml:
grep -q 'filename="bug-report-[0-9]*/var/log/sa/sa01"'  inventory.xml
grep -q 'filename="bug-report-[0-9]*/var/log/sa/sar31"' inventory.xml
grep -q 'filename="bug-report-[0-9]*/sar-A.out"'        inventory.xml

# Validate the extracted inventory.xml using the XML Schema
xmllint --schema ~-/tests/integration/inventory.xsd inventory.xml 2>stderr.out
cat stderr.out
