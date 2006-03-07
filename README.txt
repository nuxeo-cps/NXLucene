$Id: $

WebLucene
==========

What is is ? 

  WebLucene is a standalone multi threads remote server handling
  Lucene index store. It is based on the PyLucene Python bindings and
  uses twisted and zope.interface for its implementation.
  
  Currently, it supports the XML-RPC protocol but might be easily
  extended to other protocols, such as SOAP, thanks to its modular
  design.

  WebLucene supports the FSDirectory backend for now.

  The search results are returned as RSS stream.

  WebLucene exposes a custom query language for indexing and searching
  operations. Not the Lucene native search query is of course still
  supported.

  XXX

Motivation 

  XXX

Installation

  See INSTALL.txt

More information 

  - http://weblucene.nuxeo.org

  - XXX 
  
License : 

  This Software is governed by the LGPL License. See LICENSE.txt
  http://www.gnu.org/copyleft/lesser.html

  This software includes as well softwares under the MIT and the ZPL.
