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
"""Setup using zpksupport

$Id$
"""
import os
import site
import sys

here = os.path.dirname(os.path.abspath(__file__))
buildsupport = os.path.join(here, "buildsupport")

# Add 'buildsupport' to sys.path and process *.pth files from 'buildsupport':
last = len(sys.path)
site.addsitedir(buildsupport)
if len(sys.path) > last:
    # Move all appended directories to the start.
    # Make sure we use ZConfig shipped with the distribution
    new = sys.path[last:]
    del sys.path[last:]
    sys.path[:0] = new

import zpkgsetup.package
import zpkgsetup.publication
import zpkgsetup.setup

VERSION = "0.0.1"

context = zpkgsetup.setup.SetupContext(
    "NXLucene", VERSION, __file__)

context.load_metadata(
    os.path.join(here,
                 zpkgsetup.publication.PUBLICATION_CONF))

context.walk_packages("src")
context.setup()
