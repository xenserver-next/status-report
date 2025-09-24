#!/bin/bash
# This test must run as root in a container(docker, podman, toolbox, apptainer, (s)chroot):
# Precondition: python with all dependencies from requirements.txt is installed
# WARNING: xen-bugtool needs to run run as user root in the container it runs in!
#
# exit on any error
set -o errexit
set -o pipefail
if [[ -n "$TRACE" ]]; then set -o xtrace; fi
set -o nounset
: ${PYTHON:=python3}

# Prepare test container: Mock the files used by this test
cp -a tests/integration/dom0-template/* /

# Enter a clean test environment
SRCDIR=$PWD
rm -rf   .tmp/tests/xenserver-config
mkdir -p .tmp/tests/xenserver-config
cd       .tmp/tests/xenserver-config
export PYTHONPATH=~-/tests/mocks

# Check that mocking xen.lowlevel.xc works for this test
$PYTHON -c "from xen.lowlevel.xc import Error, xc;xc().domain_getinfo()"

# Run xen-bugtool --entries=xenserver-logs to capture the dummy SAR files
# and run the mocked sar command:
tar_basename=tar
export XENRT_BUGTOOL_BASENAME=$tar_basename
$PYTHON ~-/xen-bugtool -y --entries=xenserver-config --output=tar --outfd=1 -s |
    tar xvf -

export XENRT_BUGTOOL_BASENAME=zip
$PYTHON ~-/xen-bugtool -y --entries=xenserver-config --output zip
unzip -o -d. /var/opt/xen/bug-report/zip.zip

# Validate the results of collecting the mocked data:

# At this point, {tar,zip}/etc/systemd shall not exist! Else, CP-45506 is not implemented correctly:
if test -e tar/etc/systemd -o -e zip/etc/systemd; then
    ls -lR */etc/systemd
    exit 5
fi

# tar/etc/systemd.tar and zip/etc/systemd.tar must be tarballs which we check further below:
tar xvf tar/etc/systemd.tar
tar xvf zip/etc/systemd.tar
rm {tar,zip}/etc/systemd.tar

cd $XENRT_BUGTOOL_BASENAME

# Show a detailed file list in the outlog log for human analysis in case of errors
find * -type f -print0 | xargs -0 ls -l

# Check that the files retrieved from etc/system.tar are identical to our original test files:
ls -l /etc/systemd/system/basic.target.wants/make-dummy-sr.service
diff -rNu ~/tests/integration/dom0-template/etc/ etc/

# Check filename entries in inventory.xml (in case a tool expects them):
SYSTEMD_SYSTEM_DIR=$XENRT_BUGTOOL_BASENAME/etc/systemd/system
grep -q \
    -e "filename=\"$SYSTEMD_SYSTEM_DIR.conf\"" \
    -e "filename=\"$SYSTEMD_SYSTEM_DIR/basic.target.wants/iptables.service\"" \
    -e "filename=\"$SYSTEMD_SYSTEM_DIR/basic.target.wants/make-dummy-sr.service\"" \
    inventory.xml

# Validate the extracted inventory.xml using the XML Schema
xmllint --schema $SRCDIR/tests/integration/inventory.xsd inventory.xml

cd -

# Check that the tar and zip outputs are identical (except for date and uptime):
sed -i "s/\\<$tar_basename\\>/$XENRT_BUGTOOL_BASENAME/" tar/inventory.xml
sed -i 's/date="[^"]*"//;s/uptime="[^"]*"//' {tar,zip}/inventory.xml
diff -rNu tar zip
