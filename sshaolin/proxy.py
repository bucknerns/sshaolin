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
import os
import signal
import subprocess

from sshaolin.common import BaseSSHClass


class SSHProxy(BaseSSHClass):
    def __init__(
        self, hostname=None, port=22, username=None, compress=True,
            look_for_keys=False, key_filename=None):
        super(SSHProxy, self).__init__()
        self.hostname = hostname
        self.port = port
        self.username = username
        self.compress = compress
        self.look_for_keys = look_for_keys
        self.key_filename = key_filename

    def _get_args(
        self, hostname=None, port=None, username=None, compress=None,
            look_for_keys=None, key_filename=None):
        args = [
            "ssh", "-oUserKnownHostsFile=/dev/null",
            "-oStrictHostKeyChecking=no", "-oExitOnForwardFailure=yes", "-N"]
        hostname = hostname or self.hostname
        username = username or self.username
        compress = compress if compress is not None else self.compress
        key_filename = key_filename or self.key_filename
        look_for_keys = (
            look_for_keys if look_for_keys is not None
            else self.look_for_keys)

        args.append("-P{0}".format(port or self.port))
        if compress:
            args.append("-C")

        if look_for_keys is False:
            args.append("-i{0}".format(key_filename))

        if username:
            args.append("{0}@{1}".format(username, hostname))
        else:
            args.append(hostname)
        return args

    def create_forward_port(
        self, port, forward_address, forward_port, address=None,
            remote=False, **connect_kwargs):
        """
        Warning: This can be a security issue for long running tunnels because
        bind_address does not work like ssh, instead it default to binding
        on every interface.  SSH defaults to binding to localhost.
        """
        args = self._get_args(**connect_kwargs)
        remote_flag = "R" if remote else "L"
        args.append("-{0}{1}:{2}:{3}:{4}".format(
            remote_flag, address or "0.0.0.0", port,
            forward_address, forward_port))
        hostname = connect_kwargs.get("hostname", self.hostname)
        address = address or hostname if remote else "localhost"
        proc = subprocess.Popen(args, preexec_fn=os.setsid)
        return PortForward(proc.pid, address, port)

    def create_socks_proxy(self, port, address=None, **connect_kwargs):
        args = self._get_args(**connect_kwargs)
        args.append("-D{0}:{1}".format(address or "0.0.0.0", port))
        proc = subprocess.Popen(args, preexec_fn=os.setsid)
        return SocksProxy(proc.pid, port or "localhost", address)


class PortForward(BaseSSHClass):
    TYPE = "PORT_FORWARD"

    def __init__(self, pid, address, port, name=None):
        self.pid = pid
        self.address = address
        self.port = port
        self.name = name

    def set_name(self, name):
        self.name = name

    def close(self):
        try:
            os.kill(self.pid, signal.SIGKILL)
        except OSError:
            pass


class SocksProxy(PortForward):
    TYPE = "SOCKS"
    pass
