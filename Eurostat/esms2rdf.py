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
import time, urllib, os, zipfile, logging
import rdfdocument
import re

NTNS="urn:eu.europa.ec.eurostat.navtree"
GENERICNS = "http://www.SDMX.org/resources/SDMXML/schemas/v2_0/genericmetadata"


#
# Parse the XML files
#
class ESMSParser(handler.ContentHandler):
    """ """

    # Attribute names that defined in http://purl.org/linked-data/sdmx/2009/attribute
    sdmxAttributes = {
        'ACCESSIBILITY': 'accessibility',
        'ACCURACY': 'accuracy',
        'ACCURACY_OVERALL': 'accuracyOverall',
        'ADJUSTMENT': 'adjustment',
        'ADJUST_CODED': 'adjustCoded',
        'ADJUST_DETAIL': 'adjustDetail',
        'ADV_NOTICE': 'advNotice',
        'BASE_PER': 'basePer',
        'CLARITY': 'clarity',
        'CLASS_SYSTEM': 'classSystem',
        'COHERENCE': 'coherence',
        'COHER_INTERNAL': 'coherInternal',
        'COHER_X_DOM': 'coherXDom',
        'COLL_METHOD': 'collMethod',
        'COMMENT':'comment',
        'COMPARABILITY': 'comparability',
        'COMPAR_DOMAINS': 'comparDomains',
        'COMPAR_GEO': 'comparGeo',
        'COMPAR_TIME': 'comparTime',
        'COMPILING_ORG': 'compilingOrg',
        'COMPLETENESS': 'completeness',
        'CONF': 'conf',
        'CONF_DATA_TR': 'confDataTr',
        'CONF_POLICY': 'confPolicy',
        'CONF_STATUS': 'confStatus',
        'CONTACT': 'contact',
        'CONTACT_EMAIL': 'contactEmail',
        'CONTACT_FAX': 'contactFax',
        'CONTACT_FUNCT': 'contactFunct',
        'CONTACT_MAIL': 'contactMail',
        'CONTACT_NAME': 'contactName',
        'CONTACT_ORGANISATION': 'contactOrganisation',
        'CONTACT_PHONE': 'contactPhone',
        'COST_BURDEN': 'costBurden',
        'COST_BURDEN_EFF': 'costBurdenEff',
        'COST_BURDEN_RES': 'costBurdenRes',
        'COVERAGE': 'coverage',
        'COVERAGE_SECTOR': 'coverageSector',
        'COVERAGE_TIME': 'coverageTime',
        'CURRENCY': 'currency',
        'DATA_COMP': 'dataComp',
        'DATA_DESCR': 'dataDescr',
        'DATA_EDITING': 'dataEditing',
        'DATA_PRES': 'dataPres',
        'DATA_PROVIDER': 'dataProvider',
        'DATA_REV': 'dataRev',
        'DATA_UPDATE': 'dataUpdate',
        'DATA_VALIDATION': 'dataValidation',
        'DATA_VAL_INTER': 'dataValInter',
        'DATA_VAL_OUTPUT': 'dataValOutput',
        'DATA_VAL_SOURCE': 'dataValSource',
        'DECIMALS': 'decimals',
        'DISS_DET': 'dissDet',
        'DISS_FORMAT': 'dissFormat',
        'DISS_ORG': 'dissOrg',
        'DISS_OTHER': 'dissOther',
        'DOC_METHOD': 'docMethod',
        'DSI': 'dsi',
        'EMBARGO_TIME': 'embargoTime',
        'FREQ_COLL': 'freqColl',
        'FREQ_DETAIL': 'freqDetail',
        'FREQ_DISS': 'freqDiss',
        'GROSS_NET': 'grossNet',
        'I_M_RES_REL': 'iMResRel',
        'IND_TYPE': 'indType',
        'INST_MANDATE': 'instMandate',
        'INST_MAN_LA_OA': 'instManLaOa',
        'INST_MAN_SHAR': 'instManShar',
        'M_AGENCY': 'mAgency',
        'META_CERTIFIED': 'metaCertified',
        'META_LAST_UPDATE': 'metaLastUpdate',
        'META_POSTED': 'metaPosted',
        'META_UPDATE': 'metaUpdate',
        'MICRO_DAT_ACC': 'microDatAcc',
        'NEWS_REL': 'newsRel',
        'NONSAMPLING_ERR': 'nonsamplingErr',
        'OBS_PRE_BREAK': 'obsPreBreak',
        'OBS_STATUS': 'obsStatus',
        'ONLINE_DB': 'onlineDb',
        'ORGANISATION_UNIT': 'organisationUnit',
        'ORIG_DATA_ID': 'origDataId',
        'PROF': 'prof',
        'PROF_COND': 'profCond',
        'PROF_IMP': 'profImp',
        'PROF_METH': 'profMeth',
        'PROF_STAT_COM': 'profStatCom',
        'PUBLICATIONS': 'publications',
        'PUNCTUALITY': 'punctuality',
        'QUALITY_ASSMNT': 'qualityAssmnt',
        'QUALITY_ASSURE': 'qualityAssure',
        'QUALITY_DOC': 'qualityDoc',
        'QUALITY_MGMNT': 'qualityMgmnt',
        'RECORDING': 'recording',
        'REF_PER_WGTS': 'refPerWgts',
        'REL_CAL_ACCESS': 'relCalAccess',
        'REL_CAL_POLICY': 'relCalPolicy',
        'REL_COMMENT': 'relComment',
        'RELEVANCE': 'relevance',
        'REL_POLICY': 'relPolicy',
        'REL_POL_LEG_ACTS': 'relPolLegActs',
        'REL_POL_TRA': 'relPolTra',
        'REL_POL_US_AC': 'relPolUsAc',
        'REP_AGENCY': 'repAgency',
        'REV_POLICY': 'revPolicy',
        'REV_PRACTICE': 'revPractice',
        'REV_STUDY': 'revStudy',
        'SAMPLING': 'sampling',
        'SAMPLING_ERR': 'samplingErr',
        'SOURCE_TYPE': 'sourceType',
        'STAT_CONC_DEF': 'statConcDef',
        'STAT_POP': 'statPop',
        'STAT_UNIT': 'statUnit',
        'TIME_FORMAT': 'timeFormat',
        'TIMELINESS': 'timeliness',
        'TIME_OUTPUT': 'timeOutput',
        'TIME_PER_COLLECT': 'timePerCollect',
        'TIME_SOURCE': 'timeSource',
        'TITLE': 'title',
        'UNIT_MEASURE': 'unitMeasure',
        'UNIT_MEAS_DETAIL': 'unitMeasDetail',
        'UNIT_MULT': 'unitMult',
        'USER_NEEDS': 'userNeeds',
        'USER_SAT': 'userSat',
        'VALUATION': 'valuation',
        'VIS_AREA': 'visArea',
    }

    def __init__(self, website, dataset, rdfout):
        self._name = dataset
        self.data = []
        self.concepts = {}
        self.rdfout = rdfout
        self.elements = {
            (GENERICNS,'ReportedAttribute'): (self.startReportedAttribute, self.endReportedAttribute),
            (GENERICNS,'MetadataSet'): (self.startMetadataSet, None),
            (GENERICNS,'Value'): (self.startValue, self.endValue),
            (GENERICNS,'AttributeValueSet'): (self.startMetadataRec, self.endMetadataRec),
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


    def startMetadataSet(self, tag, attrs):
        self.resetData()

#   def endMetadataSet(self, tag):
#       pass

    def startReportedAttribute(self, tag, attrs):
        self.resetData()
        self._notation = attrs.get((None,'conceptID'))
        self._notation = self._notation.lower()

    def endReportedAttribute(self, tag):
        val =  self.getData()
        self.resetData()


    def startMetadataRec(self, tag, attrs):
        self.resetData()
        self.rdfout.writeStartResource("ESMSMetadata", "#" + self._name)

    def endMetadataRec(self, tag):
        self.rdfout.writeEndResource("ESMSMetadata")
        self.resetData()

    def startValue(self, tag, attrs):
        self.resetData()

    def endValue(self, tag):
        self._value = self.getData()
        if self._value != '':
            v = re.sub('<[^<]+?>', '', self._value)   # Get rid of HTML tags
            self.rdfout.writeDataProperty(self._notation.encode('utf-8'), v.encode('utf-8'))
        self.resetData()


def createESMSRdf(config):
    website = config.get('destination', 'metadata')
    sources = config.get('sources', 'esmsfiles')

    rdfout = rdfdocument.RdfDocument(config, '%s/esms.rdf' % website, False)
    rdfout.addNamespace("", "http://purl.org/linked-data/sdmx/2009/attribute#")
    rdfout.addNamespace("x", "http://rdfdata.eionet.europa.eu/eurostat/esmsschema.rdf#")
    rdfout.writeHeader()
    rdfout.writeProvenance("", "metadata")
    for f in os.listdir(sources):
        logging.debug("Building %s", f)
        dataset = f[:-9]
        try:
            zfd = zipfile.ZipFile(sources + "/" + f)
            for name in zfd.namelist():
                if name.startswith(dataset) and name[len(dataset):len(dataset)+5] == ".sdmx":
                    zdata = StringIO(zfd.read(name))
                    parser = make_parser()
                    parser.setFeature(handler.feature_namespaces, 1)
                    ch = ESMSParser(website, f[:-9], rdfout)
                    parser.setContentHandler(ch)
                    parser.setErrorHandler(handler.ErrorHandler())
                    parser.parse(zdata)
                    zdata.close()
                    zfd.close()
                    break
            else:
                raise RuntimeError, "ESMS member not found in zip archive"
        except:
            logging.error("Failed to build %s", f)
    rdfout.writeFinish()


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

    createESMSRdf(config)
