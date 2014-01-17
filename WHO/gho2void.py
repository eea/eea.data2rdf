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
# You might need to install libxslt-python
import libxml2
import libxslt
from cStringIO import StringIO
import sys, time, zipfile, os, csv, codecs
from rdfwriter import RdfWriter
import fnmatch, getopt, urllib, logging
from toclabels import datasetLabels


if __name__ == '__main__':
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    config.read('who.cfg')
    baseuri = config.get('rdf', 'baseuri')
    skipline = config.get('rdf','skip')
    vocabulary = config.get('rdf', 'vocabulary')
    website = config.get('destination', 'void')
    ghoUrl = config.get('download', 'ghourl')
    dimensions = config.get('sources', 'dimensions')
    datasetsToBuild = []
    urllib.urlretrieve(ghoUrl, dimensions + '/GHO.xml')


    try:
        opts, args = getopt.getopt(sys.argv[1:], "v")
    except getopt.GetoptError, err:
        sys.exit(2)
    for o, a in opts:
        if o == "-v":
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    skiplist = skipline.split()

    dsLabels = datasetLabels(config)
    for a,l in dsLabels.items():
        buildIt = True
        for skip in skiplist:
            if fnmatch.fnmatch(a, skip):
                logging.debug("Skipping %s", a)
                buildIt = False
                break
        if buildIt:
            datasetsToBuild.append(a)

    # The list is too large to provide as a parameter for the stylesheet
    strOfDatasets = "<datasets>" + ",".join(datasetsToBuild)  +",</datasets>\n"
    inpFd = open("tmp/void-support.xml","wb")
    inpFd.write(strOfDatasets)
    inpFd.close()
    # Create the void.rdf file with a stylesheet
    styledoc = libxml2.parseFile('gho2void.xsl')
    style = libxslt.parseStylesheetDoc(styledoc)

    doc = libxml2.parseFile(dimensions + '/GHO.xml')
    result = style.applyStylesheet(doc, { "baseuri": "'" + baseuri +"'",
                                          "vocabulary": "'" + vocabulary +"'" })
    style.saveResultToFilename(website + '/void.rdf', result, 0)
    style.freeStylesheet()
    doc.freeDoc()
    result.freeDoc()
    os.unlink("tmp/void-support.xml")
