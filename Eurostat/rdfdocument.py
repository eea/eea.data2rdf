#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Søren Roug, European Environment Agency
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Contributor(s):
#

from rdfwriter import RdfWriter
import time

class RdfDocument(RdfWriter):

    def __init__(self, config, filename, compress=True):
        """ Expects a config file with the content in UTF-8 encoding
        """
        super(RdfDocument, self).__init__(filename, compress)
        self.config = config
        self.baseuri = self.config.get('rdf', 'baseuri')
        self.timeOfRun = time.strftime("%Y-%m-%dT%H:%M:%S")

    def writeProvenance(self, document, dataset):
        self.writeStartResource("rdf:Description", document)
        for prop, val in self.config.items('provenance', False, {'dataset': dataset, 'document': document}):
            if prop in ('dataset','document'): continue
            prop = prop.replace('.',':')
            if val[0] == '<' and val[-1] == '>':
                self.writeObjectProperty(prop, val[1:-1])
            else:
                self.writeDataProperty(prop, val)

        self.writeDataProperty("dcterms:modified", self.timeOfRun, datatype="http://www.w3.org/2001/XMLSchema#dateTime")
        self.writeEndResource("rdf:Description")

