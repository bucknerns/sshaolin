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
import functools
import logging
import time

from sshaolin.models import CommandResponse
CHANNEL_KEEPALIVE = 45
DEFAULT_TIMEOUT = 60
POLLING_RATE = 0.01

logging_formatter = logging.Formatter(
    fmt="%(asctime)s: %(levelname)s: %(name)s: %(message)s")


def SSHLogger(func):
    DASH_WIDTH = 42

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        message = (
            "\n{equals}\nCALL\n{dash}\n"
            "{name} args..........: {args}\n"
            "{name} kwargs........: {kwargs}\n"
            "{dash}\n").format(
            dash="-" * DASH_WIDTH, equals="=" * DASH_WIDTH, name=func.__name__,
            args=args, kwargs=kwargs)
        if self.log_calls:
            self._log.info(message)

        start = time.time()
        try:
            resp = func(self, *args, **kwargs)
        except Exception as e:
            self._log.critical(e)
            raise

        elapsed = time.time() - start
        if isinstance(resp, CommandResponse):
            message = (
                "\n{equals}\nRESPONSE\n{dash}\n"
                "response stdout......: {stdout}\n"
                "response stderr......: {stderr}\n"
                "response exit_status.: {exit_status}\n"
                "response elapsed.....: {elapsed}\n"
                "{dash}\n").format(
                dash="-" * 42, equals="=" * 42, elapsed=elapsed,
                stdout=resp.stdout.decode("UTF-8", "ignore"),
                stderr=resp.stderr.decode("UTF-8", "ignore"),
                exit_status=resp.exit_status)
            if self.log_responses:
                self._log.info(message)
        return resp
    return wrapper


class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()


def classproperty(func):
    """Creates a property that can be accessed by a classmethod allowing for
    logging in classmethods"""
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)
    return ClassPropertyDescriptor(func)


class BaseSSHClass(object):
    @classproperty
    def _log(cls):
        # creates a separate logger for each class that are children of the
        return logging.getLogger(cls._dotpath)

    @classproperty
    def _dotpath(cls):
        string = str(cls.__mro__[0])
        string = string.split("'", 1)[-1]  # remove anything before first quote
        string = string.split("'", 1)[0]  # remove anything after first quote
        string = string.split()[0]  # remove anything after first whitespace
        string = string.replace("<", "")  # remove <
        return string

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if hasattr(self, "close"):
            self.close()

    def __del__(self):
        if hasattr(self, "close"):
            self.close()
