# Copyright 2016 Nathan Buckner
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from io import BytesIO
from socks import socket, create_connection
from types import MethodType
from uuid import uuid4
import threading
import time

from paramiko import AutoAddPolicy, RSAKey
from paramiko.client import SSHClient as ParamikoSSHClient
from paramiko import py3compat

from sshaolin import common
from sshaolin.models import CommandResponse

# this is a hack to preimport dependencies imported in a thread during connect
# which causes a deadlock. https://github.com/paramiko/paramiko/issues/104
py3compat.u("".encode())

# dirty hack 2.0 also issue 104
# Try / Catch to prevent users using paramiko<2.0.0 from raising an ImportError
try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.utils import int_from_bytes
    int_from_bytes(b"a", "big")
    default_backend()
except ImportError:
    pass


class CommandOperationTimeOut(socket.timeout):
    pass


class ProxyTypes(object):
    SOCKS5 = 2
    SOCKS4 = 1


def read_pipe(pipe, fp_out):
    def target():
        for line in iter(pipe.readline, b""):
            fp_out.write(line)
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    return thread


class ExtendedParamikoSSHClient(ParamikoSSHClient):
    def execute_command(
        self, command, bufsize=-1, timeout=None,
            stdin_str="", stdin_file=None, raise_exceptions=False):
        chan = self._transport.open_session()
        chan.settimeout(timeout)
        start = time.time()
        chan.exec_command(command)
        stdin_str = stdin_str if stdin_file is None else stdin_file.read()
        stdin = chan.makefile("wb", bufsize)
        stdout = chan.makefile("rb", bufsize)
        stderr = chan.makefile_stderr("rb", bufsize)
        stdin.write(stdin_str)
        stdin.write("\n\x04")
        stdin.close()
        exit_status = None
        stdout_bytes = BytesIO()
        stderr_bytes = BytesIO()
        out_thread = read_pipe(stdout, stdout_bytes)
        err_thread = read_pipe(stderr, stderr_bytes)
        out_thread.join(timeout)
        err_thread.join(timeout)
        if timeout and (time.time() - start) > timeout:
            raise CommandOperationTimeOut("Command timed out")
        for i in range(2):
            if chan.exit_status_ready():
                break
        exit_status = chan.recv_exit_status()
        chan.close()
        return (
            stdin_str, stdout_bytes.getvalue(), stderr_bytes.getvalue(),
            exit_status)


class SSHClient(common.BaseSSHClass):
    def __init__(
        self, hostname=None, port=22, username=None, password=None,
        accept_missing_host_key=True, timeout=common.DEFAULT_TIMEOUT,
        compress=True, pkey=None, look_for_keys=False, allow_agent=False,
        key_filename=None, proxy_type=None, proxy_ip=None, proxy_port=None,
            sock=None):
        super(SSHClient, self).__init__()
        self.connect_kwargs = {}
        self.accept_missing_host_key = accept_missing_host_key
        self.proxy_port = proxy_port
        self.proxy_ip = proxy_ip
        self.proxy_type = proxy_type
        self.connect_kwargs["timeout"] = timeout
        self.connect_kwargs["hostname"] = hostname
        self.connect_kwargs["port"] = int(port)
        self.connect_kwargs["username"] = username
        self.connect_kwargs["password"] = password
        self.connect_kwargs["compress"] = compress
        self.connect_kwargs["pkey"] = pkey
        self.connect_kwargs["look_for_keys"] = look_for_keys
        self.connect_kwargs["allow_agent"] = allow_agent
        self.connect_kwargs["key_filename"] = key_filename
        self.connect_kwargs["sock"] = sock

    @property
    def timeout(self):
        return self.connect_kwargs.get("timeout")

    @timeout.setter
    def timeout(self, value):
        self.connect_kwargs["timeout"] = value

    @timeout.deleter
    def timeout(self):
        if "timeout" in self.connect_kwargs:
            del self.connect_kwargs["timeout"]

    def _connect(
        self, hostname=None, port=None, username=None, password=None,
        accept_missing_host_key=None, timeout=None, compress=None, pkey=None,
        look_for_keys=None, allow_agent=None, key_filename=None,
            proxy_type=None, proxy_ip=None, proxy_port=None, sock=None):
        connect_kwargs = dict(self.connect_kwargs)
        connect_kwargs.update({
            k: locals().get(k) for k in self.connect_kwargs
            if locals().get(k) is not None})
        connect_kwargs["port"] = int(connect_kwargs.get("port"))

        ssh = ExtendedParamikoSSHClient()

        if bool(self.accept_missing_host_key or accept_missing_host_key):
            ssh.set_missing_host_key_policy(AutoAddPolicy())

        if connect_kwargs.get("pkey") is not None:
            connect_kwargs["pkey"] = RSAKey.from_private_key(
                BytesIO(connect_kwargs["pkey"]))

        proxy_type = proxy_type or self.proxy_type
        proxy_ip = proxy_ip or self.proxy_ip
        proxy_port = proxy_port or self.proxy_port
        if connect_kwargs.get("sock") is not None:
            pass
        elif all([proxy_type, proxy_ip, proxy_port]):
            connect_kwargs["sock"] = create_connection(
                (connect_kwargs.get("hostname"), connect_kwargs.get("port")),
                proxy_type, proxy_ip, int(proxy_port))

        ssh.connect(**connect_kwargs)
        return ssh

    @common.SSHLogger
    def execute_command(
        self, command, bufsize=-1, stdin_str=b"", stdin_file=None,
            **connect_kwargs):
        ssh_client = self._connect(**connect_kwargs)
        stdin, stdout, stderr, exit_status = ssh_client.execute_command(
            timeout=connect_kwargs.get("timeout", self.timeout),
            command=command, bufsize=bufsize, stdin_str=stdin_str,
            stdin_file=stdin_file)
        ssh_client.close()
        del ssh_client
        return CommandResponse(
            stdin=stdin, stdout=stdout, stderr=stderr, exit_status=exit_status)

    @common.SSHLogger
    def create_shell(self, keepalive=None, **connect_kwargs):
        connection = self._connect(**connect_kwargs)
        return SSHShell(
            connection, connect_kwargs.get("timeout", self.timeout),
            keepalive)

    @common.SSHLogger
    def create_sftp(self, keepalive=None, **connect_kwargs):
        connection = self._connect(**connect_kwargs)
        return SFTPShell(connection, keepalive)


class SFTPShell(common.BaseSSHClass):
    def __init__(self, connection=None, keepalive=None):
        super(SFTPShell, self).__init__()
        self.connection = connection
        self.sftp = connection.open_sftp()
        self.sftp.get_channel().get_transport().set_keepalive(
            keepalive or common.CHANNEL_KEEPALIVE)
        self._setup_sftp_funcs()
        self.chdir(".")

    def _setup_sftp_funcs(self):
        def get_func(name):
            func = getattr(self.sftp, func_name)

            def wrapper(self, *args, **kwargs):
                return func(*args, **kwargs)
            wrapper.__name__ = func_name
            wrapper.__doc__ = func.__doc__
            return common.SSHLogger(wrapper)

        for func_name in [
            "chdir", "chmod", "chown", "file", "get", "getcwd", "getfo",
            "listdir", "listdir_attr", "listdir_iter", "lstat", "mkdir",
            "normalize", "open", "put", "putfo", "readlink", "remove",
            "rename", "rmdir", "stat", "symlink", "truncate", "unlink",
                "utime"]:
            func = get_func(func_name)
            setattr(self, func_name, MethodType(func, self))

    def exists(self, path):
        ret_val = False
        try:
            self.stat(path)
            ret_val = True
        except IOError as e:
            if e[0] != 2:
                raise
            ret_val = False
        return ret_val

    def get_file(self, remote_path):
        ret_val = BytesIO()
        self.getfo(remote_path, ret_val)
        return ret_val.getvalue()

    def write_file(self, data, remote_path):
        return self.putfo(BytesIO(data), remote_path)

    def close(self):
        if hasattr(self, "sftp"):
            self.sftp.close()
            del self.sftp
        if hasattr(self, "connection"):
            self.connection.close()
            del self.connection


class SSHShell(common.BaseSSHClass):
    RAISE = "RAISE"
    RAISE_DISCONNECT = "RAISE_DISCONNECT"

    def __init__(self, connection, timeout, keepalive=None):
        super(SSHShell, self).__init__()
        self.connection = connection
        self.timeout = timeout
        self.channel = self._create_channel()
        self.channel.settimeout(common.POLLING_RATE)
        self._clear_channel()
        self.channel.get_transport().set_keepalive(
            keepalive or common.CHANNEL_KEEPALIVE)

    def close(self):
        if hasattr(self, "channel"):
            self.channel.close()
            del self.channel
        if hasattr(self, "connection"):
            self.connection.close()
            del self.connection

    @common.SSHLogger
    def execute_command(
        self, cmd, timeout_action=RAISE_DISCONNECT,
            exception_on_timeout=True, **kwargs):
        max_time = time.time() + kwargs.get("timeout", self.timeout)
        uuid = uuid4().hex.encode()
        cmd = "echo {1}\n{0}\necho {1} $?\n".format(cmd.strip(), uuid).encode()
        try:
            self._clear_channel()
            self._wait_for_active_shell(max_time)
            self.channel.send(cmd)
            response = self._read_shell_response(uuid, max_time)
        except socket.timeout:
            if timeout_action == self.RAISE_DISCONNECT:
                self.close()
            raise
        return response

    def _create_channel(self):
        chan = self.connection._transport.open_session()
        chan.invoke_shell()
        return chan

    def _wait_for_active_shell(self, max_time):
        while not self.channel.send_ready():
            time.sleep(common.POLLING_RATE)
            if max_time < time.time():
                raise socket.timeout("Timed out waiting for active shell")

    def _read_shell_response(self, uuid, max_time):
        stdout = stderr = b""
        exit_status = None
        while max_time > time.time():
            stdout += self._read_channel(self.channel.recv)
            stderr += self._read_channel(self.channel.recv_stderr)
            if stdout.count(uuid) == 2:
                list_ = stdout.split(uuid)
                stdout = list_[1]
                try:
                    exit_status = int(list_[2])
                except (ValueError, TypeError):
                    exit_status = None
                break
        else:
            raise CommandOperationTimeOut("Command timed out")
        response = CommandResponse(
            stdin=None, stdout=stdout.strip(), stderr=stderr.strip(),
            exit_status=exit_status)
        return response

    def _read_channel(self, read_func, buffsize=1024):
        read = b""
        try:
            read += read_func(buffsize)
        except socket.timeout:
            pass
        return read

    def _clear_channel(self):
        self._read_channel(self.channel.recv)
        self._read_channel(self.channel.recv_stderr)
