# Copyright 2020 Nathan Buckner
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

from setuptools import find_namespace_packages, setup

import versioneer

os.chdir(os.path.abspath(os.path.dirname(__file__)))

setup(
    name="sshaolin",
    version=versioneer.get_version(),
    description="SSH for Ninjas",
    long_description=open("README.md").read(),
    author="Nathan Buckner",
    author_email="bucknerns@gmail.com",
    url="https://github.com/bucknerns/sshaolin",
    install_requires=["paramiko", "pysocks"],
    packages=find_namespace_packages("src"),
    license=open("LICENSE").read(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: Other/Proprietary License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python"],
    package_dir={"": "src"},
    cmdclass=versioneer.get_cmdclass())
