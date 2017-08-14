from sshaolin.client import CommandOperationTimeOut
from tests.base_test import BaseTestCase, test_pass


class TestLocalhost(BaseTestCase):
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

    def test_command_timeout(self):
        timeout = 1
        command = 'sleep 300'

        shell = self.client.create_shell(timeout=timeout)
        with self.assertRaises(CommandOperationTimeOut) as exc_timeout:
            shell.execute_command(command)

            self.assertEqual(exc_timeout.timeout, timeout)
            self.assertEqual(exc_timeout.command, command)

    def test_create_sftp(self):
        sftp = self.client.create_sftp()
        resp = sftp.listdir("/")
        self.assertIsInstance(resp, list)
        self.assertTrue(resp, "root dir had no items this makes no sense")
        sftp.close()

    def test_run_at_import(self):
        self.assertTrue(test_pass, "did not execute at module level")
