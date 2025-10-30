#!/bin/bash
# This test is expected to be run as root in a container(docker, podman, toolbox, apptainer, (s)chroot):
# Precondition: python with all dependencies from requirements.txt is installed
# WARNING: This is running as user root in the container it runs in!
#
# exit on any error
set -o errexit
set -o pipefail
if [[ -n "$TRACE" ]]; then set -o xtrace; fi
set -o nounset
SRC=$PWD
: ${PYTHON:=python3}

# The bugtool capability this test is testing:
CAP=system-load

# Test object: A dummy sar files (Unix system activity reporter from the sysstat pkg)
# and the output of a fake `sar -A` command. URL: https://github.com/sysstat/sysstat

# Prepare test container: Mock the files used by this test
cp -a tests/integration/dom0-template/* /
mkdir -p  /var/log/sa
echo sa  >/var/log/sa/sa01
echo sr  >/var/log/sa/sar31
echo -e '#!/bin/sh\nsleep 2;find xen-bugtool tests/ -type f|xargs cat;echo $*' >/bin/sar
chmod +x /bin/sar

# Enter a clean test environment
rm -rf   .tmp/tests/sar-file-collection
mkdir -p .tmp/tests/sar-file-collection
cd       .tmp/tests/sar-file-collection
export PYTHONPATH=~-/tests/mocks

# Check that mocking xen.lowlevel.xc works for this test
$PYTHON -c "from xen.lowlevel.xc import Error, xc;xc().domain_getinfo()"

# Run xen-bugtool --entries=$CAP to test tar output (to a file descriptor in this case)
tar_basename=tar
export XENRT_BUGTOOL_BASENAME=$tar_basename
# Test creating a tar archive on a file descriptor using --output=tar --outfd=fd
$PYTHON ~-/xen-bugtool -y --entries=$CAP --output=tar --outfd=2 2>tar.bz2
tar xvf tar.bz2

# Run xen-bugtool --entries=$CAP --output=zip to test zip output (output to file only)
zip_basename=zip
export XENRT_BUGTOOL_BASENAME=$zip_basename
$PYTHON ~-/xen-bugtool -y --entries=$CAP --output=zip
unzip -o -d. /var/opt/xen/bug-report/zip.zip

pushd $zip_basename

# Show a detailed file list in the outlog log for human analysis in case of errors
find * -type f -print0 | xargs -0 ls -l

# Validate the results of collecting the mocked data:
grep -q '^sa$' var/log/sa/sa01
grep -q '^sr$' var/log/sa/sar31

# bugtool call sar -A, printing dummy data and the arguments it was given. Check that:
tail -1 sar-A.out | grep -q '^-A$'

# There is likely a xml tool to check the file names, in inventory.xml,
# but after verfiying the the files were included it should be sufficent
# check that they are also mentioned int the inventory.xml:
grep -q 'filename=".*/var/log/sa/sa01"'  inventory.xml
grep -q 'filename=".*/var/log/sa/sar31"' inventory.xml
grep -q 'filename=".*/sar-A.out"'        inventory.xml

# Validate the extracted inventory.xml using the XML Schema
xmllint --schema $SRC/tests/integration/inventory.xsd inventory.xml
popd

# Check that the tar and zip outputs are identical (except for date and uptime):
sed -i "s/\\<$tar_basename\\>/$zip_basename/" tar/inventory.xml
sed -i 's/date="[^"]*"//;s/uptime="[^"]*"//' {tar,zip}/inventory.xml
diff -rNu tar zip
