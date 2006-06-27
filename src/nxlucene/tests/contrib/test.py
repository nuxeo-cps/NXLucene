#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time

from nuxeo.lucene.catalog import LuceneCatalog
from nuxeo.lucene.interfaces import ILuceneCatalog
from nuxeo.lucene.testing import registerDirective

from zope.app.testing import ztapi

import zope.interface
import zope.app.intid.interfaces

import transaction


class ITest(zope.interface.Interface):
    pass

class P(object):
    zope.interface.implements(ITest)
    
    def __init__(self, name, givenName = '', phone = ''):
        self.name = name
        self.givenName = givenName
        self.phone = phone

    def getFullName(self):
        return self.name + ' ' + self.givenName


cat = LuceneCatalog('http://localhost:9180')
ztapi.provideUtility(ILuceneCatalog, cat)

registerDirective("""
      <lucene:fields for="zope.interface.Interface">
          <lucene:field name = "name" attribute = 'name'
                        type = "Text" analyzer = "Standard"/>
      </lucene:fields>
      """)

registerDirective("""
      <lucene:fields for="zope.interface.Interface">
          <lucene:field name = "givenName" attribute = 'givenName'
                        type = "UnStored" analyzer = "Standard"/>
      </lucene:fields>
      """)

registerDirective("""
      <lucene:fields for="zope.interface.Interface">
          <lucene:field name = "phone" attribute = 'phone'
                        type = "UnIndexed" analyzer = "Standard"/>
      </lucene:fields>
      """)


registerDirective("""
      <lucene:fields for="zope.interface.Interface">
          <lucene:field name = "fullname" attribute = 'getFullName'
                        type = "Text" analyzer = "Standard"/>
      </lucene:fields>
      """)

registerDirective("""
      <lucene:columns>
          <lucene:column field_name="name"/>
      </lucene:columns>
      """)

registerDirective("""
      <lucene:columns>
          <lucene:column field_name="phone"/>
      </lucene:columns>
      """)

registerDirective("""
      <lucene:columns>
          <lucene:column field_name="fullName"/>
      </lucene:columns>
      """)

print "aufruf cat.getFieldNamesFor(): \n" + str(cat.getFieldNamesFor())


o1 = P(u'Maier', u'Sepp', u'0815')
o2 = P(u'Beckenbauer', u'Franz', u'125')
o3 = P(u'Hönes', 'Uli', u'089')

class Ids:
    zope.interface.implements(zope.app.intid.interfaces.IIntIds)
    
    def __init__(self, data):
        self.data = data
    def getObject(self, id):
        return self.data[id]
    def __iter__(self):
        return self.data.iterkeys()

ids = Ids({1: o1, 2: o2, 3: o3})
ztapi.provideUtility(zope.app.intid.interfaces.IIntIds, ids)

print "call cat.clean()"
cat.clean()
print "cat clean done"
transaction.commit()

print "len of cat: " + str(len(cat))

print "index 1: " + str(cat.index(1, o1))
transaction.commit()
print "len of cat: " + str(len(cat))
while(len(cat) == 0): pass
print "len of cat: " + str(len(cat))
#print "waiting 4 sec"
#time.sleep(4)

print str(cat.searchResults(search_fields={u'uid': '1'})[0])
print str(cat.searchResults(return_fields=(u'name',), search_fields={u'uid': '1'})[0])
print str(cat.searchResults(return_fields=(u'phone',), search_fields={u'uid': '1'})[0])

print "aufruf cat.index(2, o2) (erwartet wird True): " + str(cat.index(2, o2))
transaction.commit()
print "len von cat: " + str(len(cat))
print str(cat.searchResults(search_fields={u'uid': '2'})[0])
print str(cat.searchResults(return_fields=(u'name',), search_fields={u'uid': '2'})[0])
print str(cat.searchResults(return_fields=(u'phone',), search_fields={u'uid': '2'})[0])

print str(cat.index(3, o3, indexes=('name',)))
transaction.commit()
print "len cat: " + str(len(cat))
print str(cat.searchResults(search_fields={u'uid': '3'})[0])

print str(cat.searchResults(return_fields=(u'name',), search_fields={u'uid': '3'})[0])
print str(cat.searchResults(return_fields=(u'name',), search_fields={u'uid': '2'})[0])
print str(cat.searchResults(return_fields=(u'name',), search_fields={u'uid': '1'})[0])

