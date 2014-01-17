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
from xml.sax import make_parser, handler
from xml.sax.xmlreader import InputSource
import xml.sax.saxutils
from cStringIO import StringIO
import time, zipfile, os, csv, codecs
from rdfwriter import RdfWriter
import fnmatch, logging
from toclabels import datasetLabels

#
# Parse the SDMX files
#
class DSDDimensions(handler.ContentHandler):
    """ Extract dimensions from an DSD file and write RDF
    """

    def __init__(self, dataset, config, rdfout):
        self.dataset = dataset
        self.rdfout = rdfout
        self.data = []
        self.timeOfRun = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.structureNS = config.get('sdmx', 'structure.ns', False, {'dataset': dataset})
        self.elements = {
            (self.structureNS, 'Components'): (self.startComponents, self.endComponents),
            (self.structureNS, 'Dimension'): (self.startDimension, None),
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

    def startComponents(self, tag, attrs):
        self.rdfout.writeStartResource("rdf:Description", "#%s" % self.dataset)

    def endComponents(self, tag):
        self.rdfout.writeEndResource("rdf:Description")

    def startDimension(self, tag, attrs):
        conceptRef = attrs.get((None,'conceptRef'))
        if conceptRef.lower() == conceptRef:
            self.rdfout.writeObjectProperty("void:vocabulary", "http://dd.eionet.europa.eu/vocabulary/eurostat/%s/" % conceptRef)

    def endDimension(self, tag):
        pass

def createDimsAsDatasets(config, rdfout):
    """ Create void:Dataset resources for all the dimensions
    """
    # TODO: "en/dimlst.dic" and "all_dic.zip" to be fetched from config file
    dimLstFN = "en/dimlst.dic"
    zfd = zipfile.ZipFile("all_dic.zip")
    winfile = StringIO(zfd.read(dimLstFN))
    tsvfile = codecs.EncodedFile(winfile, "utf-8", "cp1252")
    reader = csv.reader(tsvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        if len(row) == 0: continue    # Found an empty line
        code = row[0].lower().strip()
        if code == "": continue       # Found an empty code
        # TODO: Could add dcterms:modified here - from zip timestamp
        rdfout.writeStartResource("void:Dataset", "#%s" % code)
        rdfout.writeDataProperty("dcterms:title", "Code list: " + row[1].strip())
        rdfout.writeObjectProperty("dcterms:creator", "#Eurostat")
        rdfout.writeObjectProperty("void:dataDump", "dic/%s.rdf" % code)
        rdfout.writeEndResource("void:Dataset")
    tsvfile.close()
    zfd.close()



def createVocRefs(config, dataset, rdfout):
    repository = config.get('sources','sdmxfiles')

    logging.debug("Scanning: %s", dataset)
    try:
        parser = make_parser()
        parser.setFeature(handler.feature_namespaces, 1)
        ch = DSDDimensions(dataset, config, rdfout)
        parser.setContentHandler(ch)
        parser.setErrorHandler(handler.ErrorHandler())

        zfd = zipfile.ZipFile(repository + "/" + dataset + ".sdmx.zip")
        datafd = StringIO(zfd.read(dataset + ".dsd.xml"))
        parser.parse(datafd)
        datafd.close()
        zfd.close()
    except:
        logging.error("Not found in %s: %s", repository, dataset)



if __name__ == '__main__':
    import ConfigParser, getopt, sys
    config = ConfigParser.SafeConfigParser()
    config.read('eurostat.cfg')
    baseuri = config.get('rdf', 'baseuri')
    skipline = config.get('rdf','skip')
    vocabulary = config.get('rdf', 'vocabulary')
    website = config.get('destination', 'void')
    datasetsToBuild = []

    try:
        opts, args = getopt.getopt(sys.argv[1:], "dv")
    except getopt.GetoptError, err:
        sys.exit(2)
    buildLinks = True
    for o, a in opts:
        if o == "-d":
            buildLinks = False
        if o == "-v":
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    skiplist = skipline.split()
    dsLabels = datasetLabels()
    if buildLinks:
        # Get the use of vocabularies from the DSDs
        rdfout = RdfWriter("vocabulary-links.rdf", False)
        rdfout.addNamespace("void", "http://rdfs.org/ns/void#")
        rdfout.writeHeader(baseuri)
    for a,l in dsLabels.items():
        buildIt = True
        for skip in skiplist:
            if fnmatch.fnmatch(a, skip):
                logging.debug("Skipping: %s", a)
                buildIt = False
                break
        if buildIt:
            datasetsToBuild.append(a)
            if buildLinks:
                createVocRefs(config, a, rdfout)
    if buildLinks:
        #createDimsAsDatasets(config, rdfout)
        rdfout.writeFinish()

    # The list is too large to provide as a parameter for the stylesheet
    strOfDatasets = "<datasets>" + ",".join(datasetsToBuild)  +",</datasets>\n"
    inpFd = open("void-support.xml","wb")
    inpFd.write(strOfDatasets)
    inpFd.close()
    # Create the void.rdf file with a stylesheet
    styledoc = libxml2.parseFile('estat-toc2rdf.xsl')
    style = libxslt.parseStylesheetDoc(styledoc)

    doc = libxml2.parseFile('table_of_contents.xml')
    result = style.applyStylesheet(doc, { "baseuri": "'" + baseuri +"'",
                                          "vocabulary": "'" + vocabulary +"'" })
    style.saveResultToFilename(website + '/void.rdf', result, 0)
    style.freeStylesheet()
    doc.freeDoc()
    result.freeDoc()
    os.unlink("void-support.xml")
