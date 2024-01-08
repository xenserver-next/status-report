"""tests/unit/test_xapidb_filter.py: Ensure that the xen-bugtool.DBFilter() filters the XAPI DB properly"""
import os
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET


testdir = os.path.dirname(__file__)
original = r"""<?xml version="1.0" ?>
<root>
    <table name="secret">
        <row id="1">
            <value>mysecretpassword</value>
        </row>
        <row id="2">
            <value>anotherpassword</value>
        </row>
    </table>
    <table name="Cluster">
        <row id="1">
            <cluster_token>cluster_password</cluster_token>
        </row>
    </table>
    <table name="VM">
        <row id="1"
        NVRAM="(('EFI-variables'%.'myprivatedata'))"
        snapshot_metadata="('NVRAM'%.'(('_%.'_')%.(\'EFI-variables\'%.\'mydata\')()">
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
    for achild, bchild in zip(list(a), list(b)):
        assert_xml_element_trees_equiv(achild, bchild)


def test_xapi_database_filter(bugtool):
    """Assert that bugtool.DBFilter().output() filters the xAPI database as expected"""

    filtered = bugtool.DBFilter(original).output()

    # Works for Python2 equally, so we can use it to check against Python2/3 regressions:
    assert_xml_element_trees_equiv(ET.fromstring(filtered), ET.fromstring(expected))

    # Double-check with parseString(): Its output will differ between Py2/Py3
    # though, so we will use it for one language version at a time:
    if sys.version_info < (3, 0):  # pragma: no cover
        assert xml.dom.minidom.parseString(filtered).toprettyxml(indent="    ") == expected
