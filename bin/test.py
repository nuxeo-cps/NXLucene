#! /usr/bin/env python
##############################################################################
#
# Copyright (c) 2005 Nuxeo SAS <http://www.nuxeo.com>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
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
