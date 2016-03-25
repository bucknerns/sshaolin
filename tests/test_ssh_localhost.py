import os
import unittest
import getpass
from sshaolin.client import SSHClient


class TestLocalhost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        auth_path = os.path.expanduser("~/.ssh/authorized_keys")
        pub_key_path = os.path.expanduser("~/.ssh/id_rsa.pub")
        auth_exists = os.path.exists(auth_path)
        pub_exists = os.path.exists(pub_key_path)
        if pub_exists:
            with open(pub_key_path) as fp:
                public_key = fp.read()
        if auth_exists:
            with open(auth_path) as fp:
                auth_file = fp.read()
            if pub_key_path not in auth_file:
                with open(auth_path, "a") as fp:
                    fp.write("\n")
                    fp.write(public_key)
                    fp.write("\n")
        cls.client = SSHClient(
            "localhost", 22, getpass.getuser(), look_for_keys=True,
            allow_agent=True)

    def test_arun_command(self):
        resp = self.client.execute_command("ls -l")
        self.assertTrue(
            resp.stdout, "No stdout, ls -l should return at least total 0")
        self.assertEqual(resp.exit_status, 0)
        self.assertFalse(resp.stderr)

    def test_bcreate_shell(self):
        shell = self.client.create_shell()
        resp = shell.execute_command("ls -l")
        resp2 = shell.execute_command("ls -la")
        self.assertTrue(
            resp.stdout, "No stdout, ls -l should return at least total 0")
        self.assertEqual(resp.exit_status, 0)
        self.assertFalse(resp.stderr)
        self.assertNotEqual(resp.stdout, resp2.stdout)
        shell.close()

    def test_create_sftp(self):
        sftp = self.client.create_sftp()
        resp = sftp.listdir("/")
        self.assertIsInstance(resp, list)
        self.assertTrue(resp, "root dir had no items this makes no sense")
        sftp.close()
