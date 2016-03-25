from os import path
from uuid import uuid4
import getpass
import sys
import unittest

from sshaolin.behaviors import SSHBehavior


class BaseTestCase(unittest.TestCase):
    username = getpass.getuser()

    @classmethod
    def setUpClass(cls):
        cls.storage_folder = path.join(path.expanduser("~"), ".ssh")
        cls.rand_name = uuid4().hex
        try:
            keys = SSHBehavior.generate_ssh_keys()
        except TypeError as e:
            message = """Tests skipped because key generation failed
                Probably due to pycrypto bug
                https://github.com/dlitz/pycrypto/issues/99
                {0}\n""".format(e)
            sys.stdout.write(message)
            raise unittest.SkipTest(message)
        keys.public_key = "{0} {1}".format(
            keys.public_key, cls.rand_name)
        SSHBehavior.write_ssh_keys(
            private_key=keys.private_key, public_key=keys.public_key,
            folder=cls.storage_folder, key_name=cls.rand_name)
        cls.auth_path = path.join(cls.storage_folder, "authorized_keys")
        cls.pkey_path = path.join(cls.storage_folder, cls.rand_name)
        with open(cls.auth_path, "a") as fp:
            fp.write("\n")
            fp.write(keys.public_key)
            fp.write("\n")

    @classmethod
    def tearDownClass(cls):
        with open(cls.auth_path) as fp:
            public_keys = [
                line for line in fp if line and cls.rand_name not in line]
        with open(cls.auth_path, "w") as fp:
            fp.write("".join(public_keys))
