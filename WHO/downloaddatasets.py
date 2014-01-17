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
import sys, time, os, logging
import fnmatch, getopt
import urllib

#
# Parse the SDMX files
#
class GHODatasets(handler.ContentHandler):
    """ Extract datasets from a GHO file and download
    """

    def __init__(self, config):
        self.dataurl = config.get('download', 'dataurl')
        self.repository = config.get('sources','xmlfiles')
        skipline = config.get('rdf','skip')
        self.skiplist = skipline.split()
        self.data = []
        self.elements = {
            (None, 'Code'): (self.startCode, self.endCode),
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
        code = attrs.get((None,'Label'))
        for skip in self.skiplist:
            if fnmatch.fnmatch(code, skip):
                logging.debug("Skipping: %s", code)
                return
        filename = self.repository + '/' + code + '.xml'
        try:
            lastDownload = os.stat(filename).st_mtime
        except: 
            lastDownload = 0.0
        if lastDownload > 0.0:
            logging.debug("Already downloaded: %s", code)
            return
        logging.info("Retrieving: %s", code)
        urllib.urlretrieve(self.dataurl + code + '.xml', filename)
        time.sleep(2)  # Be nice to the server

    def endCode(self, tag):
        pass




if __name__ == '__main__':
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    config.read('who.cfg')
    baseuri = config.get('rdf', 'baseuri')
    #vocabulary = config.get('rdf', 'vocabulary')
    website = config.get('destination', 'void')
    ghoUrl = config.get('download', 'ghourl')
    dimensions = config.get('sources', 'dimensions')
    datasetsToBuild = []
    # Get the XML file containing the list of datasets
    urllib.urlretrieve(ghoUrl, dimensions + '/GHO.xml')


    try:
        opts, args = getopt.getopt(sys.argv[1:], "v")
    except getopt.GetoptError, err:
        sys.exit(2)
    for o, a in opts:
        if o == "-v":
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    parser = make_parser()
    parser.setFeature(handler.feature_namespaces, 1)
    ch = GHODatasets(config)
    parser.setContentHandler(ch)
    parser.setErrorHandler(handler.ErrorHandler())

    ghofd = open(dimensions + '/GHO.xml','rb')
    parser.parse(ghofd)
    ghofd.close()

