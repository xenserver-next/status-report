"""namespace_container.py: Functions for creating a test environment container on any Linux and GitHub CI"""
import ctypes
import os


CLONE_NEWUSER = 0x10000000
CLONE_NEWNET = 0x40000000
CLONE_NEWNS = 0x00020000
MS_BIND = 4096
MS_REC = 16384
MS_PRIVATE = 1 << 18


def unshare(flags):
    """Wrapper for the Linux libc/system call to unshare Linux kernel namespaces"""
    libc = ctypes.CDLL(None, use_errno=True)
    libc.unshare.argtypes = [ctypes.c_int]
    rc = libc.unshare(flags)
    if rc != 0:  # pragma: no cover
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno), flags)


def mount(source="none", target="", fs="", flags=0, options=""):
    """Wrapper for the Linux libc/system call to mount an fs, supports Python2.7 and Python3.x"""
    libc = ctypes.CDLL(None, use_errno=True)
    libc.mount.argtypes = (
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_ulong,
        ctypes.c_char_p,
    )
    print("mount -t " + fs + " -o '" + options + "' " + source + "\t" + target)
    result = libc.mount(source.encode(), target.encode(), fs.encode(), flags, options.encode())
    if result < 0:  # pragma: no cover
        errno = ctypes.get_errno()
        raise OSError(errno, "mount " + target + " (options=" + options + "): " + os.strerror(errno))


def umount(target):
    """Wrapper for the Linux umount system call, supports Python2.7 and Python3.x"""
    libc = ctypes.CDLL(None, use_errno=True)
    result = libc.umount(ctypes.c_char_p(target.encode()))
    if result < 0:  # pragma: no cover
        errno = ctypes.get_errno()
        raise OSError(errno, "umount " + target + ": " + os.strerror(errno))


def activate_private_test_namespace(bindmount_root, bindmount_mountpoints):
    """Activate a new private mount, network and user namespace with the user behaving like uid 0 (root)

    xen-bugtool requires to be run as root and checks it and writes its output to /var/opt/xen/bug-report.
    The container setup provides these root privileges and a new mount namespace to bind-mount the test files.
    It allows to bind-mount the directory trees with test files at the places where xen-bugtool collects them.
    The mount namespace also allows to create a tmpfs mount at /var/opt/xen/bug-report for the output data.
    It avoids the need to create a temporary directory and to bind-mount it into the container.
    Additionally, it ensures that no temporary data can accumulate on the host.

    This function implements the equivalent of `/usr/bin/unshare --map-root-user --mount --net`
    and mounts the passed bindmount_mountpoints below bindmount_root:

    - --map-root-user: Create a user namespace where euid/egid are mapped to the superuser UID and GID.
    - --mount: Create a Linux mount namespace for mounting temporary file systems and bind-mounting test data.
    - --net: Create a Linux network namespace to ensure that `bugtool` works without outside connectivity.
    """
    # Implements the sequence that `unshare -rmn <command>` uses. Namespace is active even without fork():
    real_uid = os.getuid()
    real_gid = os.getgid()
    unshare(CLONE_NEWUSER | CLONE_NEWNET | CLONE_NEWNS)
    # Setup uidmap for the user's uid to behave like uid 0 would (eg for bugtool's root user check)
    with open("/proc/self/uid_map", "wb") as proc_self_uidmap:
        proc_self_uidmap.write(b"0 %d 1" % real_uid)
    # Setup setgroups behave like gid 0 would (needed for new tmpfs mounts for test output files):
    with open("/proc/self/setgroups", "wb") as proc_self_setgroups:
        proc_self_setgroups.write(b"deny")
    # Setup gidmap for the user's gid to behave like gid 0 would (needed for tmpfs mounts):
    with open("/proc/self/gid_map", "wb") as proc_self_gidmap:
        proc_self_gidmap.write(b"0 %d 1" % real_gid)
    # Prepare a private root mount in the new mount namespace, needed for mounting a private tmpfs on /var:
    mount(target="/", flags=MS_REC | MS_PRIVATE)
    # Bind-mount the Dom0 template directories in the private mount namespace to provide the test files:
    for mountpoint in bindmount_mountpoints:
        if not os.path.exists(mountpoint):
            raise RuntimeError("Mountpoint missing on host! Please run: sudo mkdir " + mountpoint)
        mount(source=bindmount_root + mountpoint, target=mountpoint, flags=MS_BIND)
