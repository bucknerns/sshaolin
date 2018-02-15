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
import six


class BaseModel(object):
    def __eq__(self, obj):
        try:
            if type(obj) == type(self) and vars(obj) == vars(self):
                return True
        except Exception:
            pass
        return False

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        string = "<{0} object>\n".format(type(self).__name__)
        for key in list(vars(self).keys()):
            val = getattr(self, key)
            if isinstance(val, six.text_type):
                string += "{0} = {1}\n".format(key, val.encode("utf-8"))
            else:
                string += "{0} = {1}\n".format(key, val)
        return string

    def __repr__(self):
        return str(self)


class CommandResponse(BaseModel):
    def __init__(
            self, stdin=None, stdout=None, stderr=None, exit_status=None):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.exit_status = exit_status


class SSHKey(BaseModel):
    def __init__(self, public_key=None, private_key=None):
        self.public_key = public_key
        self.private_key = private_key
