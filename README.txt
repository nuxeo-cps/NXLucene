$Id: $

========
NXLucene
========

What is it ?
------------

  NXLucene is a standalone multi threads remote server handling a
  Lucene index store. It is based on the PyLucene Python bindings and
  uses Twisted and zope.interface for its implementation.

  Currently, it supports the XML-RPC protocol but might be easily
  extended to other protocols, such as SOAP, thanks to its modular
  design.

  Note the FSDirectory backend is the only supported backend by
  NXLucene for now.

  The search results are returned as RSS streams.

  NXLucene exposes a custom query language for indexing and searching
  operations. Note the Lucene native search query is of course still
  supported. Check the interfaces.py module.

  While installing NXLucene, you will install as well the core libs,
  nxlucene namespace, that might be used by third party Python
  programs. For instance, the query lib might be useful to help you
  format your nxlucene queries.


Motivation
----------

  This product has been implemented in CPS project scope. CPS is based
  on Zope and the standard cataloging solution of Zope is the ZCatalog
  nowadays. The ZCatalog works well until a certain amount of data but
  the main problem is that Zope is dealing with a task it shouldn't
  have to deal with and thus decrease the overall performances of the
  Zope platform. You may see the ZCatalog as en hack on top of the
  ZODB because the ZODB doesn't have any native query language nor
  full index suppport.

  That's why we needed such as solution.

  This product has been designed to deal with millions of documents
  within the Lucene store.

  For integration examples :

   - Zope3 integration

     nuxeo.lucene (http://svn.nuxeo.org)

   - CPS integration

     CPSLuceneCatalog (http://svn.nuxeo.org)


Documentation
-------------

  See the doc sub-folder of this archive and check the NXLucene website.


Installation
------------

  See INSTALL.txt


More information

  - http://nxlucene.nuxeo.org

  - http://www.cps-project.org

  - http://www.nuxeo.com/en/


Get support
-----------

  - http://lists.nuxeo.com/cps-devel


Looking for commercial support ?
--------------------------------

  - http://www.nuxeo.com/en/


License
-------

  This Software is governed by the LGPL License. See LICENSE.txt or
  http://www.gnu.org/copyleft/lesser.html

  This software includes as well softwares under the MIT and the ZPL.


.. Emacs
.. Local Variables:
.. mode: rst
.. End:
.. Vim
.. vim: set filetype=rst:
