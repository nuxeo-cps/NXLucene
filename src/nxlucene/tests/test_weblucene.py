# (C) Copyright 2006 Nuxeo SARL <http://nuxeo.com>
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
"""Test txn managers

$Id: test_txn_managers.py 30575 2005-12-13 16:15:42Z janguenot $
"""

import unittest
from zope.testing.doctest import DocFileTest

def test_suite():
    return unittest.TestSuite((
        DocFileTest('README.txt', package="nxlucene"),
        ))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
