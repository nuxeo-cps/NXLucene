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
"""Testing the store backckened registry

$Id$
"""

import os
import shutil
import PyLucene
import unittest

import zope.interface
from zope.interface.verify import verifyClass
from zope.interface.exceptions import DoesNotImplement

from nxlucene.store.pythondirectory import PythonFileDirectory

from nxlucene.server.store.interfaces import IStoreBackened
from nxlucene.server.store.backeneds import FSDirectoryBackened
from nxlucene.server.store.backeneds import BdbDirectoryBackened
from nxlucene.server.store.backeneds import PythonDirectoryBackened
from nxlucene.server.store.backeneds import RamDirectoryBackened

from nxlucene.server.store.registry import getRegistry

class TestStoreBackenedTestCase(unittest.TestCase):

    def setUp(self):
        self._registry = getRegistry()
        self._store_dir = '/tmp/lucene'

    def test_implementation(self):
        verifyClass(IStoreBackened, FSDirectoryBackened)
        verifyClass(IStoreBackened, BdbDirectoryBackened)
        verifyClass(IStoreBackened, RamDirectoryBackened)
        verifyClass(IStoreBackened, PythonDirectoryBackened)

    def test_initialization(self):
        expected = (('FSDirectory', FSDirectoryBackened),
                    ('PythonDirectory', PythonDirectoryBackened),
                    ('RamDirectory', RamDirectoryBackened),
                    ('BdbDirectory', BdbDirectoryBackened),
                    )

        expected_names = ['bdbdirectory', 'fsdirectory', 'pythondirectory',
                          'ramdirectory']
        self.assertEqual(expected_names, list(self._registry.listNames()))
        for name, klass in expected:
            self.assertEqual(self._registry.getClass(name), klass)

    def test_register(self):

        initial_num = len(self._registry.listNames())

        name ="foo"

        class FooKlass(object):
            def __init__(self, *args, **kw):
                self.kwargs = kw

        class FooBackened(object):
            zope.interface.implements(IStoreBackened)
            def get(self, *args, **kw):
                return FooKlass(*args, **kw)

        self._registry.register(name, FooBackened)
        self.assert_(name in self._registry.listNames())
        self.assertEqual(FooBackened, self._registry.getClass(name))
        self.assert_(isinstance(self._registry.makeInstance(name), FooKlass))

        self.assertEqual(1, len(self._registry.listNames()) - initial_num)

        # Try to register once again. not taken into account
        self._registry.register(name, FooBackened)
        self.assertEqual(1, len(self._registry.listNames()) - initial_num)

    def test_wrong_registration(self):

        name = "foo"

        class FooBackened(object):
            zope.interface.implements(zope.interface.Interface)
            def get(self, **kw):
                pass

        self.assertRaises(DoesNotImplement, self._registry.register,
                          name, FooBackened)


    def test_fsdirectory(self):
        self.assertEqual(self._registry.getClass('FSDirectory'),
                         FSDirectoryBackened)

        self.assert_(isinstance(self._registry.makeInstance('FSDirectory',
                                                        self._store_dir, True),
                         PyLucene.FSDirectory))

    def test_pythondirectory(self):
        self.assertEqual(self._registry.getClass('PythonDirectory'),
                         PythonDirectoryBackened)

        self.assert_(isinstance(self._registry.makeInstance('PythonDirectory',
                                                        self._store_dir, True),
                         PythonFileDirectory))

    def test_ramdirectory(self):
        self.assertEqual(self._registry.getClass('RamDirectory'),
                         RamDirectoryBackened)

        self.assert_(isinstance(self._registry.makeInstance('RamDirectory',
                                                        self._store_dir, True),
                            PyLucene.RAMDirectory))

    def test_bdbdirectory(self):
        self.assertEqual(self._registry.getClass('BdbDirectory'),
                         BdbDirectoryBackened)

        self.assertRaises(NotImplementedError, self._registry.makeInstance,
                          'BdbDirectory', self._store_dir, True),

    def tearDown(self):
        if os.path.exists(self._store_dir):
            shutil.rmtree(self._store_dir)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestStoreBackenedTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
