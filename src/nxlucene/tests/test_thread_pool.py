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
"""Testing the thread pool
"""

import time
import unittest
import nxlucene.threadpool

class ThreadPoolTestCase(unittest.TestCase):

    def setUp(self):
        self._pool = nxlucene.threadpool.ThreadPool(5)

    def test_instanciation(self):
        self.assertEqual(5, self._pool.getThreadCount())
        self.assertEqual(self._pool.getNextTask(), (None, None, None))

    def tearDown(self):
        self._pool.joinAll(False, False)
        time.sleep(0.1)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ThreadPoolTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
