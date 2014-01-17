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

import csv, codecs, sys, os
import urllib, logging
import zipfile, time
from cStringIO import StringIO
from rdfdocument import RdfDocument


class DicReader(object):

    def __init__(self, dataset, tsvfile, config, rdfout):
        """ dataset is the name of the dataset
            datastream expects a file descriptor with the content in UTF-8 encoding
        """
        self.dataset = dataset
        self.baseuri = config.get('rdf', 'baseuri')
        self.rdfout = rdfout
        self.timeOfRun = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.topconcepts = []
        reader = csv.reader(tsvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
        self.rdfout.writeHeader(self.baseuri)
        self.rdfout.writeProvenance("dic/%s.rdf" % self.dataset, "dic/en/%s.dic" % self.dataset)
        for row in reader:
            if len(row) == 0: continue    # Found an empty line
            code = row[0].strip()
            if code == "": continue       # Found an empty code
            self.topconcepts.append(code)
            self.rdfout.writeStartResource("skos:Concept", "dic/%s#%s"  % (dataset, code))
            self.rdfout.writeObjectProperty('skos:inScheme','dic/%s' % dataset)
            self.rdfout.writeDataProperty('skos:prefLabel', row[1].strip(), lang="en")
            self.rdfout.writeDataProperty('skos:notation', code)
            self.rdfout.writeEndResource("skos:Concept")

        self.rdfout.writeStartResource('skos:ConceptScheme', "dic/%s" % dataset)
        for code in self.topconcepts:
            self.rdfout.writeObjectProperty('skos:hasTopConcept', 'dic/%s#%s'  % (dataset, code))
        self.rdfout.writeDataProperty('skos:notation', dataset)
        self.rdfout.writeEndResource('skos:ConceptScheme')
        self.rdfout.writeFinish()


if __name__ == '__main__':
    import ConfigParser, getopt
    config = ConfigParser.SafeConfigParser()
    config.read('eurostat.cfg')
    website = config.get('destination', 'vocabularies')
    retrieveDic = config.getboolean('download','dic')
    dicUrl = config.get('download','dicurl')

    try:
        opts, args = getopt.getopt(sys.argv[1:], "v")
    except getopt.GetoptError, err:
        sys.exit(2)
    for o, a in opts:
        if o == "-v":
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    # Grab all_dic.zip
    if retrieveDic:
        logging.info("Downloading dictionaries")
        urllib.urlretrieve(dicUrl, 'all_dic.zip')

    zfd = zipfile.ZipFile("all_dic.zip")
    if len(args) == 0:
        for zi in zfd.infolist():
            name = zi.filename
            if name[-1] == "/": continue   # Found a folder
            if name == "en/dimlst.dic": continue   # (List of dimensions)
            if name == "en/table_dic.dic": continue   # (List of datasets)
            if name[:3] == "en/":
                code = name[3:-4]
                rdfFileName = website + "/" + code + ".rdf"
                try: lastRun = os.stat(rdfFileName).st_mtime
                except: lastRun = 0.0
                buildTime = time.mktime(zi.date_time + (0,1,-1))
                if buildTime < lastRun:
                    logging.debug("%s newer than %s", rdfFileName, time.strftime("%Y-%m-%d", time.localtime(buildTime)))
                    continue
                logging.debug("Building %s", code)
                winfile = StringIO(zfd.read(name))
                tsvfile = codecs.EncodedFile(winfile, "utf-8", "cp1252")
                rdfout = RdfDocument(config, rdfFileName, False)
                DicReader(code, tsvfile, config, rdfout)
                winfile.close()
    else:
        for code in args:
            logging.debug("Building %s", code)
            winfile = StringIO(zfd.read("en/%s.dic" % code))
            tsvfile = codecs.EncodedFile(winfile, "utf-8", "cp1252")
            rdfFileName = website + "/" + code + ".rdf"
            rdfout = RdfDocument(config, rdfFileName, False)
            DicReader(code, tsvfile, config, rdfout)
            winfile.close()
    zfd.close()
