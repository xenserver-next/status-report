"""tests/unit/test_xapidb_filter.py: Ensure that the xen-bugtool.DBFilter() filters the XAPI DB properly"""
import os
import sys
from xml.dom.minidom import parseString
from xml.etree.ElementTree import fromstring

import pytest

testdir = os.path.dirname(__file__)
original = r"""<?xml version="1.0" ?>
<root>
    <table name="secret">
        <row id="1">
            <value>secret password</value>
        </row>
        <row id="2">
            <value>another password</value>
        </row>
    </table>
    <table name="Cluster">
        <row id="1">
            <cluster_token>cluster_password</cluster_token>
        </row>
    </table>
    <table name="VM">
        <row id="1"
        NVRAM="(('EFI-variables'%.'private data'))"
        snapshot_metadata="('NVRAM'%.'(('_%.'_')%.(\'EFI-variables\'%.\'data\')()">
        </row>
    </table>
</root>
"""

# Same as original, but with passwords and private data replaced by: "REMOVED"
expected = r"""<?xml version="1.0" ?>
<root>
    <table name="secret">
        <row id="1" value="REMOVED">
            <value/>
        </row>
        <row id="2" value="REMOVED">
            <value/>
        </row>
    </table>
    <table name="Cluster">
        <row cluster_token="REMOVED" id="1">
            <cluster_token/>
        </row>
    </table>
    <table name="VM">
        <row NVRAM="(('EFI-variables'%.'REMOVED'))" id="1" snapshot_metadata="('NVRAM'%.'(('_%.'_')%.(\'EFI-variables\'%.\'REMOVED\')()"/>
    </table>
</root>
"""


def assert_xml_element_trees_equiv(a, b):
    """Assert that the contents of two XML ElementTrees are equivalent (recursive)"""
    # Check the XML tag
    assert a.tag == b.tag
    # Check the XML text
    assert (a.text or "").strip() == (b.text or "").strip()
    # Check the XML tail
    assert (a.tail or "").strip() == (b.tail or "").strip()
    # Check the XML attributes
    assert a.attrib.items() == b.attrib.items()
    # Compare the number of child nodes
    assert len(list(a)) == len(list(b))
    # Recursively repeat for all child nodes (expect same order of child nodes):
    for child_a, child_b in zip(list(a), list(b)):
        assert_xml_element_trees_equiv(child_a, child_b)


def assert_xml_str_equiv(filtered, expected):
    """Assert that the given dummy Xen-API database to filtered as expected"""

    # Works for Python2 equally, so we can use it to check Python2/3 to work.:
    assert_xml_element_trees_equiv(fromstring(filtered), fromstring(expected))

    # Double-check with parseString(): Its output will differ between Py2/Py3
    # though, so we will use it for one language version at a time:
    if sys.version_info < (3, 0):  # pragma: no cover
        assert parseString(filtered).toprettyxml(indent="    ") == expected


def test_xapi_database_filter(bugtool):
    """Assert bugtool.DBFilter().output() filters xAPI database like expected"""

    filtered = bugtool.DBFilter(original).output()
    assert_xml_str_equiv(filtered, expected)


def test_filter_xenstore_secrets(bugtool):
    """Assert that filter_xenstore_secrets() does not filter non-secrets"""

    assert bugtool.filter_xenstore_secrets(b"not secret", "_") == b"not secret"


def test_dump_filtered_xapi_db(bugtool, fs):
    """
    Assert that bugtool.dump_filtered_xapi_db() filters the XAPI DB as expected
    using a fake filesystem (pyfakefs) to avoid touching the real filesystem
    and without requiring root privileges.
    """

    # Prepare the test using the fs fixture of pyfakefs:
    fs.create_file(bugtool.DB_CONF, contents="[/xapi.db]\n")
    fs.create_file("/xapi.db", contents=original)

    # Act:
    filtered = bugtool.dump_filtered_xapi_db("mock")

    # Assert:
    assert_xml_str_equiv(filtered, expected)


def test_xapi_db_no_conf(bugtool):
    """Test bugtool.dump_filtered_xapi_db() when the DB_CONF file is missing"""

    # Prepare: Ensure the DB_CONF file does not exist:
    saved_conf = bugtool.DB_CONF
    bugtool.DB_CONF = "/non/existent/file"

    # Act:
    with pytest.raises(IOError) as exc_info:
        bugtool.dump_filtered_xapi_db("mock")

    # Assert (bugtool catches it and logs it, tested in another test):
    assert "No such file or directory" in str(exc_info.value)
    assert str(exc_info.value).endswith(bugtool.DB_CONF + "'")

    # Cleanup:
    bugtool.DB_CONF = saved_conf


def test_xapi_db_no_db_file(bugtool, fs):
    """Test bugtool.dump_filtered_xapi_db() when the xapi db file is missing"""

    # Prepare the test using the fs fixture of pyfakefs:
    fs.create_file(bugtool.DB_CONF, contents="[/nonexistent-xapi.db]\n")

    # Act:
    data = bugtool.dump_filtered_xapi_db("mock")

    # Assert: No data returned
    assert data == ""
