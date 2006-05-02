========
NXLucene
========

:Author: Julien Anguenot
:Revision: $Id$

.. sectnum::    :depth: 6
.. contents::   :depth: 1

What is it ?
============

  NXLucened_ is a standalone multi threads remote server handling a
  Lucene_ index store. It is based on the PyLucene_ Python_ bindings and
  uses Twisted_ and ZopeInterface_ for its implementation.

  Currently, it supports the XML-RPC protocol but might be easily
  extended to other protocols, such as SOAP, thanks to its modular
  design.

  Note the FSDirectory backend is the only supported backend by
  NXLucened_ for now.

  The search results are returned as RSS streams.

  NXLucened_ exposes an XML query language for indexing and searching
  operations. Note the Lucene_ native search query is of course still
  supported. Check the interfaces.py module.

  While installing NXLucened_, you will install as well the core libs,
  nxlucene namespace, that might be used by third party Python
  programs. For instance, the query lib might be useful to help you
  format your nxlucene queries.


.. _PyLucene: http://pylucene.osafoundation.org/
.. _Python: http://www.python.org/
.. _Lucene: http://lucene.apache.org/
.. _ZopeInterface: http://zope.org/Products/ZopeInterface	
.. _Twisted: http://twistedmatrix.com/projects/core/

Motivation
==========

  This product has been implemented in the CPS project scope. CPS_ is
  based on Zope_ and the standard cataloging solution of Zope_ is the
  ZCatalog_ nowadays. The ZCatalog_ works well until a certain amount
  of data but the main problem is that Zope_ is dealing with a task it
  shouldn't have to deal with and thus decrease the overall
  performances of the overall Zope_ platform. You may see, anyway, the
  ZCatalog_ as an hack on top of the ZODB_ because the ZODB_ doesn't
  have any native query language nor full index suppport.

  That's why we needed such as solution for CPS_.

  This product has been designed to deal with millions of documents
  within the Lucene_ store.

  For NXLucened_ use examples :

  - Zope3_ integration

    nuxeo.lucene_

  - CPS_ integration

    CPSLuceneCatalog_

.. _CPS: http://www.cps-project.org/
.. _Zope: http://www.zope.org/
.. _ZCatalog: http://www.faqs.org/docs/ZopeBook/SearchingZCatalog.html
.. _ZODB: http://www.zope.org/Wikis/ZODB/
.. _Zope3: http://dev.zope.org/Zope3/
.. _nuxeo.lucene: http://svn.nuxeo.org/pub/nuxeo.lucene
.. _CPSLuceneCatalog: http://svn.nuxeo.org/pub/CPSLuceneCatalog/
.. _NXLucened: http://www.cps-project.org/sections/nxlucene

Documentation
=============

  See the doc sub-folder of this archive and check the NXLucened_ website_

.. _website: http://www.cps-project.org/sections/nxlucene/

Installation
============

  See INSTALL.txt or here_

.. _here : http://www.cps-project.org/workspaces/development/projects/nxlucene/readme

Need support
============

  - http://lists.nuxeo.com/mailman/listinfo/cps-devel


Looking for commercial support ?
================================

  You can contact Nuxeo_

  - http://www.nuxeo.com/en/

.. _Nuxeo: http://www.nuxeo.com/en/

License
=======

  This Software is governed by the LGPL License. See LICENSE.txt or
  http://www.gnu.org/copyleft/lesser.html

  This software includes as well softwares under the MIT and the ZPL.


.. Emacs
.. Local Variables:
.. mode: rst
.. End:
.. Vim
.. vim: set filetype=rst:
