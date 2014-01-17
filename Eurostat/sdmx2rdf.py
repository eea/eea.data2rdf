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
import sys, time, zipfile, gzip, os, logging
from rdfdocument import RdfDocument
import codecs, csv, fnmatch
import urllib

#
# Parse the SDMX files
#
class SDMXConverter(handler.ContentHandler):
    """ Extract observations from an SDMX file and write RDF
    """

    # Common dimensions from http://purl.org/linked-data/sdmx/2009/dimension
    # Would also require usage of common vocabularies
    sdmxDimensions = {
        'age': 'sdmx-dimension:age',
        'CIVIL_STATUS': 'sdmx-dimension:civilStatus',
        'CURRENCY': 'sdmx-dimension:currency',
        'decimals': 'sdmx-attribute:decimals',
        'EDUCATION_LEV': 'sdmx-dimension:educationLev',
        'FREQ': 'sdmx-dimension:freq',
        'geo': 'sdmx-dimension:refArea',
        'X-OBS_STATUS': 'sdmx-attribute:obsStatus',
        'occup': 'sdmx-dimension:occupation',
        'X-REF_PERIOD': 'sdmx-dimension:refPeriod',
        'sex': 'sdmx-dimension:sex',
        'X-TIME_PERIOD': 'sdmx-dimension:timePeriod',
        'unit': 'sdmx-attribute:unitMeasure'
    }
    sdmxCommonVocs = {
        'FREQ': 'http://purl.org/linked-data/sdmx/2009/code#freq-',
        'decimals': 'http://purl.org/linked-data/sdmx/2009/code#decimals-',
        'X-OBS_STATUS': 'http://purl.org/linked-data/sdmx/2009/code#obsStatus-',
        'sex': 'http://purl.org/linked-data/sdmx/2009/code#sex-',
        'geo': 'dic/geo#'
    }

    def __init__(self, dataset, config, rdfout, dsLabel):
        self.dataset = dataset
        self.rdfout = rdfout
        self.dsLabel = dsLabel
        self.baseuri = config.get('rdf', 'baseuri')
        self.vocabulary = config.get('rdf', 'vocabulary')
        legacyDictline = config.get('rdf','legacydicts')
        self.legacyDicts = legacyDictline.split()
        self.dictUrl = config.get('rdf', 'dimensiondict', True)
        self.data = []
        self.level = 0
        self.seriesAttrs = {}
        self.objUri = ""
        self._dimensionsChange = False
        self.dimLst = ""
        self.allDimensions = {}
        self.obsnum = 0
        self.timeOfRun = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.dataNS = config.get('sdmx', 'data.ns', False, {'dataset': dataset})
        self.messageNS = config.get('sdmx', 'message.ns', False, {'dataset': dataset})

        self.elements = {
            (self.messageNS,'Header'): (self.startHeader, self.endHeader),
            (self.messageNS,'Extracted'): (self.startExtracted, self.endExtracted),
            (self.messageNS,'CompactData'): (self.startCompactData, self.endCompactData),
            (self.dataNS,'Series'): (self.startSeries, self.endSeries),
            (self.dataNS,'Obs'): (self.startObs, None)
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
	""" Creates a date from the time period in the SDMX data
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


    def startHeader(self, tag, attrs):
        self.resetData()

    def endHeader(self, tag):
        self.rdfout.writeStartResource("qb:DataSet", "data/%s" % self.dataset)
        if self.dsLabel:
            self.rdfout.writeDataProperty("rdfs:label", self.dsLabel.encode('utf-8'))
        self.rdfout.writeObjectProperty("rdfs:seeAlso", "http://epp.eurostat.ec.europa.eu/portal/page/portal/about_eurostat/policies/copyright_licence_policy")
        self.rdfout.writeObjectProperty("rdfs:seeAlso", self.baseuri)
        self.rdfout.writeDataProperty("dcterms:modified", self.modified, datatype="http://www.w3.org/2001/XMLSchema#dateTime")
        self.rdfout.writeObjectProperty("dcterms:source", "http://epp.eurostat.ec.europa.eu/NavTree_prod/everybody/BulkDownloadListing?file=data%%2F%s.sdmx.zip" % self.dataset)
        self.rdfout.writeObjectProperty("cr:hasSparqlBookmark","data/%s#sparqlSimple" % self.dataset)
        self.rdfout.writeObjectProperty("cr:hasSparqlBookmark","data/%s#sparqlJoined" % self.dataset)
        #self.rdfout.writeObjectProperty("qb:structure", "dsd/%s" % self.dataset)
        self.rdfout.writeEndResource("qb:DataSet")

    def startExtracted(self, tag, attrs):
        self.resetData()

    def endExtracted(self, tag):
        self.modified = self.getData()

    def startCompactData(self, tag, attrs):
        self.rdfout.addNamespace("property", self.vocabulary)
        self.rdfout.addNamespace("qb", "http://purl.org/linked-data/cube#")
        self.rdfout.addNamespace("sdmx-measure", "http://purl.org/linked-data/sdmx/2009/measure#")
        self.rdfout.addNamespace("sdmx-dimension", "http://purl.org/linked-data/sdmx/2009/dimension#")
        self.rdfout.addNamespace("sdmx-attribute", "http://purl.org/linked-data/sdmx/2009/attribute#")
        self.rdfout.addNamespace("cr","http://cr.eionet.europa.eu/ontologies/contreg.rdf#")
        self.rdfout.addNamespace("dc", "http://purl.org/dc/elements/1.1/") # Only for the bookmark
        self.rdfout.writeHeader(self.baseuri)
        self.rdfout.writeProvenance("data/%s.rdf.gz" % self.dataset, "data/%s.sdmx.zip" % self.dataset)


    def endCompactData(self, tag):
        self.rdfout.writeStartResource("rdf:Description", "data/%s.rdf.gz" % self.dataset)
        self.rdfout.writeObjectProperty("foaf:primaryTopic", "data/" + self.dataset)
        self.rdfout.writeObjectProperty("cr:hasSparqlBookmark","data/%s#sparqlSimple" % self.dataset)
        self.rdfout.writeObjectProperty("cr:hasSparqlBookmark","data/%s#sparqlJoined" % self.dataset)
        self.rdfout.writeObjectProperty("dcterms:requires", "http://purl.org/linked-data/sdmx/2009/code")
        self.rdfout.writeObjectProperty("dcterms:requires", "dic/obs_status.rdf")
        for p in self.allDimensions.keys():
            if p.lower() == p:
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
        if useDics:
            if self._dimensionsChange:
                template = "    OPTIONAL { _:%(dataset)s %(predicate)s _:%(property)s . _:%(property)s skos:notation ?%(property)s }\n"
            else:
                template = "    _:%(dataset)s %(predicate)s _:%(property)s . _:%(property)s skos:notation ?%(property)s .\n"
        else:
            if self._dimensionsChange:
                template = "    OPTIONAL { _:%(dataset)s %(predicate)s ?%(property)s }\n"
            else:
                template = "    _:%(dataset)s %(predicate)s ?%(property)s .\n"
        for p in self.allDimensions.keys():
            if p.lower() == p:
                sparql = sparql + template % {'dataset': self.dataset, 'property': p, 'predicate': self.sdmxDimensions.get(p, 'property:'+p)}
        sparql = sparql + "    OPTIONAL { _:%(dataset)s sdmx-measure:obsValue ?obsValue }\n" % args
        if useDics:
            sparql = sparql + "    OPTIONAL { _:%(dataset)s sdmx-attribute:obsStatus _:obsStatus . _:obsStatus skos:prefLabel ?obsStatus }\n" % args
        else:
            sparql = sparql + "    OPTIONAL { _:%(dataset)s sdmx-attribute:obsStatus ?obsStatus }\n" % args
        sparql = sparql + "}\n"
        return sparql

    def startSeries(self, tag, attrs):
        self.resetData()
        self.seriesAttrs = {}
        self.seriesAttrs = attrs
        self.timeFormat = attrs.get((None,'TIME_FORMAT'))
        keys = attrs.keys()
        keys.sort()
        dimValues = ""
        dims = ""
        for k in keys:
            if k not in ((None,'TIME_FORMAT'), ):
                self.allDimensions[k[1]] = 1        # Register all attributes for SPARQL
		dims = dims + k[1] + ','
                dimValues = dimValues + attrs[k] + ','
        if self.dimLst != "" and self.dimLst != dims: # Check if the dimensions change in the file
            self._dimensionsChange = True
        self.objUri = dimValues
	self.dimLst = dims

    def endSeries(self, tag):
        self.timeFormat = None

    def startObs(self, tag, attrs):
        """ Generate the observation record. Even when there is no obs_value, there can
            be a obs_status explaining why there is none.
        """
        timePeriod = attrs[(None,'TIME_PERIOD')]
        obsStatus = attrs.get((None,'OBS_STATUS'), None)
        self.rdfout.writeStartResource("qb:Observation", "data/%s#%s%s" % (self.dataset, self.objUri, timePeriod))
        self.rdfout.writeObjectProperty("qb:dataSet", "data/%s" % self.dataset)
        #self.rdfout.writeObjectProperty("sdmx-dimension:freq", "http://purl.org/linked-data/sdmx/2009/code#freq-%s" % self.seriesAttrs[(None,'FREQ')])
        self.writeTimePeriod(self.timeFormat, timePeriod)
        obsValue = attrs.get((None,'OBS_VALUE'))
        if obsValue:
            try:
                float(obsValue)
                self.rdfout.writeDataProperty("sdmx-measure:obsValue", obsValue, datatype="http://www.w3.org/2001/XMLSchema#decimal")
            except:
                self.rdfout.writeDataProperty("sdmx-measure:obsValue", obsValue)  # might have to do .encode('utf-8')

        if obsStatus:
            self.rdfout.writeObjectProperty("sdmx-attribute:obsStatus", self.vocabularyReference("obs_status", obsStatus))
        for k,v in self.seriesAttrs.items():
            loc_k = k[1]
            if loc_k.lower() == loc_k:
                self.rdfout.writeObjectProperty("property:" + loc_k, self.vocabularyReference(loc_k , v))
            if self.sdmxDimensions.get(loc_k):
                self.rdfout.writeObjectProperty(self.sdmxDimensions.get(loc_k), self.vocabularyReference(loc_k, v))
        self.rdfout.writeEndResource("qb:Observation")
        self.obsnum += 1

    def propertyElement(self, dimension):
        if self.sdmxDimensions.get(dimension):
            return self.sdmxDimensions.get(dimension)
        else:
            return "property:" + dimension

    def vocabularyReference(self, dictionary, code):
        """ Chooses the correct vocabulary for the code of the dictionary
        """
        if self.sdmxCommonVocs.get(dictionary):
             return self.sdmxCommonVocs.get(dictionary) + code
        if dictionary in self.legacyDicts:
            return "dic/%(dimension)s#%(code)s" % {'dimension':dictionary, 'code':code }
        else:
            return self.dictUrl % {'dimension':dictionary, 'code':code }


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
    repository = config.get('sources','sdmxfiles')
    sdmxname = repository + "/" + dataset + ".sdmx.zip"
    try:
        sdmxtime = os.stat(sdmxname).st_mtime
    except:
        logging.debug("No such source: %s", dataset)
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
    repository = config.get('sources','sdmxfiles')

    logging.debug("Building: %s", dataset)
    try:
        parser = make_parser()
        parser.setFeature(handler.feature_namespaces, 1)
        filename = website + "/" + dataset + ".rdf.gz"
        filenameTmp = filename + "_tmp"
        rdfout = RdfDocument(config, filenameTmp)
        ch = SDMXConverter(dataset, config, rdfout, dsLabel)
        parser.setContentHandler(ch)
        parser.setErrorHandler(handler.ErrorHandler())

        zfd = zipfile.ZipFile(repository + "/" + dataset + ".sdmx.zip")
        datafd = StringIO(zfd.read(dataset + ".sdmx.xml"))
        parser.parse(datafd)
        datafd.close()
        zfd.close()
        rdfout.close()
        try: os.unlink(filename)
        except: pass
        os.rename(filenameTmp, filename)
        #pingDatabases(config, dataset)
    except:
        if os.access(filenameTmp, os.R_OK): os.unlink(filenameTmp)
        raise

def pingDatabases(config, dataset):
    """ Sends a request to data stores as a signal to get them to reharvest
        the new RDF data.
    """
    baseuri = config.get('rdf', 'baseuri')
    urls = config.get('ping', 'stores', {'dataset': dataset, 'baseuri': baseuri})
    urllist = urls.split()
    for link in urllist:
        f = urllib.urlopen(link)
        f.read()
        f.close()

def loadDatasetLabels():
    """ Read the dataset titles from the downloaded all_dic.zip
        The titles are in the file en/table_dic.dic
        The file is not complete
    """
    datasets = {}
    zfd = zipfile.ZipFile("all_dic.zip")
    winfile = StringIO(zfd.read("en/table_dic.dic"))
    tsvfile = codecs.EncodedFile(winfile, "utf-8", "cp1252")
    reader = csv.reader(tsvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        if len(row) == 0: continue    # Found an empty line
        code = row[0].lower().strip()
        if code == "": continue       # Found an empty code
        datasets[code] = row[1].strip()
    tsvfile.close()
    zfd.close()
    return datasets

if __name__ == '__main__':
    import ConfigParser, getopt
    from toclabels import datasetLabels
    config = ConfigParser.SafeConfigParser()
    config.read('eurostat.cfg')
    skipline = config.get('rdf','skip')
    skiplist = skipline.split()
    #dsLabels = loadDatasetLabels()
    dsLabels = datasetLabels()

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
            if a[-9:] == '.sdmx.zip': a = a[:-9]
            buildIfOlder(config, a, dsLabels.get(a))
