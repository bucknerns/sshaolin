from sshaolin.client import SSHClient

from tests.base_test import BaseTestCase


class TestLocalhost(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestLocalhost, cls).setUpClass()
        cls.client = SSHClient(
            "localhost", 22, cls.username, key_filename=cls.pkey_path)

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
