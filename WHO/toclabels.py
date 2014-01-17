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
from xml.sax import make_parser, handler
from xml.sax.xmlreader import InputSource
import xml.sax.saxutils
from cStringIO import StringIO
import sys, time, os
import fnmatch, getopt
import urllib

#
# Parse the SDMX files
#
class GHODatasetLabels(handler.ContentHandler):
    """ Extract datasets from a GHO file and download
    """

    def __init__(self, config):
        skipline = config.get('rdf','skip')
        self.skiplist = skipline.split()
        self.data = []
        self.datasets = {}
        self._code = None
        self.elements = {
            (None, 'Code'): (self.startCode, self.endCode),
            (None, 'Display'): (self.startDisplay, self.endDisplay),
        }

    def startElementNS(self, tag, qname, attrs):
        method = self.elements.get(tag, (None, None) )[0]
        if method:
            method(tag, attrs)
        
    def endElementNS(self, tag, qname):
        method = self.elements.get(tag, (None, None) )[1]
        if method:
            method(tag)
            
    def getData(self):
        return ''.join(self.data).strip()

    def resetData(self):
        self.data = []

    def characters(self, data):
        self.data.append(data)

    def startCode(self, tag, attrs):
        self._code = attrs.get((None,'Label'))
        for skip in self.skiplist:
            if fnmatch.fnmatch(self._code, skip):
                self._code = None
                return
        self.datasets[self._code] = 1

    def endCode(self, tag):
        pass

    def startDisplay(self, tag, attrs):
        self.resetData()

    def endDisplay(self, tag):
        if self._code:
            self.datasets[self._code] = self.getData()
        self.resetData()


def datasetLabels(config):
    dimensions = config.get('sources', 'dimensions')
    parser = make_parser()
    parser.setFeature(handler.feature_namespaces, 1)
    ch = GHODatasetLabels(config)
    parser.setContentHandler(ch)
    parser.setErrorHandler(handler.ErrorHandler())
    ghofd = open(dimensions + '/GHO.xml','rb')
    parser.parse(ghofd)
    ghofd.close()
    return ch.datasets



if __name__ == '__main__':
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    config.read('who.cfg')

    x = datasetLabels(config)
    for k,v in x.items():
        print k,v



