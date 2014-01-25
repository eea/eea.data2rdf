#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

import unittest, ConfigParser
from StringIO import StringIO
import tempfile, os, gzip
from xml.sax import make_parser, handler
import sdmx2rdf
from rdfdocument import RdfDocument

class TestSDMXConverter(unittest.TestCase):

#   def assertIn(self, substr, actual, message=None):
#       """ For Python pre 2.7 """
#       self.assertNotEqual(-1, actual.find(substr), message)

    def setUp(self):
        self.config = ConfigParser.SafeConfigParser()
        self.config.add_section('rdf')
        self.config.set('rdf', 'baseuri', 'http://baseuri/')
        self.config.set('rdf', 'vocabulary', 'http://vocabulary/')
        self.config.set('rdf', 'legacydicts','units   nace_r2 obs_status')
        self.config.add_section('sdmx')
        self.config.set('sdmx', 'data.ns','urn:sdmx:org.sdmx.infomodel.keyfamily.KeyFamily=EUROSTAT:%(dataset)s_DSD:compact')
        self.config.set('sdmx', 'message.ns', 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message')
        self.config.set('rdf', 'dimensiondict', 'dic/%(dimension)s#%(code)s')
        #self.config.set('rdf', 'dimensiondict', 'http://dd.eionet.europa.eu/vocabulary/eurostat/%(dimension)s/%(code)s')
        tmpOut, destFileName = tempfile.mkstemp('.rdf')
        os.close(tmpOut)
        self.destFileName = destFileName
        self.rdfout = RdfDocument(self.config, destFileName)
        parser = make_parser()
        parser.setFeature(handler.feature_namespaces, 1)

    def tearDown(self):
        os.unlink(self.destFileName)

    def readRdfDocument(self):
        """ Return the content of the written RDF document"""
        f = gzip.open(self.destFileName, 'rb')
        res = f.read()
        f.close()
        return res

    def testVocabularyRef(self):
        """ Test that vocabulary references return the correct value """
        self.config.set('rdf', 'dimensiondict', 'http://dd.eionet.europa.eu/vocabulary/eurostat/%(dimension)s/%(code)s')
        converter = sdmx2rdf.SDMXConverter("test", self.config, self.rdfout, "test label")
        result = converter.vocabularyReference("xx", "TOTAL")
        self.assertEquals("http://dd.eionet.europa.eu/vocabulary/eurostat/xx/TOTAL", result)

        result = converter.vocabularyReference("sex", "M")
        self.assertEquals("http://purl.org/linked-data/sdmx/2009/code#sex-M", result)

        result = converter.vocabularyReference("nace_r2", "01")
        self.assertEquals("dic/nace_r2#01", result)

        result = converter.vocabularyReference("obs_status", "M")
        self.assertEquals("dic/obs_status#M", result)

    def testPropertyElement(self):
        """ Test that the name of the property is correct """
        converter = sdmx2rdf.SDMXConverter("test", self.config, self.rdfout, "test label")
        result = converter.propertyElement("xx")
        self.assertEquals("property:xx", result)

        result = converter.propertyElement("sex")
        self.assertEquals("sdmx-dimension:sex", result)

        result = converter.propertyElement("geo")
        self.assertEquals("sdmx-dimension:refArea", result)

    def testStartObs1(self):
        """ Test that an observation is converted correctly
        """
        converter = sdmx2rdf.SDMXConverter("test", self.config, self.rdfout, "test label")
        converter.startSeries('Series', {(None,'FREQ'): 'A',
                (None, 'indic_mx'): 'G25601',
                (None, 'geo'): 'IL',
                (None,'TIME_FORMAT'): 'P1Y' })
        converter.startObs('Obs', {(None,'TIME_PERIOD'): '2008',
                (None,'OBS_VALUE'): '4.5998', (None,'OBS_STATUS'): 'e' })

        self.rdfout.writeFinish()
        res = self.readRdfDocument()
        self.assertIn("""<sdmx-dimension:timePeriod rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-01</sdmx-dimension:timePeriod>""", res)
        self.assertIn("""<sdmx-measure:obsValue rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">4.5998</sdmx-measure:obsValue>""", res)
        self.assertIn("""<sdmx-attribute:obsStatus rdf:resource="dic/obs_status#e"/>""", res)
        self.assertIn("""<property:indic_mx rdf:resource="dic/indic_mx#G25601"/>""", res)
        #self.assertIn("""<property:indic_mx rdf:resource="http://dd.eionet.europa.eu/vocabulary/eurostat/indic_mx/G25601"/>""", res)
        self.assertIn("""<sdmx-dimension:freq rdf:resource="http://purl.org/linked-data/sdmx/2009/code#freq-A"/>""", res)
        self.assertIn("""<property:geo rdf:resource="dic/geo#IL"/>""", res)
        self.assertIn("""<sdmx-dimension:refArea rdf:resource="dic/geo#IL"/>""", res)
        #print res

    def testStartObsNewDicts(self):
        """ Test that an observation is converted correctly with new dictionaries
        """
        self.config.set('rdf', 'dimensiondict', 'http://dd.eionet.europa.eu/vocabulary/eurostat/%(dimension)s/%(code)s')

        converter = sdmx2rdf.SDMXConverter("test", self.config, self.rdfout, "test label")
        converter.startSeries('Series', {(None,'FREQ'): 'A',
                (None, 'indic_mx'): 'G25601',
                (None, 'geo'): 'IL',
                (None,'TIME_FORMAT'): 'P1Y' })
        converter.startObs('Obs', {(None,'TIME_PERIOD'): '2008',
                (None,'OBS_VALUE'): '4.5998', (None,'OBS_STATUS'): 'e' })

        self.rdfout.writeFinish()
        res = self.readRdfDocument()
        self.assertIn("""<sdmx-dimension:timePeriod rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-01</sdmx-dimension:timePeriod>""", res)
        self.assertIn("""<sdmx-measure:obsValue rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">4.5998</sdmx-measure:obsValue>""", res)
        self.assertIn("""<sdmx-attribute:obsStatus rdf:resource="dic/obs_status#e"/>""", res)
        self.assertIn("""<property:indic_mx rdf:resource="http://dd.eionet.europa.eu/vocabulary/eurostat/indic_mx/G25601"/>""", res)
        self.assertIn("""<sdmx-dimension:freq rdf:resource="http://purl.org/linked-data/sdmx/2009/code#freq-A"/>""", res)
        self.assertIn("""<property:geo rdf:resource="dic/geo#IL"/>""", res)
        self.assertIn("""<sdmx-dimension:refArea rdf:resource="dic/geo#IL"/>""", res)
        #print res

    def testWriteTime(self):
        converter = sdmx2rdf.SDMXConverter("test", self.config, self.rdfout, "test label")
        timeValue, timeType = converter.getTimePeriod("","TARGET")
        self.assertEquals("TARGET", timeValue)
        self.assertEquals("", timeType)
        timeValue, timeType = converter.getTimePeriod("P1Y","2013")
        self.assertEquals("2013-01-01", timeValue)
        self.assertEquals("http://www.w3.org/2001/XMLSchema#date", timeType)

if __name__ == '__main__': 
    unittest.main() 
