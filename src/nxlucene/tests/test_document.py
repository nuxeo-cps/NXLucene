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
"""NXLucene document.definition tests

$Id: $
"""

import unittest

from nxlucene.document import Document

class DocumentTestCase(unittest.TestCase):

    def test_contruct_no_uid(self):

        # Can't construct without an UID
        e = False
        try:
            doc = Document()
        except ValueError:
            e = True
        else:
            self.assert_(e)

    def test_construct(self):

        # String
        doc = Document('uid')

        # Integer
        doc = Document(1)


    def test_getUID(self):

        uid = unicode(1)
        doc = Document(uid)
        self.assertEqual(uid, doc.getUID())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
