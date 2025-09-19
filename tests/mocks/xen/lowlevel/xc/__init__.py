"""Mock xen.lowlevel.xc for testing the xen-bugtool python application"""

Error = None


class xc:
    """Mock xc class as a stand-in for the real xen.lowlevel.xc which only works in a real Xen Dom0"""

    def __init__(self):
        """Mock for the constructor of xen.lowlevel.xc.xc() constructor"""

    def domain_getinfo(self):
        """Mock for xen.lowlevel.xc.xc().domain_getinfo()"""
        return []
