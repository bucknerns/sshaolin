from functools import wraps
import errno
import os
import signal
import getpass
import unittest

from sshaolin.client import SSHClient


class BaseTestCase(unittest.TestCase):
    username = getpass.getuser()

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        cls.client = SSHClient(
            "localhost", 22, cls.username, look_for_keys=True)


class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


# special test case for running ssh commands at module level
@timeout()
def import_ssh_test():
    from tests import ssh_run_ls_on_import
    ssh_run_ls_on_import


try:
    import_ssh_test()
    test_pass = True
except Exception:
    test_pass = False
