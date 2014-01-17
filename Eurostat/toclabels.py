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
import time, urllib, os

NTNS="urn:eu.europa.ec.eurostat.navtree"

#
# Parse the XML files
#
class ToCLabelParser(handler.ContentHandler):
    """ """

    def __init__(self):
        self.data = []
        self.inLeaf = False
        self.hasLink = False
        self.datasets = {}
        self.elements = {
            (NTNS,'title'): (self.startTitle, self.endTitle),
            (NTNS,'leaf'): (self.startLeaf, self.endLeaf),
            (NTNS,'downloadLink'): (self.startDownloadLink, self.endDownloadLink),
            (NTNS,'code'): (self.startCode, self.endCode),
        }

    def startElementNS(self, tag, qname, attrs):
        method = self.elements.get(tag, (None, None) )[0]
        if method:
            method(tag, attrs)

    def endElementNS(self, tag, qname):
        method = self.elements.get(tag, (None, None) )[1]
        if method:
            method(tag)

    def characters(self, data):
        self.data.append(data)

    def getData(self):
        return ''.join(self.data).strip()

    def resetData(self):
        self.data = []


    def startLeaf(self, tag, attrs):
        self.inLeaf = True
        self.hasLink = False
        self.resetData()

    def endLeaf(self, tag):
        self.inLeaf = False
        if self.hasLink == True:
            self.datasets[self.code] = self.title
        self.title = ""
        self.code = ""
        self.resetData()

    def startCode(self, tag, attrs):
        self.resetData()

    def endCode(self, tag):
        self.code = self.getData()
        self.resetData()

    def startDownloadLink(self, tag, attrs):
        if attrs.get((None,'format')) == "sdmx":
            self.hasLink = True
        self.resetData()

    def endDownloadLink(self, tag):
        self.resetData()

    def startTitle(self, tag, attrs):
        language = attrs.get((None,'language'))
        self.inTitle = False
        if self.inLeaf and language == "en":
            self.inTitle = True
        self.resetData()

    def endTitle(self, tag):
        """ Download the file to sdmxfiles
        """
        if self.inTitle == True:
            self.title = self.getData()
        self.resetData()


def datasetLabels():
    """ Get the titles of the datasets from the TOC
    """
    parser = make_parser()
    parser.setFeature(handler.feature_namespaces, 1)
    ch = ToCLabelParser()
    parser.setContentHandler(ch)
    parser.setErrorHandler(handler.ErrorHandler())
    inpsrc = InputSource()
    inpsrc.setByteStream(open('table_of_contents.xml'))
    parser.parse(inpsrc)
    return ch.datasets

if __name__ == '__main__':
    x = datasetLabels()
    for k,v in x.items():
        print k,v
