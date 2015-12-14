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

import MySQLdb
import csv, codecs, sys, os
import urllib, logging
import zipfile, time
from cStringIO import StringIO

INVALID = 113
VALID = 145
DEPRECATED = 161
DEPRECATED_RETIRED = 163

def q(s):
    return s.replace("'","''")


class DD(object):

    db_connection = None

    def __init__(self, config):
        self.config = config
        self.vocnames = {}
        dbuser = config.get('database', 'user')
        dbpass = config.get('database', 'password')
        dbdb = config.get('database', 'database')
        self.eurostatId = config.getint('vocabularies','set')
        
        self.db_connection = MySQLdb.connect('localhost', dbuser, dbpass, dbdb, connect_timeout = 30, charset = "utf8")
        self.cursor = self.db_connection.cursor
        self.commit = self.db_connection.commit

    def close(self):
        self.db_connection.close()
        self.db_connection = None

    def createVoc(self, code, modifyDate):
        """ Look in the database for the vocabulary under the 'eurostat' set
            If it is not there then create it.
        """
        label = self.vocnames.get(code, 'Description missing in source')
        cursor = self.cursor()
        cursor.execute("""SELECT VOCABULARY_ID FROM VOCABULARY WHERE IDENTIFIER=%s AND FOLDER_ID=%s""", (code, self.eurostatId))
        if cursor.rowcount == 0:
            logging.debug("Creating vocabulary %s" % code)
            cursor.execute("""INSERT INTO VOCABULARY (CONTINUITY_ID, IDENTIFIER, LABEL, REG_STATUS, FOLDER_ID, NOTATIONS_EQUAL_IDENTIFIERS, DATE_MODIFIED, USER_MODIFIED, BASE_URI) VALUES (UUID(), %s, %s, 'Released', %s, 1, %s, 'system', CONCAT('http://dd.eionet.europa.eu/vocabulary/eurostat/', %s, '/')) """, (code, label, self.eurostatId, modifyDate, code))
            self.commit()
        elif cursor.rowcount == 1:
            cursor.execute("""UPDATE VOCABULARY set LABEL=%s, DATE_MODIFIED=%s,USER_MODIFIED='system' WHERE IDENTIFIER=%s AND FOLDER_ID=%s""", (label, modifyDate, code, self.eurostatId))
            self.commit()
        else:
            raise AssertionError, "Found more than one ID"
        cursor.execute("""SELECT VOCABULARY_ID FROM VOCABULARY WHERE IDENTIFIER=%s AND FOLDER_ID=%s""", (code, self.eurostatId))
        row = cursor.fetchone()
        vocId = row[0]
        # Add source statement
        # FIXME: Only for new vocabularies
        #cursor.execute("""INSERT INTO ATTRIBUTE VALUES (59, %s, concat('Original source from Eurostat at http://epp.eurostat.ec.europa.eu/NavTree_prod/everybody/BulkDownloadListing?file=dic/en/', %s,'.dic'),'VCF')""", (vocId, code))
        return vocId

    def recordVocabularies(self):
        dimLstFN = "en/dimlst.dic"
        zfd = zipfile.ZipFile("all_dic.zip")
        winfile = StringIO(zfd.read(dimLstFN))
        tsvfile = codecs.EncodedFile(winfile, "utf-8", "cp1252")
        reader = csv.reader(tsvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
        for row in reader:
            if len(row) == 0: continue    # Found an empty line
            code = row[0].lower().strip()
            if code == "": continue       # Found an empty code
            label = row[1].strip()
            if label == '': label = 'Description missing in source'
            self.vocnames[code] = label
        tsvfile.close()
        zfd.close()
        # Special cases
        self.vocnames['cities'] = 'Urban audit cities'

    def getExistingConcepts(self, vocabulary):
        """ Get existing concepts as a dictionary """
        existingCodes = {}
        cursor = self.cursor()
        cursor.execute("""SELECT C.IDENTIFIER, C.VOCABULARY_CONCEPT_ID, C.LABEL FROM VOCABULARY_CONCEPT AS C JOIN VOCABULARY AS V USING(VOCABULARY_ID) WHERE V.IDENTIFIER=%s AND FOLDER_ID=%s""", (vocabulary, self.eurostatId))
        row = cursor.fetchone()
        while row:
            existingCodes[row[0]] = [ int(row[1]), row[2] ]
            row = cursor.fetchone()
        return existingCodes

    def addConcepts(self, vocabulary, tsvfile, config, modifyDate):
        """ vocabulary is the name of the vocabulary
            datastream expects a file descriptor with the content in UTF-8 encoding
        """
        newCodes = {}
        existingCodes = self.getExistingConcepts(vocabulary)

        cursor = self.cursor()
        
        reader = csv.reader(tsvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
        for row in reader:
            if len(row) == 0: continue    # Found an empty line
            code = row[0].strip()
            prefLabel = unicode(row[1].strip(), 'utf-8')
            if code == "": continue       # Found an empty code
            newCodes[code] = 1
            conceptId, currLabel = existingCodes.get(code, (None, None))
            if conceptId:
                if currLabel != prefLabel:
                    logging.debug("Update: %s %d %s %s" % (vocabulary, conceptId, code, prefLabel))
                    cursor.execute(u"""UPDATE VOCABULARY_CONCEPT SET LABEL=%s, STATUS=145 WHERE VOCABULARY_CONCEPT_ID=%s""", (prefLabel, conceptId))
            else:
                logging.debug("Insert: %s %s %s" % (vocabulary, code, prefLabel))
                cursor.execute(u"""INSERT INTO VOCABULARY_CONCEPT (VOCABULARY_CONCEPT_ID, VOCABULARY_ID, IDENTIFIER, LABEL, DEFINITION, NOTATION, ORIGINAL_CONCEPT_ID, STATUS, STATUS_MODIFIED, ACCEPTED_DATE, NOT_ACCEPTED_DATE) SELECT NULL, VOCABULARY_ID, %s,%s,'',%s,NULL,145, %s, %s, NULL FROM VOCABULARY WHERE IDENTIFIER=%s AND FOLDER_ID=%s""", (code, prefLabel, code, modifyDate, modifyDate, vocabulary, self.eurostatId))
        # Retire old codes
        for oldCode, oldVals in existingCodes.items():
            if oldCode not in newCodes:
                conceptId = oldVals[0]
                oldLabel = oldVals[1]
                logging.debug("Invalidating: %s %d %s %s" % (vocabulary, conceptId, oldCode, oldLabel))
                cursor.execute(u"""UPDATE VOCABULARY_CONCEPT SET STATUS=113, NOT_ACCEPTED_DATE=%s, STATUS_MODIFIED=%s WHERE VOCABULARY_CONCEPT_ID=%s AND STATUS>=128""", (modifyDate, modifyDate, conceptId))
        self.commit()

if __name__ == '__main__':
    import ConfigParser, getopt
    config = ConfigParser.SafeConfigParser()
    config.read('eurostat.cfg')
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

    ddObj = DD(config)
    ddObj.recordVocabularies()

    zfd = zipfile.ZipFile("all_dic.zip")
    if len(args) == 0:
        for zi in zfd.infolist():
            name = zi.filename
            modifyDate = "%04d-%02d-%02d %02d:%02d:%02d" % zi.date_time
            if name[-1] == "/": continue   # Found a folder
            if name == "en/dimlst.dic": continue   # (List of dimensions)
            if name == "en/table_dic.dic": continue   # (List of datasets)
            if name[:3] == "en/":
                code = name[3:-4]
                logging.debug("Building %s", code)
                winfile = StringIO(zfd.read(name))
                tsvfile = codecs.EncodedFile(winfile, "utf-8", "cp1252")
                ddObj.createVoc(code, modifyDate)
                ddObj.addConcepts(code, tsvfile, config, modifyDate)
                winfile.close()
    else:
        for code in args:
            logging.debug("Building %s", code)
            zi = zfd.getinfo("en/%s.dic" % code)
            modifyDate = "%04d-%02d-%02d %02d:%02d:%02d" % zi.date_time
            winfile = StringIO(zfd.read("en/%s.dic" % code))
            tsvfile = codecs.EncodedFile(winfile, "utf-8", "cp1252")
            ddObj.createVoc(code, modifyDate)
            ddObj.addConcepts(code, tsvfile, config, modifyDate)
            winfile.close()
    zfd.close()
    
