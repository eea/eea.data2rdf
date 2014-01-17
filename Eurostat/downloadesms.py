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
import time, urllib, os, logging

NTNS="urn:eu.europa.ec.eurostat.navtree"

#
# Parse the XML files
#
class ToCParser(handler.ContentHandler):
    """ """

    def __init__(self, config):
        self.data = []
        self.level = 0
        self.seriesAttrs = {}
        self.obsnum = 0
        self.config = config
        self.failures = 0
        self.repository = config.get('sources','esmsfiles')

    def characters(self, data):
        self.data.append(data)

    def getData(self):
        return ''.join(self.data).strip()

    def resetData(self):
        self.data = []

    def startLastModified(self, tag, qname, attrs):
        self.data = []

    def endLastModified(self, tag, qname):
        s = self.getData()
        if s == '': return
        # lastModified is in tuple-time
        self.lastModified = time.strptime(s,"%d.%m.%Y")
        self.resetData()

    def startCode(self, tag, qname, attrs):
        self.resetData()

    def endCode(self, tag, qname):
        self.code = self.getData()
        self.resetData()

    def startMetadata(self, tag, qname, attrs):
        self._format = attrs.get((None,'format'))
        self.resetData()

    def endMetadata(self, tag, qname):
        """ Download the file to sdmxfiles
        """
        link = self.getData()
        self.resetData()
        if self._format == "sdmx":
            if link == "": return
            filename = self.repository + "/" + link[90:]
            try:
                lastDownload = os.stat(filename).st_mtime
            except:
                lastDownload = 0.0
            # If local mod time is older than self.lastModified then download
            if lastDownload > time.mktime(self.lastModified):
                logging.debug("%s newer than %s", filename, time.strftime("%Y-%m-%d", self.lastModified))
                return
            logging.debug("Retrieving %s last updated %s", link[90:], time.strftime("%Y-%m-%d",self.lastModified))
            try:
                urllib.urlretrieve(link, filename)
            except KeyboardInterrupt:
                if os.access(filename, os.R_OK): os.unlink(filename)
                raise
            except:
                self.failures += 1
                if os.access(filename, os.R_OK): os.unlink(filename)


    def startElementNS(self, tag, qname, attrs):
        self.level = self.level + 1
        if tag == (NTNS,'lastModified'): return self.startLastModified(tag, qname, attrs)
        elif tag == (NTNS,'metadata'): return self.startMetadata(tag, qname, attrs)
        elif tag == (NTNS,'code'): return self.startCode(tag, qname, attrs)

    def endElementNS(self, tag, qname):
        self.level = self.level - 1
        if tag == (NTNS,'lastModified'): return self.endLastModified(tag, qname)
        elif tag == (NTNS,'metadata'): return self.endMetadata(tag, qname)
        elif tag == (NTNS,'code'): return self.endCode(tag, qname)


def syncDatasets(config):
#   retrieveToc = config.getboolean('download','toc')
#   tocUrl = config.get('download','tocurl')

    # Grab table of contents
#   if retrieveToc:
#       logging.debug("Downloading table of contents")
#       urllib.urlretrieve(tocUrl, 'table_of_contents.xml')
    # Start XML parsing
    parser = make_parser()
    parser.setFeature(handler.feature_namespaces, 1)
    ch = ToCParser(config)
    parser.setContentHandler(ch)
    parser.setErrorHandler(handler.ErrorHandler())
    inpsrc = InputSource()
    inpsrc.setByteStream(open('table_of_contents.xml'))
    parser.parse(inpsrc)
    if ch.failures > 0:
        logging.warning("Failed: %s", ch.failures)

if __name__ == '__main__':
    import ConfigParser, getopt, sys

    config = ConfigParser.SafeConfigParser()
    config.read('eurostat.cfg')
    try:
        opts, args = getopt.getopt(sys.argv[1:], "v")
    except getopt.GetoptError, err:
        sys.exit(2)
    for o, a in opts:
        if o == "-v":
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    syncDatasets(config)
