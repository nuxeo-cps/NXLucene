#! /usr/bin/env python
# Copyright (C) 2006, Nuxeo SAS <http://www.nuxeo.com>
# Author: Julien Anguenot <ja@nuxeo.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-13
"""Test runner for WebLucene.

See the docs for zope.testing; test.py is a small driver for
zope.testing.testrunner.
"""

import sys

path = "src"
pylucene_path = "src/PyLucene/python"
print "Running tests from", path

# Insert the WebLucene src dir first in the sys.path to avoid a name conflict
# with zope.whatever librairies that might be installed on the Python
# version used to launch these tests.
sys.path.insert(0, path)
sys.path.append(pylucene_path)

from zope.testing import testrunner

defaults = [
    "--path", path,
    ]

testrunner.run(defaults)
