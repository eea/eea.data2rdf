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

import csv, gzip
from cgi import escape
from urllib import quote

class RdfWriter(object):

    def __init__(self, filename, compress=True):
        if compress:
            self.outfd = gzip.open(filename, "w")
        else:
            self.outfd = open(filename, "w")
        self.namespaces = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'foaf': 'http://xmlns.com/foaf/0.1/',
            'dcterms': 'http://purl.org/dc/terms/',
            'skos': 'http://www.w3.org/2004/02/skos/core#',
            'foaf': 'http://xmlns.com/foaf/0.1/',
            'cc': 'http://creativecommons.org/ns#',
#           '': 'http://ontologycentral.com/2009/01/eurostat/ns#'
        }

    def addNamespace(self, prefix, namespace):
        self.namespaces[prefix] = namespace

    def output(self, data):
        self.outfd.write(data)

    def writeStartResource(self, rdftype, uri):
        self.output('<%s rdf:about="%s">\n' % (rdftype, escape(quote(uri, safe='?=&:#/,'))))

    def writeEndResource(self, rdftype):
        self.output('</%s>\n\n' % rdftype)

    def writeObjectProperty(self, name, reference):
        self.output(' <%s rdf:resource="%s"/>\n' % (name, escape(quote(reference, safe='?=&:#/,'))))

    def writeDataProperty(self, name, value, datatype='', lang=''):
        if datatype != '':
            self.output(' <%s rdf:datatype="%s">%s</%s>\n' % (name, datatype, escape(str(value)), name))
        elif lang != '':
            self.output(' <%s xml:lang="%s">%s</%s>\n' % (name, lang, escape(str(value)), name))
        else:
            self.output(' <%s>%s</%s>\n' % (name, escape(str(value)), name))

    def writeHeader(self, baseuri=None):
        self.output('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.output('<rdf:RDF')
        for ns, uri in self.namespaces.items():
            if ns == '':
                self.output(' xmlns="%s"\n' % uri)
            else:
                self.output(' xmlns:%s="%s"\n' % (ns, uri))
        if baseuri:
            self.output(' xml:base="%s"' % baseuri)
        self.output('>\n\n')

    def close(self):
        if self.outfd:
            self.outfd.close()
            self.outfd = None

    def writeFinish(self):
        self.writeEndResource('rdf:RDF')
        self.outfd.close()
        self.outfd = None


