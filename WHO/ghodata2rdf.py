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
import sys, time, gzip, os, logging
from rdfdocument import RdfDocument
import fnmatch
from toclabels import datasetLabels

#
# Parse the Data files
#
class DataConverter(handler.ContentHandler):
    """ Extract observations from an Data file and write RDF
    """

    def __init__(self, dataset, config, rdfout, dsLabel):
        self.dataset = dataset
        self.baseuri = config.get('rdf', 'baseuri')
        self.vocabulary = config.get('rdf', 'vocabulary')
        self.rdfout = rdfout
        self.dsLabel = dsLabel
        self.data = []
        self.level = 0
        self.objUri = ""
        self.dimLst = ""
        self.allDimensions = {}
        self.dims = {}
        self.obsnum = 0
        self.timeOfRun = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.elements = {
            (None ,'Data'): (self.startData, None),
            (None ,'Observation'): (self.startObservation, self.endObservation),
            (None ,'GHO'): (self.startGHO, self.endGHO),
            (None ,'Dim'): (self.startDim, None),
            (None ,'Display'): (self.startDisplay, self.endDisplay),
            (None ,'Value'): (self.startValue, None),
            (None ,'Comments'): (None, self.endComments)
        }

    # Common dimensions from http://purl.org/linked-data/sdmx/2009/dimension
    # Would also require usage of common vocabularies
    sdmxDimensions = {
        'country': 'sdmx-dimension:refArea',
    }

    def startElementNS(self, tag, qname, attrs):
        self.level = self.level + 1
        method = self.elements.get(tag, (None, None) )[0]
        if method:
            method(tag, attrs)
        
    def endElementNS(self, tag, qname):
        self.level = self.level - 1
        method = self.elements.get(tag, (None, None) )[1]
        if method:
            method(tag)
            
    def getData(self):
        return ''.join(self.data).strip()

    def resetData(self):
        self.data = []

    def characters(self, data):
        self.data.append(data)

    def writeTimePeriod(self, timeFormat, timePeriod):
	""" Creates a date from the time period in the data
            LTAA = long term anual average
        """
        if timePeriod in ("TARGET", "LTAA"):
            self.rdfout.writeDataProperty("sdmx-dimension:timePeriod", timePeriod)
            return
        if timeFormat == "P1Y":
            date = timePeriod + "-01-01"
        elif timeFormat == "P6M":
            q = timePeriod[-2:]
            if q == "B1": date = timePeriod[:4] + "-01-01"
            elif q == "B2": date = timePeriod[:4] + "-07-01"
        elif timeFormat == "P3M":
            q = timePeriod[-2:]
            if q == "Q1": date = timePeriod[:4] + "-01-01"
            elif q == "Q2": date = timePeriod[:4] + "-04-01"
            elif q == "Q3": date = timePeriod[:4] + "-07-01"
            elif q == "Q4": date = timePeriod[:4] + "-10-01"
        elif timeFormat == "P1M":
            date = timePeriod + "-01"
        elif timeFormat == "P1D":
            date = timePeriod[:4] + "-" + timePeriod[4:6] + "-" + timePeriod[6:8]
        elif timeFormat in ("P5Y", "P4Y", "P3Y"):
            # period has staryear - endyear concatenated
            date = timePeriod[:4] + "-01-01"
        # Missing PT1M - minutely
        self.rdfout.writeDataProperty("sdmx-dimension:timePeriod", date, datatype="http://www.w3.org/2001/XMLSchema#date")


    def startData(self, tag, attrs):
        self.resetData()

    def startGHO(self, tag, attrs):
        self.rdfout.addNamespace("property", self.vocabulary)
        self.rdfout.addNamespace("qb", "http://purl.org/linked-data/cube#")
        self.rdfout.addNamespace("sdmx-measure", "http://purl.org/linked-data/sdmx/2009/measure#")
        self.rdfout.addNamespace("sdmx-dimension", "http://purl.org/linked-data/sdmx/2009/dimension#")
        self.rdfout.addNamespace("sdmx-attribute", "http://purl.org/linked-data/sdmx/2009/attribute#")
        self.rdfout.addNamespace("cr","http://cr.eionet.europa.eu/ontologies/contreg.rdf#")
        self.rdfout.addNamespace("dc", "http://purl.org/dc/elements/1.1/") # Only for the bookmark
        self.rdfout.writeHeader(self.baseuri)

        self.rdfout.writeProvenance("data/%s.rdf.gz" % self.dataset, "%s.xml" % self.dataset)
        # Write the DataSet object
        self.rdfout.writeStartResource("qb:DataSet", "data/%s" % self.dataset)
        if self.dsLabel:
            self.rdfout.writeDataProperty("rdfs:label", self.dsLabel.encode('utf-8'))
        created = attrs.get((None,'Created'))
        if created:
            self.rdfout.writeDataProperty("dcterms:created", created, datatype="http://www.w3.org/2001/XMLSchema#dateTime")
        self.rdfout.writeObjectProperty("cr:hasSparqlBookmark","data/%s#sparqlSimple" % self.dataset)
        self.rdfout.writeObjectProperty("cr:hasSparqlBookmark","data/%s#sparqlJoined" % self.dataset)
        self.rdfout.writeEndResource("qb:DataSet")


    def endGHO(self, tag):
        self.rdfout.writeStartResource("rdf:Description", "data/%s.rdf.gz" % self.dataset)
        self.rdfout.writeObjectProperty("foaf:primaryTopic", "data/" + self.dataset)
        self.rdfout.writeObjectProperty("cr:hasSparqlBookmark","data/%s#sparqlSimple" % self.dataset)
        self.rdfout.writeObjectProperty("cr:hasSparqlBookmark","data/%s#sparqlJoined" % self.dataset)
        self.rdfout.writeObjectProperty("dcterms:requires", "http://purl.org/linked-data/sdmx/2009/code")
        for p in self.allDimensions.keys():
            self.rdfout.writeObjectProperty("dcterms:requires", "dic/%s.rdf" % p)
        self.rdfout.writeEndResource("rdf:Description")

        sparql = self.makeSparqlQuery(False)
        self.rdfout.writeStartResource("cr:SparqlBookmark", "data/%s#sparqlSimple" % self.dataset)
        self.rdfout.writeDataProperty("rdfs:label","Simple SPARQL query on %s" % self.dataset)
        self.rdfout.writeDataProperty("cr:sparqlQuery", sparql)
        self.rdfout.writeDataProperty("dcterms:format", "text/html")
        self.rdfout.writeDataProperty("dc:format", "text/html")
        self.rdfout.writeEndResource("cr:SparqlBookmark")

        sparql = self.makeSparqlQuery(True)
        self.rdfout.writeStartResource("cr:SparqlBookmark", "data/%s#sparqlJoined" % self.dataset)
        self.rdfout.writeDataProperty("rdfs:label","SPARQL query on %s with joins on dictionaries" % self.dataset)
        self.rdfout.writeDataProperty("cr:sparqlQuery", sparql)
        self.rdfout.writeDataProperty("dcterms:format", "text/html")
        self.rdfout.writeDataProperty("dc:format", "text/html")
        self.rdfout.writeEndResource("cr:SparqlBookmark")

        self.rdfout.writeFinish()

    def makeSparqlQuery(self, useDics = False):
	""" Create an example SPARQL query for this dataset """
        args = {'dataset': self.dataset, 'baseuri': self.baseuri , 'vocabulary': self.vocabulary }
        sparql =          "PREFIX qb: <http://purl.org/linked-data/cube#>\n"
        sparql = sparql + "PREFIX sdmx-measure: <http://purl.org/linked-data/sdmx/2009/measure#>\n"
        sparql = sparql + "PREFIX sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>\n"
        sparql = sparql + "PREFIX sdmx-attribute: <http://purl.org/linked-data/sdmx/2009/attribute#>\n"
        sparql = sparql + "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n"
        sparql = sparql + "PREFIX property: <%(vocabulary)s>\n" % args
        sparql = sparql + "\n"
        sparql = sparql + "SELECT *\nWHERE {\n"
        sparql = sparql + "    _:%(dataset)s qb:dataSet <%(baseuri)sdata/%(dataset)s>.\n" % args
        if useDics:
            sparql = sparql + "    _:%(dataset)s sdmx-dimension:freq _:freq . _:freq skos:prefLabel ?freq .\n" % args
        else:
            sparql = sparql + "    _:%(dataset)s sdmx-dimension:freq ?freq .\n" % args
        sparql = sparql + "    _:%(dataset)s sdmx-dimension:timePeriod ?date .\n" % args
        for p, onum in self.allDimensions.items():
            if onum != self.obsnum:
                if useDics:
                    template = "    OPTIONAL { _:%(dataset)s %(predicate)s _:%(property)s . _:%(property)s skos:notation ?%(property)s . }\n"
                else:
                    template = "    OPTIONAL { _:%(dataset)s %(predicate)s ?%(property)s . }\n"
            else:
                if useDics:
                    template = "    _:%(dataset)s %(predicate)s _:%(property)s . _:%(property)s skos:notation ?%(property)s .\n"
                else:
                    template = "    _:%(dataset)s %(predicate)s ?%(property)s .\n"
            sparql = sparql + template % {'dataset': self.dataset, 'property': p, 'predicate': self.sdmxDimensions.get(p, 'property:'+p)}
        sparql = sparql + "    OPTIONAL { _:%(dataset)s sdmx-measure:obsValue ?obsValue }\n" % args
        if useDics:
            sparql = sparql + "    OPTIONAL { _:%(dataset)s sdmx-attribute:comment ?comment }\n" % args
        else:
            sparql = sparql + "    OPTIONAL { _:%(dataset)s sdmx-attribute:comment ?comment }\n" % args
        sparql = sparql + "}\n"
        return sparql

    def startDim(self, tag, attrs):
	cat = attrs.get((None,'Category')).lower()
        code = attrs.get((None,'Code'))
        if cat == "year":
            self.rdfout.writeObjectProperty("sdmx-dimension:freq", "http://purl.org/linked-data/sdmx/2009/code#freq-A")
            self.writeTimePeriod("P1Y", code)
        elif cat == "gho":
            pass
        else:
            self.allDimensions[cat] = self.allDimensions.setdefault(cat,0) + 1
            self.dims[cat] = code

    def startObservation(self, tag, attrs):
        self.resetData()
        self.obsnum += 1
        self.dims = {}
        self.rdfout.writeStartResource("qb:Observation", "data/%s#O%d" % (self.dataset, self.obsnum))
        self.rdfout.writeObjectProperty("qb:dataSet", "data/%s" % self.dataset)

    def endObservation(self, tag):
        if self.obsNumeric:
            try:
                float(self.obsNumeric)
                self.rdfout.writeDataProperty("sdmx-measure:obsValue", self.obsNumeric, datatype="http://www.w3.org/2001/XMLSchema#decimal")
            except:
                self.rdfout.writeDataProperty("sdmx-measure:obsValue", self.obsNumeric)  # might have to do .encode('utf-8')
        elif self.displayText:
            self.rdfout.writeDataProperty("sdmx-measure:obsValue", self.displayText)  # might have to do .encode('utf-8')
        for k,v in self.dims.items():
            self.rdfout.writeObjectProperty(self.sdmxDimensions.get(k, 'property:'+k), "dic/%s#%s" % (k, v) )
        self.rdfout.writeEndResource("qb:Observation")

    def startValue(self, tag, attrs):
        """ Generate the observation record. Even when there is no obs_value, there can
            be a obs_status explaining why there is none.
        """
        self.obsNumeric = attrs.get((None,'Numeric'))

    def endComments(self, tag):
	self.rdfout.writeDataProperty("sdmx-attribute:comment", self.displayText)

    def startDisplay(self, tag, attrs):
        self.resetData()

    def endDisplay(self, tag):
	self.displayText = self.getData().strip().encode('utf-8')


def rdfFileTime(config, dataset):
    """ Returns the modification time of the rdf file or 0.0 if not present
    """
    website = config.get('destination', 'datafiles')
    filename = website + "/" + dataset + ".rdf.gz"
    try:
        mtime = os.stat(filename).st_mtime
    except:
        mtime = 0.0
    return mtime

def buildIfOlder(config, dataset, dsLabel):
    """ Compare the timestamp of the source and destination and build if
        destination is older
    """
    rdftime = rdfFileTime(config, dataset)
    repository = config.get('sources','xmlfiles')
    sdmxname = repository + "/" + dataset + ".xml"
    try:
        sdmxtime = os.stat(sdmxname).st_mtime
    except:
        logging.info("No such source: %s", dataset)
        return
    try:
        if rdftime < sdmxtime:
            createRdfFile(config, dataset, dsLabel)
        else:
            logging.debug("Destination is newer: %s", dataset)
    except xml.sax._exceptions.SAXParseException:
        pass


def createRdfFile(config, dataset, dsLabel):
    website = config.get('destination', 'datafiles')
    repository = config.get('sources','xmlfiles')

    logging.debug("Building: %s", dataset)
    try:
        parser = make_parser()
        parser.setFeature(handler.feature_namespaces, 1)
        filename = website + "/" + dataset + ".rdf.gz"
        filenameTmp = filename + "_tmp"
        rdfout = RdfDocument(config, filenameTmp)
        ch = DataConverter(dataset, config, rdfout, dsLabel)
        parser.setContentHandler(ch)
        parser.setErrorHandler(handler.ErrorHandler())

        datafd = open(repository + '/' + dataset + '.xml','rb')
        parser.parse(datafd)
        datafd.close()
        rdfout.close()
        try: os.unlink(filename)
        except: pass
        os.rename(filenameTmp, filename)
    except:
        if os.access(filenameTmp, os.R_OK): os.unlink(filenameTmp)
        raise


if __name__ == '__main__':
    import ConfigParser, getopt
    config = ConfigParser.SafeConfigParser()
    config.read('who.cfg')
    skipline = config.get('rdf','skip')
    skiplist = skipline.split()
    dsLabels = datasetLabels(config)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "v")
    except getopt.GetoptError, err:
        sys.exit(2)
    for o, a in opts:
        if o == "-v":
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    if len(args) == 0:
        for a,l in dsLabels.items():
            buildIt = True
            for skip in skiplist:
                if fnmatch.fnmatch(a, skip):
                    logging.debug("Skipping %s", a)
                    buildIt = False
                    break
            if buildIt:
                buildIfOlder(config, a, l)
    else:
        for a in args:
            if a[-9:] == '.xml': a = a[:-9]
            buildIfOlder(config, a, dsLabels.get(a))
