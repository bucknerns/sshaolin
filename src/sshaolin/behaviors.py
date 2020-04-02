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

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption,
    BestAvailableEncryption)

from sshaolin.common import BaseSSHClass
from sshaolin.models import SSHKey


class SSHBehavior(BaseSSHClass):
    @classmethod
    def generate_ssh_keys(
        cls, size=4096, passphrase=None, private_format=PrivateFormat.PKCS8,
        public_format=PublicFormat.OpenSSH, private_encoding=Encoding.PEM,
            public_encoding=Encoding.OpenSSH):
        """Generates a public and private rsa ssh key

        Returns an SSHKeyResponse objects which has both the public and private
        key as attributes

        :param int size: RSA modulus length (must be a multiple of 256)
                             and >= 1024
        :param str passphrase: The pass phrase to derive the encryption key
                                from
        """
        encryption = (
            BestAvailableEncryption(passphrase) if passphrase else
            NoEncryption())
        key = rsa.generate_private_key(
            backend=default_backend(),
            public_exponent=65537,
            key_size=size)

        return SSHKey(
            public_key=key.public_key().public_bytes(
                public_encoding, public_format),
            private_key=key.private_bytes(
                Encoding.PEM, private_format, encryption))

    @classmethod
    def write_ssh_keys(
            cls, private_key, public_key=None, folder=None, key_name=None):
        """Writes secure keys to a local file

        :param str private_key: Private rsa ssh key string
        :param str public_key: Public rsa ssh key string
        :param str folder: Path to put the file(s)
        :param str key_name: Name of the private_key file, 'id_rsa' by default
        """
        folder = folder or "."
        key_name = key_name or "id_rsa"

        try:
            os.makedirs(folder)
        except OSError:
            pass

        key_path = os.path.join(folder, key_name)
        cls.write_file(key_path, private_key, 0o600)
        cls.write_file("{0}.pub".format(key_path), public_key, 0o664)

    @staticmethod
    def write_file(path, string=None, permissions=0o600):
        """Writes files with parameterized permissions

        :param str path: Path to write the file to
        :param str string: String to write into the file
        :param int permissions: Permissions to give the file
        """
        if string is None:
            return
        with open(path, "wb") as fp:
            fp.write(string or "")
        os.chmod(path, permissions)

    @classmethod
    def generate_and_write_files(
            cls, folder=None, key_name=None, **generate_ssh_keys_args):
        """Generate and write public and private rsa keys to local files

        :param str path: Path to put the file(s)
        :param str file_name: Name of the private_key file, 'id_rsa' by default
        :param int key_size: RSA modulus length (must be a multiple of 256)
                             and >= 1024
        :param str pass_phrase: The pass phrase to derive the encryption key
                                from
        """
        keys = cls.generate_ssh_keys(**generate_ssh_keys_args)
        cls.write_ssh_keys(
            private_key=keys.private_key, public_key=keys.public_key,
            folder=folder, key_name=key_name)
