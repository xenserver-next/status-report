"""Mock xen.lowlevel.xc for testing the xen-bugtool python application"""
Error = None

class xc:
    def __init__(self):
        print("Mock xen.lowlevel.xc.xc() instantiated.")

    def domain_getinfo(self):
        print("Mock xen.lowlevel.xc.xc().domain_getinfo() called.")
        return []
