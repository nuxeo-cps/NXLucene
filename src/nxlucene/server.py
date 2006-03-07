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
"""WebLucene XMLRPC server

$Id$
"""

import os
import threading
import logging
import PyLucene
import time

import zope.interface

from interfaces import ILuceneServer

from indexer import LuceneIndexer
from reader import LuceneReader
from searcher import LuceneSearcher

import rss.resultset

MAX_SEARCH = 100

class LuceneServer(object):
    """Lucene server
    """

    zope.interface.implements(ILuceneServer)

    def __init__(self, store_dir):
        self.store_dir = store_dir
        self.write_lock = threading.Lock()
        self.search_sema = threading.BoundedSemaphore(MAX_SEARCH)
        self.log = logging.getLogger("LuceneServer")

    def __len__(self):
        reader = self._getReader()
        if reader is None:
            return 0
        return reader.get().numDocs()

    def _getDocumentByUID(self, uid):
        # Return a document instance given an UID
        res = None
        searcher = self._getSearcher()
        if searcher is None:
            return res
        query = PyLucene.TermQuery(PyLucene.Term('uid', unicode(uid)))
        hits = list(searcher.get().search(query))
        if hits:
            res = hits[0][1]
        searcher.close()
        if res:
            self.log.debug("FOUND document with uid=%s" % str(uid))
        else:
            self.log.debug("Document with uid=%s NOT FOUND" % str(uid))
        return res

    def optimize(self, indexer=None):
        self.log.debug("Optimize indexes store")
        close = False
        if indexer is None:
            indexer = self._getIndexer().get()
            close = True
        self.write_lock.acquire()
        indexer.optimize()
        # XXX implement this properly.
        #ticker = Ticker()
        #threading.Thread(target=ticker.run).start()
        #writer.optimize()
        #ticker.tick = False
        if close:
            indexer.close()
        self.write_lock.release()
        return True

    def clean(self):

        self.write_lock.acquire()

        indexer = LuceneIndexer(self.store_dir, creation=True)
        indexer.close()

        self.write_lock.release()

        self.log.info("Indexes Store has been cleaned up")
        return True

    def _indexob(self, uid, ob, attributs=()):

        self.write_lock.acquire()

        # Check if we got an existing document given this UID.
        doc = self._getDocumentByUID(uid)
        delete_existing = doc and True or False

        # In case we need to update we'll have to take care of the
        # existing fields.
        existing_fields = () 

        if doc is not None:
            self.log.debug("FOUND document with uid=%s to update" % str(uid))
            # Keep fields for update purpose.
            existing_fields = doc.fields()
        else:
            self.log.debug(
                "Document with uid=%s does not exist yet" % str(uid))

        # Create a new document instance.
        doc = PyLucene.Document()
        doc.add(PyLucene.Field.Keyword('uid', unicode(uid)))            

        for index in attributs:
            value = getattr(ob, index, '')
            self.log.debug(
                "Adding Field on doc for index %s with value %s "
                % (index, value))
            # XXX make this configurable.
            doc.add(
                PyLucene.Field(index, unicode(value), True, True, True))

        # Update
        for field in existing_fields:
            if field.name() not in attributs and field.name() != 'uid':
                doc.add(field)

        # We got to remove the document from the index first.
        # http://wiki.apache.org/jakarta
        # -lucene/LuceneFAQ#head-917dd4fc904aa20a34ebd23eb321125bdca1dea2
        if delete_existing:
            self._unindexob(uid, lock=False)

        # Merge indexes
        indexer = self._getIndexer()
        writer = indexer.get()
        writer.addDocument(doc)
#        writer.optimize()
        indexer.close()

        self.write_lock.release()

    def _unindexob(self, uid, lock=True):

        if lock:
            self.write_lock.acquire()

        reader = self._getReader()
        if reader is None:
            return False

        ireader = reader.get()

        t = PyLucene.Term('uid', unicode(uid))
        ireader.deleteDocuments(t)

        if ireader.hasDeletions():
            self.log.info("UNINDEXED document with uid=%s" % str(uid))
        else:
            self.log.info("CANNOT UNINDEXED document with uid=%s"
                          "NOT FOUND" % str(uid))

        reader.close()

        if lock:
            self.write_lock.release()

    def _reindexob(self, uid, ob, attributs=()):
        self._indexob(uid, ob, attributs)

    def _search(self, return_fields=(), kws=None):

        # XXX make this configurable
        start = 0
        stop = 10

        # uid will be returned automatically
        return_fields = ('uid',) + return_fields

        results = rss.resultset.ResultSet()

        # This behavior is not allowed.
        if kws is None:
            return results.getStream()

        # Probably no indexes are created yet.
        searcher = self._getSearcher()
        if not searcher:
            return results.getStream()

        # TODO : Make this configurable
        analyzer = PyLucene.StandardAnalyzer()

        # TODO : Optimize me using PhraseQuery
        uids = []
        for index, value in kws.items():
            self.log.debug('_search for %s, %s' % (index, value))
            parser = PyLucene.QueryParser(index, analyzer)
            # XXX : should be extracted from stream.
            parser.setOperator(PyLucene.QueryParser.DEFAULT_OPERATOR_AND)

            # XXX harcoded here. Should be part of a configuration.
            if index == 'uid':
                query = PyLucene.TermQuery(
                    PyLucene.Term('uid', unicode(value)))
            else:
                query = parser.parseQuery(value)
#            self.log.debug('query %s' %str(query))
            hits = list(searcher.get().search(query))
            hits = hits[start:stop]
            for i, doc in hits:
                table = dict([(field.name(), field.stringValue())
                              for field in doc
                              if unicode(field.name()) in return_fields])
                uid = table['uid']
                if uid not in uids:
                    uids.append(uid)
                    del table['uid']
                    self.log.debug("match for %s %s" %(uid, str(table)))
                    results.addItem(uid, table)
        searcher.close()
        return results.getStream()

    def _getIndexer(self):
        creation = False
        if not os.path.exists(self.store_dir):
            creation = True
        analyzer = PyLucene.StandardAnalyzer()
        return LuceneIndexer(self.store_dir, creation, analyzer)

    def _getSearcher(self):
        if not os.path.exists(self.store_dir):
            return None
        return LuceneSearcher(self.store_dir)

    def _getReader(self):
        try:
            reader = LuceneReader(self.store_dir)
        except PyLucene.JavaError:
            # Store is not initialized yet.
            reader = None
        return reader

    def _getStore(self, creation=False):
        if not os.path.exists(self.store_dir):
            creation = True
        return PyLucene.FSDirectory.getDirectory(self.store_dir, creation)


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            time.sleep(1.0)
